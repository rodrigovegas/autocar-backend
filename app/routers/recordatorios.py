from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.recordatorio_service import RecordatorioService
from app.schemas.recordatorio import RecordatorioCreate, RecordatorioResponse
from app.models.usuario import Usuario
from typing import List

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])


@router.post("/", response_model=RecordatorioResponse)
def crear_recordatorio(
    datos: RecordatorioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = RecordatorioService(db)
    return service.crear(datos, current_user.id)


@router.get("/vehiculo/{vehiculo_id}", response_model=List[RecordatorioResponse])
def listar_por_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = RecordatorioService(db)
    return service.listar_por_vehiculo(vehiculo_id, current_user.id)


@router.patch("/{recordatorio_id}/completar", response_model=RecordatorioResponse)
def marcar_completado(
    recordatorio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = RecordatorioService(db)
    return service.marcar_completado(recordatorio_id, current_user.id)


@router.delete("/{recordatorio_id}")
def eliminar_recordatorio(
    recordatorio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = RecordatorioService(db)
    return service.eliminar(recordatorio_id, current_user.id)