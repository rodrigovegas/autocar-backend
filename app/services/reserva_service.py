from sqlalchemy.orm import Session
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.disponibilidad_repository import DisponibilidadRepository
from app.models.servicio_taller import ServicioTaller

reserva_repo = ReservaRepository()
disponibilidad_repo = DisponibilidadRepository()

ESTADOS_VALIDOS_TRANSICION = {
    "pendiente": ["confirmada", "rechazada", "cancelada"],
    "confirmada": ["completada", "cancelada"],
    "rechazada": [],
    "completada": [],
    "cancelada": []
}

class ReservaService:

    def crear_reserva(self, db: Session, usuario_id: str, taller_id: str,
                      vehiculo_id: str, disponibilidad_id: str,
                      servicios_ids: list, descripcion_otro: str = None):
        """Crea una reserva aplicando todas las reglas de negocio."""

        disponibilidad = disponibilidad_repo.obtener_por_id(db, disponibilidad_id)
        if not disponibilidad:
            raise ValueError("La franja horaria seleccionada no existe")

        if not disponibilidad.activo:
            raise ValueError("La franja horaria seleccionada no está disponible")

        if disponibilidad.cupos_ocupados >= disponibilidad.cupos_totales:
            raise ValueError(
                "No hay cupos disponibles para la franja horaria seleccionada"
            )

        if reserva_repo.verificar_duplicado_activo(
            db, usuario_id, vehiculo_id, taller_id
        ):
            raise ValueError(
                "Ya existe una reserva activa en este taller para ese vehículo"
            )

        for servicio_id in servicios_ids:
            servicio = db.query(ServicioTaller).filter(
                ServicioTaller.id == servicio_id,
                ServicioTaller.taller_id == taller_id,
                ServicioTaller.activo == True
            ).first()
            if not servicio:
                raise ValueError(
                    f"El servicio {servicio_id} no pertenece al taller o no está activo"
                )

        reserva = reserva_repo.crear(
            db, usuario_id, taller_id, vehiculo_id,
            disponibilidad_id, descripcion_otro
        )
        reserva_repo.agregar_servicios(db, str(reserva.id), servicios_ids)
        reserva_repo.incrementar_cupos(db, disponibilidad_id)
        db.commit()
        db.refresh(reserva)
        return reserva

    def obtener_reservas_usuario(self, db: Session, usuario_id: str):
        return reserva_repo.obtener_por_usuario(db, usuario_id)

    def obtener_reservas_taller(self, db: Session, taller_id: str):
        return reserva_repo.obtener_por_taller(db, taller_id)

    def actualizar_estado_taller(self, db: Session, reserva_id: str,
                                  taller_id: str, nuevo_estado: str,
                                  motivo_rechazo: str = None):
        reserva = reserva_repo.obtener_por_id(db, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        if str(reserva.taller_id) != str(taller_id):
            raise PermissionError(
                "No tiene permisos para gestionar esta reserva"
            )

        if nuevo_estado not in ESTADOS_VALIDOS_TRANSICION.get(reserva.estado, []):
            raise ValueError(
                f"No se puede cambiar el estado de {reserva.estado} a {nuevo_estado}"
            )

        if nuevo_estado == "rechazada":
            reserva_repo.liberar_cupos(db, str(reserva.disponibilidad_id))

        return reserva_repo.actualizar_estado(
            db, reserva, nuevo_estado, motivo_rechazo
        )

    def cancelar_reserva_usuario(self, db: Session, reserva_id: str,
                                  usuario_id: str):
        reserva = reserva_repo.obtener_por_id(db, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        if str(reserva.usuario_id) != str(usuario_id):
            raise PermissionError(
                "No tiene permisos para cancelar esta reserva"
            )

        if reserva.estado != "pendiente":
            raise ValueError(
                "Solo se pueden cancelar reservas en estado pendiente."
            )

        reserva_repo.liberar_cupos(db, str(reserva.disponibilidad_id))
        return reserva_repo.actualizar_estado(db, reserva, "cancelada")