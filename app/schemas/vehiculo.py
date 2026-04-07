from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehiculoCreateSchema(BaseModel):
    marca: str
    modelo: str
    anio: int
    kilometraje_actual: int
    placa: Optional[str] = None
    color: Optional[str] = None
    tipo_combustible: Optional[str] = None

class VehiculoUpdateSchema(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje_actual: Optional[int] = None
    placa: Optional[str] = None
    color: Optional[str] = None
    tipo_combustible: Optional[str] = None

class VehiculoResponse(BaseModel):
    id: str
    marca: str
    modelo: str
    anio: int
    kilometraje_actual: int
    placa: Optional[str]
    color: Optional[str]
    tipo_combustible: Optional[str]
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True