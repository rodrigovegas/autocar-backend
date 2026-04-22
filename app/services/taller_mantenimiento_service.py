from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid

from app.models.mantenimiento import Mantenimiento
from app.models.reserva import Reserva
from app.models.vehiculo import Vehiculo
from app.schemas.mantenimiento_registro import MantenimientoRegistroCreate


class TallerMantenimientoService:

    def registrar_mantenimiento(
        self,
        db: Session,
        datos: MantenimientoRegistroCreate,
        taller_id,
    ) -> Mantenimiento:
        reserva = db.query(Reserva).filter(
            Reserva.id == uuid.UUID(datos.reserva_id),
            Reserva.taller_id == taller_id,
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
            taller_id=taller_id,
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

    def historial_usuario(self, db: Session, usuario_id) -> List[dict]:
        vehiculos = db.query(Vehiculo).filter(
            Vehiculo.usuario_id == usuario_id
        ).all()
        vehiculo_ids = [v.id for v in vehiculos]
        mantenimientos = (
            db.query(Mantenimiento)
            .options(
                joinedload(Mantenimiento.taller),
                joinedload(Mantenimiento.vehiculo),
            )
            .filter(Mantenimiento.vehiculo_id.in_(vehiculo_ids))
            .order_by(Mantenimiento.fecha_realizado.desc())
            .all()
        )
        return [
            {
                "id": m.id,
                "vehiculo_id": m.vehiculo_id,
                "vehiculo_nombre": (
                    f"{m.vehiculo.marca} {m.vehiculo.modelo}"
                    if m.vehiculo else None
                ),
                "taller_id": m.taller_id,
                "taller_nombre": m.taller.nombre if m.taller else None,
                "kilometraje_registro": m.kilometraje_registro,
                "fecha_realizado": m.fecha_realizado,
                "costo": float(m.costo) if m.costo is not None else None,
                "detalle_tecnico": m.detalle_tecnico,
                "problemas_detectados": m.problemas_detectados,
                "gravedad_problemas": m.gravedad_problemas,
                "km_proximo_mantenimiento": m.km_proximo_mantenimiento,
                "fecha_proximo_mantenimiento": m.fecha_proximo_mantenimiento,
                "recomendaciones": m.recomendaciones,
                "observaciones": m.observaciones,
                "fecha_registro": m.fecha_registro,
            }
            for m in mantenimientos
        ]

    def historial_taller(self, db: Session, taller_id) -> List[dict]:
        mantenimientos = (
            db.query(Mantenimiento)
            .options(joinedload(Mantenimiento.vehiculo))
            .filter(Mantenimiento.taller_id == taller_id)
            .order_by(Mantenimiento.fecha_realizado.desc())
            .all()
        )
        return [
            {
                "id": str(m.id),
                "fecha_realizado": (
                    str(m.fecha_realizado) if m.fecha_realizado else None
                ),
                "kilometraje_registro": m.kilometraje_registro,
                "observaciones": m.observaciones,
                "costo": m.costo,
                "detalle_tecnico": m.detalle_tecnico,
                "problemas_detectados": m.problemas_detectados,
                "gravedad_problemas": m.gravedad_problemas,
                "km_proximo_mantenimiento": m.km_proximo_mantenimiento,
                "fecha_proximo_mantenimiento": (
                    str(m.fecha_proximo_mantenimiento)
                    if m.fecha_proximo_mantenimiento else None
                ),
                "recomendaciones": m.recomendaciones,
                "marca": m.vehiculo.marca if m.vehiculo else None,
                "modelo": m.vehiculo.modelo if m.vehiculo else None,
                "anio": m.vehiculo.anio if m.vehiculo else None,
                "placa": m.vehiculo.placa if m.vehiculo else None,
                "color": m.vehiculo.color if m.vehiculo else None,
            }
            for m in mantenimientos
        ]
