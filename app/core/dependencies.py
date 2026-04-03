from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verificar_token_firebase
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.administrador import Administrador

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtiene el usuario autenticado desde el token JWT."""
    try:
        token = credentials.credentials
        decoded = verificar_token_firebase(token)
        firebase_uid = decoded["uid"]

        usuario = db.query(Usuario).filter(
            Usuario.firebase_uid == firebase_uid,
            Usuario.activo == True
        ).first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        return usuario
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def get_current_taller(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtiene el taller autenticado desde el token JWT."""
    try:
        token = credentials.credentials
        decoded = verificar_token_firebase(token)
        firebase_uid = decoded["uid"]

        taller = db.query(Taller).filter(
            Taller.firebase_uid == firebase_uid,
            Taller.estado == "activo"
        ).first()

        if not taller:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Taller no encontrado o no activo"
            )
        return taller
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtiene el administrador autenticado desde el token JWT."""
    try:
        token = credentials.credentials
        decoded = verificar_token_firebase(token)
        firebase_uid = decoded["uid"]

        admin = db.query(Administrador).filter(
            Administrador.firebase_uid == firebase_uid
        ).first()

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos de administrador"
            )
        return admin
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )