from sqlalchemy.orm import Session
from app.models.disponibilidad_taller import DisponibilidadTaller
from datetime import date

class DisponibilidadRepository:

    def obtener_por_taller(self, db: Session, taller_id: str):
        """Obtiene toda la disponibilidad configurada por el taller."""
        return db.query(DisponibilidadTaller).filter(
            DisponibilidadTaller.taller_id == taller_id
        ).order_by(DisponibilidadTaller.fecha, DisponibilidadTaller.hora_inicio).all()

    def obtener_disponible_por_taller(self, db: Session, taller_id: str):
        """Obtiene franjas con cupos disponibles para el usuario al reservar."""
        from sqlalchemy import and_
        return db.query(DisponibilidadTaller).filter(
            and_(
                DisponibilidadTaller.taller_id == taller_id,
                DisponibilidadTaller.activo == True,
                DisponibilidadTaller.fecha >= date.today(),
                DisponibilidadTaller.cupos_ocupados < DisponibilidadTaller.cupos_totales
            )
        ).order_by(DisponibilidadTaller.fecha, DisponibilidadTaller.hora_inicio).all()

    def obtener_por_id(self, db: Session, disponibilidad_id: str):
        """Obtiene una franja horaria por su ID."""
        return db.query(DisponibilidadTaller).filter(
            DisponibilidadTaller.id == disponibilidad_id
        ).first()

    def verificar_duplicado(self, db: Session, taller_id: str,
                            fecha: date, hora_inicio, hora_fin) -> bool:
        """Verifica si ya existe una franja con los mismos datos."""
        existente = db.query(DisponibilidadTaller).filter(
            DisponibilidadTaller.taller_id == taller_id,
            DisponibilidadTaller.fecha == fecha,
            DisponibilidadTaller.hora_inicio == hora_inicio,
            DisponibilidadTaller.hora_fin == hora_fin
        ).first()
        return existente is not None

    def crear(self, db: Session, taller_id: str, fecha: date,
              hora_inicio, hora_fin, cupos_totales: int):
        """Registra una nueva franja de disponibilidad."""
        disponibilidad = DisponibilidadTaller(
            taller_id=taller_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            cupos_totales=cupos_totales,
            cupos_ocupados=0,
            activo=True
        )
        db.add(disponibilidad)
        db.commit()
        db.refresh(disponibilidad)
        return disponibilidad

    def actualizar_estado(self, db: Session,
                          disponibilidad: DisponibilidadTaller, activo: bool):
        """Activa o desactiva una franja horaria."""
        disponibilidad.activo = activo
        db.commit()
        db.refresh(disponibilidad)
        return disponibilidad
    