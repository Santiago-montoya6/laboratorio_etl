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
        
        