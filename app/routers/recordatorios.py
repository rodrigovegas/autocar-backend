from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.recordatorio import (
    RecordatorioCreateSchema,
    RecordatorioResponse,
    VehiculoResumen,
    TipoMantenimientoResumen,
)
from app.services.recordatorio_service import RecordatorioService
from app.models.usuario import Usuario

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])
recordatorio_service = RecordatorioService()


def _build_response(r) -> RecordatorioResponse:
    return RecordatorioResponse(
        id=str(r.id),
        vehiculo=VehiculoResumen(
            id=str(r.vehiculo.id),
            marca=r.vehiculo.marca,
            modelo=r.vehiculo.modelo,
            placa=r.vehiculo.placa,
        ),
        tipo_mantenimiento=TipoMantenimientoResumen(
            id=str(r.tipo_mantenimiento.id),
            nombre=r.tipo_mantenimiento.nombre,
        ),
        origen=r.origen,
        fecha_programada=r.fecha_programada,
        kilometraje_programado=r.kilometraje_programado,
        texto_personalizado=r.texto_personalizado,
        estado=r.estado,
        fecha_creacion=r.fecha_creacion,
    )


@router.get("", response_model=List[RecordatorioResponse])
def listar_recordatorios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recordatorios = recordatorio_service.listar_por_usuario(db, str(current_user.id))
    return [_build_response(r) for r in recordatorios]


@router.post("", response_model=RecordatorioResponse, status_code=201)
def crear_recordatorio(
    datos: RecordatorioCreateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        recordatorio = recordatorio_service.crear(
            db,
            str(current_user.id),
            datos.vehiculo_id,
            datos.tipo_mantenimiento_id,
            datos.fecha_programada,
            datos.kilometraje_programado,
            datos.texto_personalizado,
        )
        return _build_response(recordatorio)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{recordatorio_id}", status_code=204)
def eliminar_recordatorio(
    recordatorio_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        recordatorio_service.eliminar(db, recordatorio_id, str(current_user.id))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
