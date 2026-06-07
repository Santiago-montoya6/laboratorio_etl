import requests
from datetime import datetime
from app.database import mongo_collection

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon"
FUENTE       = "PokéAPI"

def extraer_pokemon(cantidad: int) -> dict:
    """
    Extrae 'cantidad' pokémon de la PokéAPI y los guarda en MongoDB.
    Es idempotente: usa upsert por _id para no duplicar.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    # 1. Obtener la lista de pokémon (paginación con limit/offset)
    lista_url = f"{POKEAPI_BASE}?limit={cantidad}&offset=0"
    lista_resp = requests.get(lista_url, timeout=10)
    lista_resp.raise_for_status()
    lista = lista_resp.json().get("results", [])

    guardados = 0

    for item in lista:
        # 2. Llamar al endpoint individual de cada pokémon
        detalle_resp = requests.get(item["url"], timeout=10)
        if detalle_resp.status_code != 200:
            continue

        data = detalle_resp.json()

        # 3. Construir el documento crudo
        documento = {
            "_id": data["id"],          # PK natural = ID de la API
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

        # 4. Upsert — si ya existe no duplica, si no existe lo crea
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