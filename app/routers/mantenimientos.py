from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_taller, get_current_user
from app.schemas.mantenimiento_registro import (
    MantenimientoRegistroCreate,
    MantenimientoRegistroResponse,
    MantenimientoHistorialResponse,
)
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.services.taller_mantenimiento_service import TallerMantenimientoService

router = APIRouter(prefix="/mantenimientos", tags=["Mantenimiento"])
mantenimiento_service = TallerMantenimientoService()


@router.post("/", response_model=MantenimientoRegistroResponse, status_code=201)
def registrar_mantenimiento(
    datos: MantenimientoRegistroCreate,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    try:
        return mantenimiento_service.registrar_mantenimiento(db, datos, current_taller.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/historial/usuario", response_model=List[MantenimientoHistorialResponse])
def historial_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return mantenimiento_service.historial_usuario(db, current_user.id)


@router.get("/historial/taller", response_model=List[dict])
def historial_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    return mantenimiento_service.historial_taller(db, current_taller.id)
