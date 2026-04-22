from pydantic import BaseModel
from typing import List, Optional

class MensajeHistorial(BaseModel):
    rol: str  # "user" o "model"
    contenido: str

class ConsultaAsistenteSchema(BaseModel):
    mensaje: str
    historial: Optional[List[MensajeHistorial]] = []

class RespuestaAsistenteSchema(BaseModel):
    respuesta: str

class GenerarTemplateSchema(BaseModel):
    descripcion: str