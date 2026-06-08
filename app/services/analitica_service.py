from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.database import SessionLocal, mongo_collection
from app.models.personajes_sql import PokemonMaster
import pandas as pd


class AnaliticaService:
    """Servicio de analítica para consultas dinámicas sobre SQL y Mongo-SQL."""
    
    @staticmethod
    def get_column_info(column_name: str):
        """
        Obtiene información sobre una columna de la tabla PokemonMaster.
        Retorna: (existe, tipo_sqlalchemy, tipo_python)
        """
        try:
            inspector = inspect(PokemonMaster)
            columns = {col.name: col for col in inspector.columns}
            
            if column_name not in columns:
                return False, None, None
            
            col = columns[column_name]
            return True, col.type, type(col.type)
        except Exception as e:
            return False, None, None
    
    @staticmethod
    def _detectar_tipo(col_data, tipo_sql):
        """Detecta dinámicamente el tipo de la columna basado en SQLAlchemy Type."""
        tipo_str = str(tipo_sql).upper()
        
        if "BOOL" in tipo_str or "BIT" in tipo_str:
            return "booleana"
        elif "INT" in tipo_str or "FLOAT" in tipo_str or "DECIMAL" in tipo_str or "DOUBLE" in tipo_str:
            return "numerica"
        elif "DATE" in tipo_str or "DATETIME" in tipo_str or "TIME" in tipo_str:
            return "fecha"
        else:
            return "categorica"
    
    @staticmethod
    def get_valid_columns() -> list:
        """Retorna lista de columnas válidas de la tabla."""
        inspector = inspect(PokemonMaster)
        return [col.name for col in inspector.columns]
    
    @staticmethod
    def analizar_columna(column_name: str) -> dict:
        """
        Análisis dinámico de una columna según su tipo.
        Soporta: categórica, numérica, fecha, booleana.
        """
        existe, tipo_sql, tipo_python = AnaliticaService.get_column_info(column_name)
        
        if not existe:
            return {
                "error": f"Columna '{column_name}' no existe",
                "columnas_validas": AnaliticaService.get_valid_columns()
            }
        
        try:
            db = SessionLocal()
            # Obtener datos en DataFrame
            query = db.query(PokemonMaster).all()
            data = [
                {col.name: getattr(row, col.name) for col in inspect(PokemonMaster).columns}
                for row in query
            ]
            db.close()
            
            df = pd.DataFrame(data)
            
            if df.empty:
                return {"error": "No hay datos en la tabla"}
            
            # Detectar tipo dinámicamente
            col_data = df[column_name]
            tipo_detectado = AnaliticaService._detectar_tipo(col_data, tipo_sql)
            
            # Análisis según tipo
            if tipo_detectado == "categorica":
                return AnaliticaService._analizar_categorica(column_name, col_data)
            elif tipo_detectado == "numerica":
                return AnaliticaService._analizar_numerica(column_name, col_data)
            elif tipo_detectado == "fecha":
                return AnaliticaService._analizar_fecha(column_name, col_data)
            elif tipo_detectado == "booleana":
                return AnaliticaService._analizar_booleana(column_name, col_data)
            else:
                return {"error": f"Tipo no soportado: {tipo_detectado}"}
        
        except Exception as e:
            return {"error": f"Error al analizar columna: {str(e)}"}
    
    @staticmethod
    def _analizar_categorica(column_name: str, col_data) -> dict:
        """Análisis para columnas categóricas (texto con valores repetidos)."""
        value_counts = col_data.value_counts().to_dict()
        return {
            "columna": column_name,
            "tipo": "categorica",
            "valores_unicos": col_data.nunique(),
            "distribucion": value_counts,
            "valor_mas_comun": col_data.mode()[0] if not col_data.mode().empty else None,
            "nulos": int(col_data.isna().sum())
        }
    
    @staticmethod
    def _analizar_numerica(column_name: str, col_data) -> dict:
        """Análisis para columnas numéricas (INT, FLOAT, DECIMAL)."""
        return {
            "columna": column_name,
            "tipo": "numerica",
            "min": float(col_data.min()) if not col_data.isna().all() else None,
            "max": float(col_data.max()) if not col_data.isna().all() else None,
            "promedio": float(col_data.mean()) if not col_data.isna().all() else None,
            "mediana": float(col_data.median()) if not col_data.isna().all() else None,
            "desviacion_std": float(col_data.std()) if not col_data.isna().all() else None,
            "nulos": int(col_data.isna().sum())
        }
    
    @staticmethod
    def _analizar_fecha(column_name: str, col_data) -> dict:
        """Análisis para columnas de fecha (DATE, DATETIME)."""
        col_data = pd.to_datetime(col_data, errors='coerce')
        return {
            "columna": column_name,
            "tipo": "fecha",
            "min": str(col_data.min().date()) if not col_data.isna().all() else None,
            "max": str(col_data.max().date()) if not col_data.isna().all() else None,
            "rango_dias": int((col_data.max() - col_data.min()).days) if not col_data.isna().all() else None,
            "nulos": int(col_data.isna().sum())
        }
    
    @staticmethod
    def _analizar_booleana(column_name: str, col_data) -> dict:
        """Análisis para columnas booleanas (BOOLEAN, BIT)."""
        return {
            "columna": column_name,
            "tipo": "booleana",
            "true": int((col_data == True).sum()),
            "false": int((col_data == False).sum()),
            "nulos": int(col_data.isna().sum())
        }
    
    @staticmethod
    def obtener_perfil_dual(pokemon_id: int) -> dict:
        """
        Retorna el mismo registro visto desde Mongo y MySQL.
        Valida alineación de PKs y maneja 3 casos.
        """
        db = SessionLocal()
        try:
            # Consulta Mongo
            vista_mongo = mongo_collection.find_one({"_id": pokemon_id})
            
            # Consulta MySQL
            vista_sql = db.query(PokemonMaster).filter(PokemonMaster.id_pokemon == pokemon_id).first()
            
            # Convertir SQL a dict
            vista_sql_dict = None
            if vista_sql:
                vista_sql_dict = {
                    col.name: getattr(vista_sql, col.name)
                    for col in inspect(PokemonMaster).columns
                }
            
            # Caso 1: En ambas bases
            if vista_mongo and vista_sql:
                return {
                    "id": pokemon_id,
                    "vista_mongo": {k: v for k, v in vista_mongo.items() if k != "_id"},
                    "vista_sql": vista_sql_dict
                }
            # Caso 2: Solo en Mongo
            elif vista_mongo and not vista_sql:
                return {
                    "id": pokemon_id,
                    "vista_mongo": {k: v for k, v in vista_mongo.items() if k != "_id"},
                    "vista_sql": None,
                    "warning": "Registro existe en Mongo pero no en MySQL. Posiblemente no se ejecutó /transformar o falló."
                }
            # Caso 3: Solo en SQL
            elif not vista_mongo and vista_sql:
                return {
                    "id": pokemon_id,
                    "vista_mongo": None,
                    "vista_sql": vista_sql_dict,
                    "warning": "Registro existe en MySQL pero no en Mongo. Posiblemente fue eliminado."
                }
            # Caso 4: En ninguna
            else:
                return {"error": "Registro no existe en ninguna base de datos", "id": pokemon_id}
        
        except Exception as e:
            return {"error": f"Error al obtener perfil dual: {str(e)}"}
        finally:
            db.close()

