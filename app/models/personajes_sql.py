from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

class PokemonMaster(Base):
    __tablename__ = "pokemon_master"

    # PK alineada con _id de MongoDB (NO autoincremental)
    id_pokemon       = Column(Integer, primary_key=True, autoincrement=False)
    nombre           = Column(String(100), nullable=False)
    altura           = Column(Integer, nullable=True)        # en decímetros
    peso             = Column(Integer, nullable=True)        # en hectogramos
    experiencia_base = Column(Integer, nullable=True)
    tipo_primario    = Column(String(50), nullable=True)
    tipo_secundario  = Column(String(50), nullable=True)
    habilidad_principal = Column(String(100), nullable=True)
    es_legendario    = Column(Boolean, nullable=True)        # derivado de species
    total_movimientos = Column(Integer, nullable=True)       # len(moves[])
    sprite_url       = Column(String(255), nullable=True)
    fecha_agregado = Column(DateTime, nullable=True)