from fastapi import FastAPI
from app.database import Base, engine
from app.controllers import etl_controller, analitica_controller

# Crear tablas si no existen (resiliencia)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pipeline ETL Pokémon",
    description="Laboratorio Final — Bases de Datos para Ciencia de Datos",
    version="1.0.0"
)

app.include_router(etl_controller.router)
app.include_router(analitica_controller.router)

@app.get("/")
def root():
    return {"mensaje": "API ETL Pokémon activa ✅"}