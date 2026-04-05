from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.mantenimiento_service import MantenimientoService
from app.schemas.mantenimiento import (
    MantenimientoCreate,
    MantenimientoResponse,
    TipoMantenimientoResponse,
)
from app.models.usuario import Usuario
from typing import List

router = APIRouter(prefix="/mantenimientos", tags=["Mantenimiento"])


@router.get("/tipos", response_model=List[TipoMantenimientoResponse])
def listar_tipos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = MantenimientoService(db)
    return service.listar_tipos()


@router.post("/", response_model=MantenimientoResponse)
def registrar_mantenimiento(
    datos: MantenimientoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = MantenimientoService(db)
    return service.registrar(datos, current_user.id)


@router.get("/vehiculo/{vehiculo_id}", response_model=List[MantenimientoResponse])
def listar_por_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = MantenimientoService(db)
    return service.listar_por_vehiculo(vehiculo_id, current_user.id)


@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = MantenimientoService(db)
    return service.eliminar(mantenimiento_id, current_user.id)