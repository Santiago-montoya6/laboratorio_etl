from pydantic import BaseModel, Field

class ExtraccionRequest(BaseModel):
    cantidad: int = Field(..., gt=0, description="Número de pokémon a extraer (mayor a 0)")

class ExtraccionResponse(BaseModel):
    mensaje: str
    registros_guardados: int
    fuente: str
    status: int

class TransformacionResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int

class ResetResponse(BaseModel):
    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminadas: int
    status: int