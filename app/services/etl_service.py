import requests
import pandas as pd
from datetime import datetime
from app.database import mongo_collection, SessionLocal, engine
from app.models.personajes_sql import PokemonMaster, Base
from sqlalchemy import text

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon"
FUENTE       = "PokéAPI"

def extraer_pokemon(cantidad: int) -> dict:
    """
    Extrae 'cantidad' pokémon de la PokéAPI y los guarda en MongoDB.
    Es idempotente: usa upsert por _id para no duplicar.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    lista_url = f"{POKEAPI_BASE}?limit={cantidad}&offset=0"
    lista_resp = requests.get(lista_url, timeout=10)
    lista_resp.raise_for_status()
    lista = lista_resp.json().get("results", [])

    guardados = 0

    for item in lista:
        detalle_resp = requests.get(item["url"], timeout=10)
        if detalle_resp.status_code != 200:
            continue

        data = detalle_resp.json()

        documento = {
            "_id": data["id"],
            "nombre": data["name"],
            "altura": data.get("height"),
            "peso": data.get("weight"),
            "experiencia_base": data.get("base_experience"),
            "tipos": [t["type"]["name"] for t in data.get("types", [])],
            "habilidades": [a["ability"]["name"] for a in data.get("abilities", [])],
            "movimientos": [m["move"]["name"] for m in data.get("moves", [])],
            "sprites": data.get("sprites", {}),
            "stats": data.get("stats", []),
            "fecha_ingesta": datetime.utcnow().isoformat()
        }

        mongo_collection.update_one(
            {"_id": documento["_id"]},
            {"$set": documento},
            upsert=True
        )
        guardados += 1

    return {
        "mensaje": "Datos extraídos exitosamente",
        "registros_guardados": guardados,
        "fuente": FUENTE,
        "status": 201
    }


def transformar_y_cargar() -> dict:
    """
    Lee datos crudos de MongoDB, los transforma con Pandas
    y los carga en MySQL con idempotencia.
    """
    # 1. Leer datos crudos de MongoDB
    documentos = list(mongo_collection.find({}, {"_id": 1, "nombre": 1, "altura": 1, "peso": 1, "experiencia_base": 1, "tipos": 1, "habilidades": 1, "movimientos": 1, "sprites": 1}))
    if not documentos:
        raise ValueError("No hay datos en MongoDB. Ejecute primero el endpoint /extraer.")

    # 2. Transformar con Pandas
    # Se aplanan los campos anidados (tipos, habilidades, sprites)
    # y se calculan campos derivados (total_movimientos, es_legendario)
    df = pd.DataFrame(documentos)

    df["tipo_primario"] = df["tipos"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "N/A"
    )
    df["tipo_secundario"] = df["tipos"].apply(
        lambda x: x[1] if isinstance(x, list) and len(x) > 1 else "N/A"
    )
    df["habilidad_principal"] = df["habilidades"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "N/A"
    )
    df["total_movimientos"] = df["movimientos"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df["sprite_url"] = df["sprites"].apply(
        lambda x: x.get("front_default", "N/A") if isinstance(x, dict) else "N/A"
    )
    df["altura"] = df["altura"].fillna(0).astype(int)
    df["peso"] = df["peso"].fillna(0).astype(int)
    df["experiencia_base"] = df["experiencia_base"].fillna(0).astype(int)
    df["es_legendario"] = False
    df["fecha_agregado"] = datetime.utcnow() 

    # 3. Crear tabla si no existe
    Base.metadata.create_all(bind=engine)

    # 4. Cargar en MySQL con idempotencia
    db = SessionLocal()
    procesados = 0
    try:
        for _, row in df.iterrows():
            existente = db.query(PokemonMaster).filter(
                PokemonMaster.id_pokemon == int(row["_id"])
            ).first()

            if existente:
                existente.nombre = row["nombre"]
                existente.altura = int(row["altura"])
                existente.peso = int(row["peso"])
                existente.experiencia_base = int(row["experiencia_base"])
                existente.tipo_primario = row["tipo_primario"]
                existente.tipo_secundario = row["tipo_secundario"]
                existente.habilidad_principal = row["habilidad_principal"]
                existente.es_legendario = bool(row["es_legendario"])
                existente.total_movimientos = int(row["total_movimientos"])
                existente.sprite_url = row["sprite_url"]
                existente.fecha_agregado = row["fecha_agregado"]
            else:
                pokemon = PokemonMaster(
                    id_pokemon=int(row["_id"]),
                    nombre=row["nombre"],
                    altura=int(row["altura"]),
                    peso=int(row["peso"]),
                    experiencia_base=int(row["experiencia_base"]),
                    tipo_primario=row["tipo_primario"],
                    tipo_secundario=row["tipo_secundario"],
                    habilidad_principal=row["habilidad_principal"],
                    es_legendario=bool(row["es_legendario"]),
                    total_movimientos=int(row["total_movimientos"]),
                    sprite_url=row["sprite_url"],
                    fecha_agregado=row["fecha_agregado"]
                )
                db.add(pokemon)

            procesados += 1

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    return {
        "mensaje": "Pipeline finalizado",
        "registros_procesados": procesados,
        "tabla_destino": "pokemon_master",
        "status": 200
    }


def reset_pipeline() -> dict:
    """
    Limpia MongoDB y hace TRUNCATE en MySQL.
    """
    print(f"[RESET] Iniciando limpieza - {datetime.utcnow()}")

    # 1. Limpiar MongoDB
    resultado_mongo = mongo_collection.delete_many({})
    mongo_docs_eliminados = resultado_mongo.deleted_count

    # 2. TRUNCATE en MySQL
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE pokemon_master"))
        db.commit()
        mysql_rows_eliminadas = mongo_docs_eliminados
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    print(f"[RESET] Completado - Mongo: {mongo_docs_eliminados}, MySQL: {mysql_rows_eliminadas}")

    return {
        "mensaje": "Sistema reseteado correctamente",
        "mongo_docs_eliminados": mongo_docs_eliminados,
        "mysql_rows_eliminadas": mysql_rows_eliminadas,
        "status": 200
    }
