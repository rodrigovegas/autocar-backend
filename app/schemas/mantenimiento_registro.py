from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class MantenimientoRegistroCreate(BaseModel):
    reserva_id: str
    kilometraje_registro: int
    fecha_realizado: date
    costo: Optional[float] = None
    detalle_tecnico: Optional[str] = None
    problemas_detectados: Optional[str] = None
    gravedad_problemas: Optional[str] = None
    km_proximo_mantenimiento: Optional[int] = None
    fecha_proximo_mantenimiento: Optional[date] = None
    recomendaciones: Optional[str] = None

class MantenimientoRegistroResponse(BaseModel):
    id: UUID
    reserva_id: UUID
    vehiculo_id: UUID
    taller_id: UUID
    kilometraje_registro: int
    fecha_realizado: date
    costo: Optional[float]
    detalle_tecnico: Optional[str]
    problemas_detectados: Optional[str]
    gravedad_problemas: Optional[str]
    km_proximo_mantenimiento: Optional[int]
    fecha_proximo_mantenimiento: Optional[date]
    recomendaciones: Optional[str]
    observaciones: Optional[str]

    class Config:
        from_attributes = True

class MantenimientoHistorialResponse(BaseModel):
    id: UUID
    vehiculo_id: UUID
    taller_id: UUID
    kilometraje_registro: int
    fecha_realizado: date
    costo: Optional[float]
    detalle_tecnico: Optional[str]
    problemas_detectados: Optional[str]
    gravedad_problemas: Optional[str]
    km_proximo_mantenimiento: Optional[int]
    fecha_proximo_mantenimiento: Optional[date]
    recomendaciones: Optional[str]
    observaciones: Optional[str]
    fecha_registro: Optional[datetime]

    class Config:
        from_attributes = True