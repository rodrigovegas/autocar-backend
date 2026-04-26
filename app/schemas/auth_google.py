from pydantic import BaseModel
from typing import Optional


class GoogleLoginSchema(BaseModel):
    id_token: str


class GoogleRegistroUsuarioSchema(BaseModel):
    id_token: str
    # Nombre opcional: el frontend lo envía solo si Google devuelve displayName vacío
    nombre: Optional[str] = None


class GoogleRegistroTallerSchema(BaseModel):
    id_token: str
    nombre: str           # Nombre del taller (no del propietario)
    especialidad: str     # Nombre de la especialidad
    direccion_texto: str
    telefono: str
