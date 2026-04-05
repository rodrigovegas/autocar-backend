from pydantic import BaseModel
from datetime import date
from typing import Optional

class MantenimientoCreate(BaseModel):
    vehiculo_id: int
    tipo_mantenimiento_id: int
    fecha: date
    kilometraje: Optional[int] = None
    costo: Optional[float] = None
    descripcion: Optional[str] = None
    taller_nombre: Optional[str] = None

class MantenimientoResponse(BaseModel):
    id: int
    vehiculo_id: int
    tipo_mantenimiento_id: int
    fecha: date
    kilometraje: Optional[int]
    costo: Optional[float]
    descripcion: Optional[str]
    taller_nombre: Optional[str]

    class Config:
        from_attributes = True

class TipoMantenimientoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    intervalo_km: Optional[int]
    intervalo_dias: Optional[int]

    class Config:
        from_attributes = True