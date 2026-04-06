from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class MantenimientoCreate(BaseModel):
    vehiculo_id: str
    tipo_mantenimiento_id: UUID
    fecha: date
    kilometraje: Optional[int] = None
    costo: Optional[float] = None
    descripcion: Optional[str] = None
    taller_nombre: Optional[str] = None

class MantenimientoResponse(BaseModel):
    id: int
    vehiculo_id: str
    tipo_mantenimiento_id: UUID
    fecha: date
    kilometraje: Optional[int]
    costo: Optional[float]
    descripcion: Optional[str]
    taller_nombre: Optional[str]

    class Config:
        from_attributes = True

class TipoMantenimientoResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion_base: Optional[str]
    intervalo_km: Optional[int]
    intervalo_dias: Optional[int]

    class Config:
        from_attributes = True