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
    
@router.get("/perfil/{pokemon_id}", status_code=200)
def obtener_perfil_dual(pokemon_id: int):
    """
    Endpoint para obtener el mismo registro desde Mongo y MySQL.
    Valida alineación de PKs y detecta inconsistencias.
    Casos:
    - 200: En ambas bases o solo en una (con warning)
    - 404: No existe en ninguna
    """
    try:
        resultado = AnaliticaService.obtener_perfil_dual(pokemon_id)
        
        if "error" in resultado and "no existe" in resultado["error"]:
            raise HTTPException(status_code=404, detail=resultado["error"])
        
        return resultado
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
