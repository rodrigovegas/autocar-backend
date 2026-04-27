from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class VehiculoResumen(BaseModel):
    id: str
    marca: str
    modelo: str
    placa: Optional[str]


class TipoMantenimientoResumen(BaseModel):
    id: str
    nombre: str


class RecordatorioCreateSchema(BaseModel):
    vehiculo_id: str
    tipo_mantenimiento_id: str
    fecha_programada: Optional[date] = None
    kilometraje_programado: Optional[int] = None
    texto_personalizado: Optional[str] = None


class RecordatorioResponse(BaseModel):
    id: str
    vehiculo: VehiculoResumen
    tipo_mantenimiento: TipoMantenimientoResumen
    origen: str
    fecha_programada: Optional[date]
    kilometraje_programado: Optional[int]
    texto_personalizado: Optional[str]
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True
