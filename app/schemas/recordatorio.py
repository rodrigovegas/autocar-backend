from pydantic import BaseModel
from datetime import date
from typing import Optional

class RecordatorioCreate(BaseModel):
    vehiculo_id: int
    tipo_mantenimiento_id: int
    fecha_programada: date
    kilometraje_programado: Optional[int] = None
    notas: Optional[str] = None

class RecordatorioResponse(BaseModel):
    id: int
    vehiculo_id: int
    tipo_mantenimiento_id: int
    fecha_programada: date
    kilometraje_programado: Optional[int]
    notas: Optional[str]
    completado: bool

    class Config:
        from_attributes = True