from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    RegistroUsuarioSchema,
    RegistroTallerSchema,
    LoginSchema,
    LoginResponse,
    UsuarioResponse,
    TallerResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])
auth_service = AuthService()

@router.post("/registro/usuario", response_model=UsuarioResponse, status_code=201)
def registrar_usuario(datos: RegistroUsuarioSchema, db: Session = Depends(get_db)):
    try:
        usuario = auth_service.registrar_usuario(
            db,
            datos.nombre_completo,
            datos.correo,
            datos.contrasena
        )
        return UsuarioResponse(
            id=str(usuario.id),
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/registro/taller", response_model=TallerResponse, status_code=201)
def registrar_taller(datos: RegistroTallerSchema, db: Session = Depends(get_db)):
    try:
        taller = auth_service.registrar_taller(
            db,
            datos.nombre,
            datos.especialidad,
            datos.direccion_texto,
            datos.telefono,
            datos.correo,
            datos.contrasena
        )
        return TallerResponse(
            id=str(taller.id),
            nombre=taller.nombre,
            correo=taller.correo,
            estado=taller.estado
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse)
def login(datos: LoginSchema, db: Session = Depends(get_db)):
    try:
        resultado = auth_service.login(db, datos.correo, datos.contrasena)
        return LoginResponse(**resultado)
    except ValueError as e:
        if "CUENTA_PENDIENTE" in str(e):
            raise HTTPException(
                status_code=403,
                detail="Su cuenta está pendiente de verificación por el administrador"
            )
        raise HTTPException(status_code=400, detail=str(e))
    