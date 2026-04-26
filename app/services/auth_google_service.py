from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.auth_repository import AuthRepository
from app.models.especialidad import Especialidad
from app.models.administrador import Administrador
from app.core.security import verificar_token_firebase

auth_repo = AuthRepository()


class AuthGoogleService:
    """Lógica de negocio para el flujo de autenticación con Google.

    Todos los endpoints de este servicio reciben un Firebase ID Token
    obtenido por el cliente tras completar el flujo OAuth de Google.
    El backend no crea usuarios en Firebase — eso ya lo hizo el SDK del cliente.
    Solo verifica el token y gestiona los registros en la base de datos propia.
    """

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _extraer_datos_token(self, id_token: str) -> dict:
        """Verifica el token de Firebase y retorna los datos decodificados.

        Campos retornados: uid, email, nombre.
        Lanza HTTPException si el token es inválido o el correo no está verificado.
        Los tokens de Google siempre tienen email_verified=True, pero lo validamos
        explícitamente como salvaguarda.
        """
        try:
            decoded = verificar_token_firebase(id_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token de autenticación inválido o expirado.",
                },
            )

        if not decoded.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "EMAIL_NOT_VERIFIED",
                    "message": (
                        "Tu correo de Google no está verificado. "
                        "Verifícalo y vuelve a intentar."
                    ),
                },
            )

        return {
            "uid": decoded["uid"],
            "email": decoded.get("email", ""),
            "nombre": (decoded.get("name") or "").strip(),
        }

    def _rechazar_si_es_admin(self, db: Session, firebase_uid: str, email: str) -> None:
        """Lanza HTTPException si el uid o el correo pertenecen a un administrador.

        Los administradores solo pueden acceder con correo + contraseña tradicional.
        Se verifica por UID y por correo para cubrir el caso en que Firebase
        permita múltiples cuentas por email.
        """
        by_uid = (
            db.query(Administrador)
            .filter(Administrador.firebase_uid == firebase_uid)
            .first()
        )
        by_email = (
            db.query(Administrador)
            .filter(Administrador.correo == email)
            .first()
        )
        if by_uid or by_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ADMIN_NOT_ALLOWED",
                    "message": (
                        "El acceso administrativo solo está disponible "
                        "con correo y contraseña."
                    ),
                },
            )

    # ── Endpoints de negocio ──────────────────────────────────────────────────

    def login(self, db: Session, id_token: str) -> dict:
        """Inicia sesión con una cuenta de Google ya registrada en el sistema.

        Flujo:
        1. Verifica el token → extrae uid, email.
        2. Rechaza administradores.
        3. Busca por firebase_uid → si existe devuelve LoginResponse.
        4. Si no existe por uid pero sí por correo → EMAIL_EXISTS (cuenta tradicional).
        5. Si no existe en absoluto → NOT_REGISTERED.
        """
        datos = self._extraer_datos_token(id_token)
        firebase_uid = datos["uid"]
        email = datos["email"]

        self._rechazar_si_es_admin(db, firebase_uid, email)

        # Buscar como usuario registrado
        usuario = auth_repo.obtener_usuario_por_firebase_uid(db, firebase_uid)
        if usuario:
            if not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "CUENTA_DESACTIVADA",
                        "message": "Tu cuenta se encuentra desactivada.",
                    },
                )
            return {
                "token": id_token,
                "rol": "usuario",
                "id": str(usuario.id),
                "nombre": usuario.nombre_completo,
            }

        # Buscar como taller registrado
        taller = auth_repo.obtener_taller_por_firebase_uid(db, firebase_uid)
        if taller:
            if taller.estado == "pendiente":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "CUENTA_PENDIENTE",
                        "message": "Su cuenta está pendiente de verificación por el administrador.",
                    },
                )
            if taller.estado == "rechazado":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "CUENTA_RECHAZADA",
                        "message": "Su solicitud de registro no fue aprobada.",
                    },
                )
            if taller.estado == "inactivo":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "CUENTA_DESACTIVADA",
                        "message": "Su cuenta se encuentra desactivada.",
                    },
                )
            return {
                "token": id_token,
                "rol": "taller",
                "id": str(taller.id),
                "nombre": taller.nombre,
            }

        # No encontrado por UID — verificar si el correo ya pertenece a otra cuenta
        # (cuenta tradicional con correo+contraseña)
        if (
            auth_repo.obtener_usuario_por_correo(db, email)
            or auth_repo.obtener_taller_por_correo(db, email)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": (
                        "Ya existe una cuenta registrada con este correo. "
                        "Por favor inicia sesión con tu correo y contraseña, "
                        "o usa otro correo de Google."
                    ),
                },
            )

        # Correo tampoco existe → usuario no registrado en absoluto
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_REGISTERED",
                "message": "No tienes una cuenta registrada. ¿Deseas crear una?",
            },
        )

    def registrar_usuario(
        self,
        db: Session,
        id_token: str,
        nombre_override: Optional[str] = None,
    ) -> dict:
        """Registra un usuario nuevo con Google.

        El usuario ya está autenticado en Firebase (el SDK del cliente lo creó).
        Solo se crea el registro en la base de datos propia.

        Si Google no provee nombre (displayName vacío), el frontend puede enviar
        nombre_override con el nombre que el usuario ingresó manualmente.
        """
        datos = self._extraer_datos_token(id_token)
        firebase_uid = datos["uid"]
        email = datos["email"]
        nombre = (nombre_override or datos["nombre"] or "").strip()

        self._rechazar_si_es_admin(db, firebase_uid, email)

        if not nombre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NOMBRE_REQUERIDO",
                    "message": (
                        "Tu perfil de Google no tiene nombre. "
                        "Por favor ingresa tu nombre completo."
                    ),
                },
            )

        # Verificar que no esté ya registrado
        if auth_repo.obtener_usuario_por_firebase_uid(db, firebase_uid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ALREADY_REGISTERED",
                    "message": "Ya tienes una cuenta de usuario registrada.",
                },
            )
        if auth_repo.obtener_usuario_por_correo(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "Ya existe una cuenta registrada con este correo.",
                },
            )
        if auth_repo.obtener_taller_por_correo(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "Ya existe una cuenta de taller con este correo.",
                },
            )

        # Crear en la base de datos (Firebase ya tiene al usuario, no lo creamos aquí)
        usuario = auth_repo.crear_usuario(
            db, firebase_uid, nombre, email, auth_method="google"
        )

        return {
            "token": id_token,
            "rol": "usuario",
            "id": str(usuario.id),
            "nombre": usuario.nombre_completo,
        }

    def registrar_taller(
        self,
        db: Session,
        id_token: str,
        nombre: str,
        especialidad: str,
        direccion_texto: str,
        telefono: str,
    ) -> dict:
        """Registra un taller nuevo con Google + datos adicionales del formulario.

        El taller queda en estado 'pendiente' hasta que el admin lo apruebe,
        igual que el flujo de registro tradicional.
        """
        datos = self._extraer_datos_token(id_token)
        firebase_uid = datos["uid"]
        email = datos["email"]

        self._rechazar_si_es_admin(db, firebase_uid, email)

        # Verificar que no esté ya registrado
        if auth_repo.obtener_taller_por_firebase_uid(db, firebase_uid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ALREADY_REGISTERED",
                    "message": "Ya tienes una cuenta de taller registrada.",
                },
            )
        if auth_repo.obtener_taller_por_correo(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "Ya existe una cuenta de taller con este correo.",
                },
            )
        if auth_repo.obtener_usuario_por_correo(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "Ya existe una cuenta de usuario con este correo.",
                },
            )

        # Resolver la especialidad por nombre → obtener su UUID
        especialidad_obj = (
            db.query(Especialidad)
            .filter(Especialidad.nombre == especialidad, Especialidad.activo == True)
            .first()
        )
        if not especialidad_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ESPECIALIDAD_INVALIDA",
                    "message": "La especialidad seleccionada no existe o no está activa.",
                },
            )

        # Crear en la base de datos — estado "pendiente" por defecto
        taller = auth_repo.crear_taller(
            db,
            firebase_uid,
            nombre,
            especialidad_obj.id,
            direccion_texto,
            telefono,
            email,
            auth_method="google",
        )

        return {
            "id": str(taller.id),
            "nombre": taller.nombre,
            "correo": taller.correo,
            "estado": taller.estado,
        }
