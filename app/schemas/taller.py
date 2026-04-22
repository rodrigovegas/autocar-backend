from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class TallerResumenResponse(BaseModel):
    id: str
    nombre: str
    especialidad_nombre: Optional[str] = None
    direccion_texto: str
    telefono: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    calificacion_promedio: Optional[float] = None
    total_calificaciones: Optional[int] = None

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
    especialidad_nombre: Optional[str] = None
    direccion_texto: str
    telefono: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    servicios: List[ServicioEnTallerResponse] = []
    calificacion_promedio: Optional[float] = None
    total_calificaciones: Optional[int] = None

    class Config:
        from_attributes = True


class TallerPerfilUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    direccion_texto: Optional[str] = None
    telefono: Optional[str] = None


class ProponerTipoSchema(BaseModel):
    nombre: str
    descripcion_base: str


class AgregarServicioSchema(BaseModel):
    tiempo_estimado_minutos: int = 60