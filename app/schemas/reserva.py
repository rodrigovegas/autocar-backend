from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime

class ReservaCreateSchema(BaseModel):
    taller_id: str
    vehiculo_id: str
    disponibilidad_id: str
    servicios_ids: List[str]

class ReservaEstadoSchema(BaseModel):
    estado: str
    motivo_rechazo: Optional[str] = None

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
    fecha_creacion: datetime

    class Config:
        from_attributes = True