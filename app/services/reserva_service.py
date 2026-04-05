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
                      servicios_ids: list):
        """Crea una reserva aplicando todas las reglas de negocio."""

        # Verifica que la franja existe y tiene cupos
        disponibilidad = disponibilidad_repo.obtener_por_id(db, disponibilidad_id)
        if not disponibilidad:
            raise ValueError("La franja horaria seleccionada no existe")

        if not disponibilidad.activo:
            raise ValueError("La franja horaria seleccionada no está disponible")

        # RN-18: Verifica cupos disponibles
        if disponibilidad.cupos_ocupados >= disponibilidad.cupos_totales:
            raise ValueError(
                "No hay cupos disponibles para la franja horaria seleccionada"
            )

        # RN-16: Verifica reserva duplicada activa
        if reserva_repo.verificar_duplicado_activo(
            db, usuario_id, vehiculo_id, taller_id
        ):
            raise ValueError(
                "Ya existe una reserva activa en este taller para ese vehículo"
            )

        # Verifica que los servicios pertenecen al taller
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

        # Crea la reserva y asocia servicios en una transacción
        reserva = reserva_repo.crear(
            db, usuario_id, taller_id, vehiculo_id, disponibilidad_id
        )
        reserva_repo.agregar_servicios(db, str(reserva.id), servicios_ids)
        reserva_repo.incrementar_cupos(db, disponibilidad_id)
        db.commit()
        db.refresh(reserva)
        return reserva

    def obtener_reservas_usuario(self, db: Session, usuario_id: str):
        """Retorna todas las reservas del usuario."""
        return reserva_repo.obtener_por_usuario(db, usuario_id)

    def obtener_reservas_taller(self, db: Session, taller_id: str):
        """Retorna todas las reservas del taller."""
        return reserva_repo.obtener_por_taller(db, taller_id)

    def actualizar_estado_taller(self, db: Session, reserva_id: str,
                                  taller_id: str, nuevo_estado: str,
                                  motivo_rechazo: str = None):
        """El taller confirma o rechaza una reserva (RN-11)."""
        reserva = reserva_repo.obtener_por_id(db, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        # Verifica que la reserva pertenece al taller
        if str(reserva.taller_id) != str(taller_id):
            raise PermissionError(
                "No tiene permisos para gestionar esta reserva"
            )

        # RN-10: Verifica transición de estado válida
        if nuevo_estado not in ESTADOS_VALIDOS_TRANSICION.get(reserva.estado, []):
            raise ValueError(
                f"No se puede cambiar el estado de {reserva.estado} a {nuevo_estado}"
            )

        # Si rechaza libera el cupo
        if nuevo_estado == "rechazada":
            reserva_repo.liberar_cupos(db, str(reserva.disponibilidad_id))

        return reserva_repo.actualizar_estado(
            db, reserva, nuevo_estado, motivo_rechazo
        )

    def cancelar_reserva_usuario(self, db: Session, reserva_id: str,
                                  usuario_id: str):
        """El usuario cancela una reserva pendiente (RN-12)."""
        reserva = reserva_repo.obtener_por_id(db, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        # Verifica que pertenece al usuario
        if str(reserva.usuario_id) != str(usuario_id):
            raise PermissionError(
                "No tiene permisos para cancelar esta reserva"
            )

        # RN-12: Solo se pueden cancelar reservas pendientes
        if reserva.estado != "pendiente":
            raise ValueError(
                "Solo se pueden cancelar reservas en estado pendiente. "
                "Las reservas confirmadas no pueden cancelarse desde la aplicación."
            )

        # Libera el cupo
        reserva_repo.liberar_cupos(db, str(reserva.disponibilidad_id))
        return reserva_repo.actualizar_estado(db, reserva, "cancelada")
    