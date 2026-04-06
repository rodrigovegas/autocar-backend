from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ContenidoCreateSchema(BaseModel):
    titulo: str
    cuerpo: str
    categoria: str
    url_imagen: Optional[str] = None
    url_video: Optional[str] = None

class ContenidoResponse(BaseModel):
    id: UUID
    taller_id: UUID
    titulo: str
    cuerpo: str
    categoria: str
    url_imagen: Optional[str]
    url_video: Optional[str]
    estado: str
    informe_ia: Optional[str]
    motivo_rechazo: Optional[str]
    fecha_publicacion: datetime

    class Config:
        from_attributes = True