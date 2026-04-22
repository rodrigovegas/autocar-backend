from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class TallerAdminResponse(BaseModel):
    id: UUID
    nombre: str
    especialidad_nombre: Optional[str] = None
    direccion_texto: str
    telefono: str
    correo: str
    estado: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    fecha_registro: datetime

    class Config:
        from_attributes = True


class ActivarTallerSchema(BaseModel):
    latitud: float
    longitud: float


class UsuarioAdminResponse(BaseModel):
    id: UUID
    nombre_completo: str
    correo: str
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True


class ContenidoAdminResponse(BaseModel):
    id: UUID
    taller_id: UUID
    titulo: str
    cuerpo: str
    categoria: str
    estado: str
    informe_ia: Optional[str] = None
    url_video: Optional[str] = None
    url_imagen: Optional[str] = None
    fecha_publicacion: datetime

    class Config:
        from_attributes = True


class RechazarContenidoSchema(BaseModel):
    motivo: str


class TipoMantenimientoAdminResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion_base: str
    estado: str

    class Config:
        from_attributes = True


class CrearTipoMantenimientoSchema(BaseModel):
    nombre: str
    descripcion_base: str