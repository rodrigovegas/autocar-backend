from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class DisponibilidadCreateSchema(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupos_totales: int

class DisponibilidadUpdateSchema(BaseModel):
    activo: bool

class DisponibilidadTallerResponse(BaseModel):
    id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupos_totales: int
    cupos_ocupados: int
    activo: bool

    class Config:
        from_attributes = True

class DisponibilidadUsuarioResponse(BaseModel):
    id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupos_disponibles: int

    class Config:
        from_attributes = True