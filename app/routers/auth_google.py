import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginResponse, TallerResponse
from app.schemas.auth_google import (
    GoogleLoginSchema,
    GoogleRegistroUsuarioSchema,
    GoogleRegistroTallerSchema,
)
from app.services.auth_google_service import AuthGoogleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["Autenticación Google"])
google_service = AuthGoogleService()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con Google",
    description=(
        "Autentica un usuario o taller ya registrado usando un Firebase ID Token "
        "obtenido tras el flujo OAuth de Google. "
        "No crea cuentas nuevas — solo autentica las existentes.\n\n"
        "**Códigos de error posibles:**\n"
        "- `INVALID_TOKEN` (401): Token inválido o expirado.\n"
        "- `EMAIL_NOT_VERIFIED` (400): El correo de Google no está verificado.\n"
        "- `ADMIN_NOT_ALLOWED` (403): Los administradores no pueden usar Google.\n"
        "- `CUENTA_DESACTIVADA` (403): Cuenta desactivada.\n"
        "- `CUENTA_PENDIENTE` (403): Taller pendiente de aprobación.\n"
        "- `CUENTA_RECHAZADA` (403): Solicitud de taller rechazada.\n"
        "- `EMAIL_EXISTS` (409): El correo pertenece a una cuenta tradicional.\n"
        "- `NOT_REGISTERED` (404): No existe cuenta con este correo/UID."
    ),
    responses={
        200: {"description": "Login exitoso — devuelve token y rol."},
        400: {"description": "Email no verificado."},
        401: {"description": "Token inválido."},
        403: {"description": "Acceso denegado (admin / cuenta inactiva / pendiente)."},
        404: {"description": "Cuenta no registrada."},
        409: {"description": "Email ya existe en cuenta tradicional."},
        500: {"description": "Error interno del servidor."},
    },
)
def login_google(datos: GoogleLoginSchema, db: Session = Depends(get_db)):
    try:
        resultado = google_service.login(db, datos.id_token)
        return LoginResponse(**resultado)
    except Exception as exc:
        # HTTPException proviene del servicio — la dejamos pasar sin tocar
        from fastapi import HTTPException
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Error inesperado en /auth/google/login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Error interno del servidor."},
        )


@router.post(
    "/registro/usuario",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario con Google",
    description=(
        "Crea un registro de usuario en la base de datos a partir de un Firebase ID Token "
        "de Google. Firebase ya creó al usuario client-side; este endpoint solo persiste "
        "el registro en la BD propia.\n\n"
        "Si Google no provee `displayName`, el frontend debe enviar `nombre` con el valor "
        "ingresado manualmente por el usuario.\n\n"
        "**Códigos de error posibles:**\n"
        "- `INVALID_TOKEN` (401): Token inválido o expirado.\n"
        "- `EMAIL_NOT_VERIFIED` (400): El correo de Google no está verificado.\n"
        "- `ADMIN_NOT_ALLOWED` (403): Los administradores no pueden usar Google.\n"
        "- `NOMBRE_REQUERIDO` (400): Google no provee nombre y el frontend tampoco lo envió.\n"
        "- `ALREADY_REGISTERED` (400): Este UID de Google ya tiene cuenta de usuario.\n"
        "- `EMAIL_EXISTS` (409): El correo ya existe en otra cuenta."
    ),
    responses={
        201: {"description": "Registro exitoso — devuelve token y rol."},
        400: {"description": "Datos inválidos (email no verificado / nombre faltante / ya registrado)."},
        401: {"description": "Token inválido."},
        403: {"description": "Acceso denegado (admin)."},
        409: {"description": "Email ya registrado en otra cuenta."},
        500: {"description": "Error interno del servidor."},
    },
)
def registrar_usuario_google(
    datos: GoogleRegistroUsuarioSchema, db: Session = Depends(get_db)
):
    try:
        resultado = google_service.registrar_usuario(db, datos.id_token, datos.nombre)
        return LoginResponse(**resultado)
    except Exception as exc:
        from fastapi import HTTPException
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Error inesperado en /auth/google/registro/usuario")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Error interno del servidor."},
        )


@router.post(
    "/registro/taller",
    response_model=TallerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar taller con Google",
    description=(
        "Crea un registro de taller en la base de datos usando un Firebase ID Token de Google "
        "más los datos del formulario (nombre, especialidad, dirección, teléfono). "
        "El taller queda en estado **`pendiente`** hasta que el administrador lo apruebe, "
        "igual que en el registro tradicional.\n\n"
        "**Códigos de error posibles:**\n"
        "- `INVALID_TOKEN` (401): Token inválido o expirado.\n"
        "- `EMAIL_NOT_VERIFIED` (400): El correo de Google no está verificado.\n"
        "- `ADMIN_NOT_ALLOWED` (403): Los administradores no pueden usar Google.\n"
        "- `ALREADY_REGISTERED` (400): Este UID de Google ya tiene cuenta de taller.\n"
        "- `EMAIL_EXISTS` (409): El correo ya existe en otra cuenta.\n"
        "- `ESPECIALIDAD_INVALIDA` (400): La especialidad no existe o está inactiva."
    ),
    responses={
        201: {"description": "Registro exitoso — taller en estado pendiente."},
        400: {"description": "Datos inválidos (especialidad inexistente / ya registrado / etc)."},
        401: {"description": "Token inválido."},
        403: {"description": "Acceso denegado (admin)."},
        409: {"description": "Email ya registrado en otra cuenta."},
        500: {"description": "Error interno del servidor."},
    },
)
def registrar_taller_google(
    datos: GoogleRegistroTallerSchema, db: Session = Depends(get_db)
):
    try:
        resultado = google_service.registrar_taller(
            db,
            datos.id_token,
            datos.nombre,
            datos.especialidad,
            datos.direccion_texto,
            datos.telefono,
        )
        return TallerResponse(**resultado)
    except Exception as exc:
        from fastapi import HTTPException
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Error inesperado en /auth/google/registro/taller")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Error interno del servidor."},
        )
