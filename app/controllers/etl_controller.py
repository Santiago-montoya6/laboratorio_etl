from fastapi import APIRouter, HTTPException
from app.views.schemas import ExtraccionRequest, ExtraccionResponse
from app.services import etl_service

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])

@router.post("/extraer", response_model=ExtraccionResponse, status_code=201)
def extraer(body: ExtraccionRequest):
    try:
        resultado = etl_service.extraer_pokemon(body.cantidad)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/transformar", status_code=200)
def transformar():
    try:
        resultado = etl_service.transformar_y_cargar()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.delete("/reset", status_code=200)
def reset():
    try:
        resultado = etl_service.reset_pipeline()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
