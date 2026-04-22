from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime

class ReservaCreateSchema(BaseModel):
    taller_id: str
    vehiculo_id: str
    disponibilidad_id: str
    servicios_ids: List[str]
    descripcion_otro: Optional[str] = None

class ReservaEstadoSchema(BaseModel):
    estado: str
    motivo_rechazo: Optional[str] = None

class CalificarReservaSchema(BaseModel):
    calificacion: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None

class ServicioReservaResponse(BaseModel):
    id: str
    nombre: str

class ReservaResponse(BaseModel):
    id: str
    taller_nombre: str
    vehiculo: str
    fecha: date
    hora_inicio: time
    estado: str
    servicios: List[ServicioReservaResponse]
    motivo_rechazo: Optional[str] = None
    descripcion_otro: Optional[str] = None
    fecha_creacion: datetime
    calificacion: Optional[int] = None
    comentario_calificacion: Optional[str] = None

    class Config:
        from_attributes = True