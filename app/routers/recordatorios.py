from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_taller
from app.schemas.mantenimiento_registro import (
    MantenimientoRegistroCreate,
    MantenimientoRegistroResponse,
)
from app.models.mantenimiento import Mantenimiento
from app.models.reserva import Reserva
from app.models.taller import Taller
import uuid

router = APIRouter(prefix="/mantenimientos", tags=["Mantenimiento"])


@router.post("/", response_model=MantenimientoRegistroResponse, status_code=201)
def registrar_mantenimiento(
    datos: MantenimientoRegistroCreate,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    """El taller registra el mantenimiento al completar una reserva."""
    # Verificar que la reserva existe y pertenece al taller
    reserva = db.query(Reserva).filter(
        Reserva.id == uuid.UUID(datos.reserva_id),
        Reserva.taller_id == current_taller.id,
    ).first()

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != "confirmada":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden registrar mantenimientos de reservas confirmadas",
        )

    # Verificar que no tenga ya un mantenimiento
    existente = db.query(Mantenimiento).filter(
        Mantenimiento.reserva_id == uuid.UUID(datos.reserva_id)
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Esta reserva ya tiene un mantenimiento registrado",
        )

    # Crear el mantenimiento
    mantenimiento = Mantenimiento(
        reserva_id=uuid.UUID(datos.reserva_id),
        vehiculo_id=reserva.vehiculo_id,
        taller_id=current_taller.id,
        kilometraje_registro=datos.kilometraje_registro,
        fecha_realizado=datos.fecha_realizado,
        observaciones=datos.observaciones,
    )
    db.add(mantenimiento)

    # Marcar la reserva como completada
    reserva.estado = "completada"
    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento