from sqlalchemy.orm import Session
from app.repositories.auth_repository import AuthRepository
from app.models.especialidad import Especialidad
from app.core.security import (
    crear_usuario_firebase,
    verificar_token_firebase,
    obtener_token_firebase
)
from app.core.config import settings

auth_repo = AuthRepository()

class AuthService:

    def registrar_usuario(self, db: Session, nombre_completo: str,
                          correo: str, contrasena: str):
        # Verificar si el correo ya existe
        if auth_repo.obtener_usuario_por_correo(db, correo):
            raise ValueError("El correo ya está registrado")

        # Crear usuario en Firebase
        firebase_uid = crear_usuario_firebase(correo, contrasena)

        # Crear usuario en la base de datos
        usuario = auth_repo.crear_usuario(db, firebase_uid, nombre_completo, correo)
        return usuario

    def registrar_taller(self, db: Session, nombre: str, especialidad: str,
                         direccion_texto: str, telefono: str,
                         correo: str, contrasena: str):
        # Verificar si el correo ya existe
        if auth_repo.obtener_taller_por_correo(db, correo):
            raise ValueError("El correo ya está registrado")

        # Buscar la especialidad por nombre y obtener su UUID
        especialidad_obj = db.query(Especialidad).filter(
            Especialidad.nombre == especialidad,
            Especialidad.activo == True
        ).first()

        if not especialidad_obj:
            raise ValueError("La especialidad seleccionada no existe o no está activa")

        # Crear usuario en Firebase
        firebase_uid = crear_usuario_firebase(correo, contrasena)

        # Crear taller en la base de datos (pasando el UUID, no el nombre)
        taller = auth_repo.crear_taller(
            db, firebase_uid, nombre, especialidad_obj.id,
            direccion_texto, telefono, correo
        )
        return taller

    def login(self, db: Session, correo: str, contrasena: str):
        # Obtener token de Firebase
        token = obtener_token_firebase(correo, contrasena, settings.FIREBASE_API_KEY)

        # Verificar token y obtener firebase_uid
        decoded = verificar_token_firebase(token)
        firebase_uid = decoded["uid"]

        # Buscar en qué tabla está el actor
        usuario = auth_repo.obtener_usuario_por_firebase_uid(db, firebase_uid)
        if usuario:
            if not usuario.activo:
                raise ValueError("Cuenta desactivada")
            return {
                "token": token,
                "rol": "usuario",
                "id": str(usuario.id),
                "nombre": usuario.nombre_completo
            }

        taller = auth_repo.obtener_taller_por_firebase_uid(db, firebase_uid)
        if taller:
            if taller.estado == "pendiente":
                raise ValueError("CUENTA_PENDIENTE")
            if taller.estado == "rechazado":
                raise ValueError("Cuenta rechazada")
            if taller.estado == "inactivo":
                raise ValueError("Cuenta desactivada")
            return {
                "token": token,
                "rol": "taller",
                "id": str(taller.id),
                "nombre": taller.nombre
            }

        admin = auth_repo.obtener_admin_por_firebase_uid(db, firebase_uid)
        if admin:
            return {
                "token": token,
                "rol": "administrador",
                "id": str(admin.id),
                "nombre": admin.nombre_completo
            }

        raise ValueError("Usuario no encontrado en el sistema")