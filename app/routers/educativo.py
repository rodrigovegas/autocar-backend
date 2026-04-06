from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.services.educativo_service import EducativoService
from app.schemas.educativo import ContenidoCreateSchema, ContenidoResponse
from app.models.usuario import Usuario
from app.models.taller import Taller

router = APIRouter(prefix="/educativo", tags=["Educativo"])


@router.get("/", response_model=List[ContenidoResponse])
def listar_contenidos_publicados(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos los contenidos educativos publicados para el usuario."""
    service = EducativoService(db)
    return service.listar_publicados()


@router.post("/", response_model=ContenidoResponse, status_code=201)
def publicar_contenido(
    datos: ContenidoCreateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """El taller publica un nuevo contenido educativo."""
    service = EducativoService(db)
    return service.publicar_contenido(str(current_taller.id), datos)


@router.get("/taller", response_model=List[ContenidoResponse])
def listar_contenidos_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Lista los contenidos publicados por el taller autenticado."""
    service = EducativoService(db)
    return service.listar_por_taller(str(current_taller.id))


@router.get("/pendientes", response_model=List[ContenidoResponse])
def listar_pendientes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista contenidos pendientes de revisión — solo para administrador."""
    service = EducativoService(db)
    return service.listar_pendientes()


@router.patch("/{contenido_id}/aprobar", response_model=ContenidoResponse)
def aprobar_contenido(
    contenido_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aprueba un contenido educativo pendiente."""
    service = EducativoService(db)
    return service.aprobar(contenido_id, str(current_user.id))


@router.patch("/{contenido_id}/rechazar", response_model=ContenidoResponse)
def rechazar_contenido(
    contenido_id: str,
    motivo: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rechaza un contenido educativo pendiente."""
    service = EducativoService(db)
    return service.rechazar(contenido_id, motivo)