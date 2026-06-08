from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Analítica"])

@router.get("/analitica/columna/{nombre}", status_code=200)
def analizar_columna(nombre: str):
    """
    Endpoint para análisis dinámico de una columna.
    Detecta tipo automáticamente: categórica, numérica, fecha, booleana.
    """
    try:
        resultado = AnaliticaService.analizar_columna(nombre)
        
        if "error" in resultado:
            return {"error": resultado["error"], "columnas_validas": resultado.get("columnas_validas")}
        
        return resultado
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
