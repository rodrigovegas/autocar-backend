from pydantic import BaseModel
from typing import Optional

class MensajeHistorialSchema(BaseModel):
    rol: str
    contenido: str

class ConsultaAsistenteSchema(BaseModel):
    mensaje: str
    historial: list[MensajeHistorialSchema] = []
    vehiculo_id: Optional[str] = None

class RespuestaAsistenteSchema(BaseModel):
    respuesta: str

class GenerarTemplateSchema(BaseModel):
    descripcion: str
