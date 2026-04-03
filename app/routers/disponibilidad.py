from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.schemas.disponibilidad import (
    DisponibilidadCreateSchema,
    DisponibilidadUpdateSchema,
    DisponibilidadTallerResponse,
    DisponibilidadUsuarioResponse
)
from app.services.taller_service import TallerService
from app.models.usuario import Usuario
from app.models.taller import Taller

router = APIRouter(prefix="/disponibilidad", tags=["Disponibilidad"])
taller_service = TallerService()

@router.get("/taller", response_model=List[DisponibilidadTallerResponse])
def listar_disponibilidad_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Lista toda la disponibilidad configurada por el taller autenticado."""
    disponibilidades = taller_service.obtener_disponibilidad_taller(
        db, str(current_taller.id)
    )
    return [DisponibilidadTallerResponse(
        id=str(d.id),
        fecha=d.fecha,
        hora_inicio=d.hora_inicio,
        hora_fin=d.hora_fin,
        cupos_totales=d.cupos_totales,
        cupos_ocupados=d.cupos_ocupados,
        activo=d.activo
    ) for d in disponibilidades]

@router.get("/{taller_id}", response_model=List[DisponibilidadUsuarioResponse])
def listar_disponibilidad_para_reserva(
    taller_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista las franjas disponibles de un taller para realizar una reserva."""
    try:
        disponibilidades = taller_service.obtener_disponibilidad_para_reserva(
            db, taller_id
        )
        return [DisponibilidadUsuarioResponse(
            id=str(d.id),
            fecha=d.fecha,
            hora_inicio=d.hora_inicio,
            hora_fin=d.hora_fin,
            cupos_disponibles=d.cupos_totales - d.cupos_ocupados
        ) for d in disponibilidades]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model=DisponibilidadTallerResponse, status_code=201)
def crear_disponibilidad(
    datos: DisponibilidadCreateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Registra una nueva franja horaria de disponibilidad."""
    try:
        disponibilidad = taller_service.crear_disponibilidad(
            db, str(current_taller.id),
            datos.fecha, datos.hora_inicio,
            datos.hora_fin, datos.cupos_totales
        )
        return DisponibilidadTallerResponse(
            id=str(disponibilidad.id),
            fecha=disponibilidad.fecha,
            hora_inicio=disponibilidad.hora_inicio,
            hora_fin=disponibilidad.hora_fin,
            cupos_totales=disponibilidad.cupos_totales,
            cupos_ocupados=disponibilidad.cupos_ocupados,
            activo=disponibilidad.activo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{disponibilidad_id}", response_model=DisponibilidadTallerResponse)
def actualizar_estado_disponibilidad(
    disponibilidad_id: str,
    datos: DisponibilidadUpdateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Activa o desactiva una franja horaria del taller autenticado."""
    try:
        disponibilidad = taller_service.actualizar_estado_disponibilidad(
            db, disponibilidad_id, str(current_taller.id), datos.activo
        )
        return DisponibilidadTallerResponse(
            id=str(disponibilidad.id),
            fecha=disponibilidad.fecha,
            hora_inicio=disponibilidad.hora_inicio,
            hora_fin=disponibilidad.hora_fin,
            cupos_totales=disponibilidad.cupos_totales,
            cupos_ocupados=disponibilidad.cupos_ocupados,
            activo=disponibilidad.activo
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))