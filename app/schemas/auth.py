from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class RegistroUsuarioSchema(BaseModel):
    nombre_completo: str
    correo: EmailStr
    contrasena: str

class RegistroTallerSchema(BaseModel):
    nombre: str
    especialidad: str
    direccion_texto: str
    telefono: str
    correo: EmailStr
    contrasena: str

class LoginSchema(BaseModel):
    correo: EmailStr
    contrasena: str

class LoginResponse(BaseModel):
    token: str
    rol: str
    id: str
    nombre: str

class UsuarioResponse(BaseModel):
    id: str
    nombre_completo: str
    correo: str

    class Config:
        from_attributes = True

class TallerResponse(BaseModel):
    id: str
    nombre: str
    correo: str
    estado: str