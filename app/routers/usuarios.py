from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.reserva import Reserva
from app.models.mantenimiento import Mantenimiento
from app.models.recordatorio import Recordatorio

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/estadisticas")
def estadisticas_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehiculos_count = db.query(Vehiculo).filter(
        Vehiculo.usuario_id == current_user.id,
        Vehiculo.activo == True,
    ).count()

    reservas_activas = db.query(Reserva).filter(
        Reserva.usuario_id == current_user.id,
        Reserva.estado.in_(["pendiente", "confirmada"]),
    ).count()

    vehiculo_ids = [
        v.id
        for v in db.query(Vehiculo.id)
        .filter(Vehiculo.usuario_id == current_user.id)
        .all()
    ]

    mantenimientos_count = 0
    if vehiculo_ids:
        mantenimientos_count = db.query(Mantenimiento).filter(
            Mantenimiento.vehiculo_id.in_(vehiculo_ids)
        ).count()

    proximo = (
        db.query(Recordatorio)
        .filter(
            Recordatorio.usuario_id == current_user.id,
            Recordatorio.estado == "activo",
            Recordatorio.fecha_programada.isnot(None),
        )
        .order_by(Recordatorio.fecha_programada.asc())
        .first()
    )

    return {
        "vehiculos_registrados": vehiculos_count,
        "reservas_activas": reservas_activas,
        "mantenimientos_completados": mantenimientos_count,
        "proximo_mantenimiento": (
            str(proximo.fecha_programada)
            if proximo and proximo.fecha_programada
            else None
        ),
    }
