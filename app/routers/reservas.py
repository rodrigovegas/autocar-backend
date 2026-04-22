from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.schemas.reserva import (
    ReservaCreateSchema,
    ReservaEstadoSchema,
    CalificarReservaSchema,
    ReservaResponse,
    ServicioReservaResponse
)
from app.services.reserva_service import ReservaService
from app.models.usuario import Usuario
from app.models.taller import Taller

router = APIRouter(prefix="/reservas", tags=["Reservas"])
reserva_service = ReservaService()

def _build_reserva_response(reserva) -> ReservaResponse:
    servicios = [ServicioReservaResponse(
        id=str(rs.servicio_taller_id),
        nombre=rs.servicio_taller.nombre_personalizado
              or rs.servicio_taller.tipo_mantenimiento.nombre
    ) for rs in reserva.servicios]

    return ReservaResponse(
        id=str(reserva.id),
        taller_nombre=reserva.taller.nombre,
        vehiculo=f"{reserva.vehiculo.marca} {reserva.vehiculo.modelo} {reserva.vehiculo.anio}",
        fecha=reserva.disponibilidad.fecha,
        hora_inicio=reserva.disponibilidad.hora_inicio,
        estado=reserva.estado,
        servicios=servicios,
        motivo_rechazo=reserva.motivo_rechazo,
        descripcion_otro=reserva.descripcion_otro,
        fecha_creacion=reserva.fecha_creacion,
        calificacion=reserva.calificacion,
        comentario_calificacion=reserva.comentario_calificacion,
    )

@router.post("", response_model=ReservaResponse, status_code=201)
def crear_reserva(
    datos: ReservaCreateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        reserva = reserva_service.crear_reserva(
            db,
            str(current_user.id),
            datos.taller_id,
            datos.vehiculo_id,
            datos.disponibilidad_id,
            datos.servicios_ids,
            datos.descripcion_otro
        )
        return _build_reserva_response(reserva)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/usuario", response_model=List[ReservaResponse])
def listar_reservas_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas las reservas del usuario autenticado."""
    reservas = reserva_service.obtener_reservas_usuario(
        db, str(current_user.id)
    )
    return [_build_reserva_response(r) for r in reservas]

@router.get("/taller", response_model=List[ReservaResponse])
def listar_reservas_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Lista todas las reservas recibidas por el taller autenticado."""
    reservas = reserva_service.obtener_reservas_taller(
        db, str(current_taller.id)
    )
    return [_build_reserva_response(r) for r in reservas]

@router.patch("/{reserva_id}/estado", response_model=ReservaResponse)
def actualizar_estado_reserva(
    reserva_id: str,
    datos: ReservaEstadoSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """El taller confirma o rechaza una reserva pendiente."""
    try:
        reserva = reserva_service.actualizar_estado_taller(
            db,
            reserva_id,
            str(current_taller.id),
            datos.estado,
            datos.motivo_rechazo
        )
        return _build_reserva_response(reserva)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{reserva_id}/calificar", response_model=ReservaResponse)
def calificar_reserva(
    reserva_id: str,
    datos: CalificarReservaSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """El usuario califica una reserva completada."""
    from app.models.reserva import Reserva as ReservaModel
    import uuid as _uuid
    reserva = db.query(ReservaModel).filter(
        ReservaModel.id == _uuid.UUID(reserva_id)
    ).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if str(reserva.usuario_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para calificar esta reserva")
    if reserva.estado != "completada":
        raise HTTPException(status_code=400, detail="Solo se pueden calificar reservas completadas")
    reserva.calificacion = datos.calificacion
    reserva.comentario_calificacion = datos.comentario
    db.commit()
    db.refresh(reserva)
    return _build_reserva_response(reserva)


@router.patch("/{reserva_id}/cancelar", response_model=ReservaResponse)
def cancelar_reserva(
    reserva_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """El usuario cancela una reserva en estado pendiente."""
    try:
        reserva = reserva_service.cancelar_reserva_usuario(
            db,
            reserva_id,
            str(current_user.id)
        )
        return _build_reserva_response(reserva)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))