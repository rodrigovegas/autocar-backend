from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehiculoCreateSchema(BaseModel):
    marca: str
    modelo: str
    anio: int
    kilometraje_actual: int

class VehiculoUpdateSchema(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    kilometraje_actual: Optional[int] = None

class VehiculoResponse(BaseModel):
    id: str
    marca: str
    modelo: str
    anio: int
    kilometraje_actual: int
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True