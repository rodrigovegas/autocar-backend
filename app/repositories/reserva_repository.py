from sqlalchemy.orm import Session
from app.models.reserva import Reserva
from app.models.reserva_servicio import ReservaServicio
from app.models.disponibilidad_taller import DisponibilidadTaller

class ReservaRepository:

    def obtener_por_usuario(self, db: Session, usuario_id: str):
        """Obtiene todas las reservas del usuario."""
        return db.query(Reserva).filter(
            Reserva.usuario_id == usuario_id
        ).order_by(Reserva.fecha_creacion.desc()).all()

    def obtener_por_taller(self, db: Session, taller_id: str):
        """Obtiene todas las reservas del taller."""
        return db.query(Reserva).filter(
            Reserva.taller_id == taller_id
        ).order_by(Reserva.fecha_creacion.desc()).all()

    def obtener_por_id(self, db: Session, reserva_id: str):
        """Obtiene una reserva por su ID."""
        return db.query(Reserva).filter(
            Reserva.id == reserva_id
        ).first()

    def verificar_duplicado_activo(self, db: Session, usuario_id: str,
                                   vehiculo_id: str, taller_id: str) -> bool:
        """Verifica si existe una reserva activa duplicada (RN-16)."""
        count = db.query(Reserva).filter(
            Reserva.usuario_id == usuario_id,
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.taller_id == taller_id,
            Reserva.estado.in_(["pendiente", "confirmada"])
        ).count()
        return count > 0

    def crear(self, db: Session, usuario_id: str, taller_id: str,
              vehiculo_id: str, disponibilidad_id: str):
        """Crea una nueva reserva en estado pendiente."""
        reserva = Reserva(
            usuario_id=usuario_id,
            taller_id=taller_id,
            vehiculo_id=vehiculo_id,
            disponibilidad_id=disponibilidad_id,
            estado="pendiente"
        )
        db.add(reserva)
        db.flush()
        return reserva

    def agregar_servicios(self, db: Session, reserva_id: str,
                          servicios_ids: list):
        """Asocia servicios a una reserva."""
        for servicio_id in servicios_ids:
            reserva_servicio = ReservaServicio(
                reserva_id=reserva_id,
                servicio_taller_id=servicio_id
            )
            db.add(reserva_servicio)

    def actualizar_estado(self, db: Session, reserva: Reserva,
                          nuevo_estado: str, motivo_rechazo: str = None):
        """Actualiza el estado de una reserva."""
        reserva.estado = nuevo_estado
        if motivo_rechazo:
            reserva.motivo_rechazo = motivo_rechazo
        db.commit()
        db.refresh(reserva)
        return reserva

    def incrementar_cupos(self, db: Session, disponibilidad_id: str):
        """Incrementa los cupos ocupados de una franja horaria."""
        disponibilidad = db.query(DisponibilidadTaller).filter(
            DisponibilidadTaller.id == disponibilidad_id
        ).first()
        if disponibilidad:
            disponibilidad.cupos_ocupados += 1
            db.flush()

    def liberar_cupos(self, db: Session, disponibilidad_id: str):
        """Libera un cupo al rechazar o cancelar una reserva."""
        disponibilidad = db.query(DisponibilidadTaller).filter(
            DisponibilidadTaller.id == disponibilidad_id
        ).first()
        if disponibilidad and disponibilidad.cupos_ocupados > 0:
            disponibilidad.cupos_ocupados -= 1
            db.flush()