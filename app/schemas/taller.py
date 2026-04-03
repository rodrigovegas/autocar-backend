from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal

class TallerResumenResponse(BaseModel):
    id: str
    nombre: str
    especialidad: str
    direccion_texto: str
    telefono: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None

    class Config:
        from_attributes = True

class ServicioEnTallerResponse(BaseModel):
    id: str
    nombre: str
    descripcion: str
    tiempo_estimado_minutos: int

class TallerDetalleResponse(BaseModel):
    id: str
    nombre: str
    especialidad: str
    direccion_texto: str
    telefono: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    servicios: List[ServicioEnTallerResponse] = []

    class Config:
        from_attributes = True

class TallerPerfilUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    especialidad: Optional[str] = None
    direccion_texto: Optional[str] = None
    telefono: Optional[str] = None