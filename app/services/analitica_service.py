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

