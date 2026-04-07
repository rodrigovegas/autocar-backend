from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_taller, get_current_user
from app.schemas.mantenimiento_registro import (
    MantenimientoRegistroCreate,
    MantenimientoRegistroResponse,
    MantenimientoHistorialResponse,
)
from app.models.mantenimiento import Mantenimiento
from app.models.reserva import Reserva
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
import uuid

router = APIRouter(prefix="/mantenimientos", tags=["Mantenimiento"])


@router.post("/", response_model=MantenimientoRegistroResponse, status_code=201)
def registrar_mantenimiento(
    datos: MantenimientoRegistroCreate,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
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

    existente = db.query(Mantenimiento).filter(
        Mantenimiento.reserva_id == uuid.UUID(datos.reserva_id)
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Esta reserva ya tiene un mantenimiento registrado",
        )

    mantenimiento = Mantenimiento(
        reserva_id=uuid.UUID(datos.reserva_id),
        vehiculo_id=reserva.vehiculo_id,
        taller_id=current_taller.id,
        kilometraje_registro=datos.kilometraje_registro,
        fecha_realizado=datos.fecha_realizado,
        observaciones=datos.detalle_tecnico,
        costo=datos.costo,
        detalle_tecnico=datos.detalle_tecnico,
        problemas_detectados=datos.problemas_detectados,
        gravedad_problemas=datos.gravedad_problemas,
        km_proximo_mantenimiento=datos.km_proximo_mantenimiento,
        fecha_proximo_mantenimiento=datos.fecha_proximo_mantenimiento,
        recomendaciones=datos.recomendaciones,
    )
    db.add(mantenimiento)
    reserva.estado = "completada"
    db.commit()
    db.refresh(mantenimiento)
    return mantenimiento


@router.get("/historial/usuario", response_model=List[MantenimientoHistorialResponse])
def historial_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehiculos = db.query(Vehiculo).filter(
        Vehiculo.usuario_id == current_user.id
    ).all()
    vehiculo_ids = [v.id for v in vehiculos]
    return (
        db.query(Mantenimiento)
        .filter(Mantenimiento.vehiculo_id.in_(vehiculo_ids))
        .order_by(Mantenimiento.fecha_realizado.desc())
        .all()
    )


@router.get("/historial/taller", response_model=List[dict])
def historial_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    resultado = db.execute(text("""
        SELECT 
            m.id::text,
            m.fecha_realizado::text,
            m.kilometraje_registro,
            m.observaciones,
            m.costo,
            m.detalle_tecnico,
            m.problemas_detectados,
            m.gravedad_problemas,
            m.km_proximo_mantenimiento,
            m.fecha_proximo_mantenimiento::text,
            m.recomendaciones,
            v.marca,
            v.modelo,
            v.anio,
            v.placa,
            v.color
        FROM mantenimiento m
        JOIN vehiculo v ON v.id = m.vehiculo_id
        WHERE m.taller_id = :taller_id
        ORDER BY m.fecha_realizado DESC
    """), {"taller_id": str(current_taller.id)})

    rows = resultado.fetchall()
    return [
        {
            "id": row[0],
            "fecha_realizado": row[1],
            "kilometraje_registro": row[2],
            "observaciones": row[3],
            "costo": row[4],
            "detalle_tecnico": row[5],
            "problemas_detectados": row[6],
            "gravedad_problemas": row[7],
            "km_proximo_mantenimiento": row[8],
            "fecha_proximo_mantenimiento": row[9],
            "recomendaciones": row[10],
            "marca": row[11],
            "modelo": row[12],
            "anio": row[13],
            "placa": row[14],
            "color": row[15],
        }
        for row in rows
    ]