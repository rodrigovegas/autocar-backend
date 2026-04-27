from sqlalchemy.orm import Session, joinedload
from app.models.recordatorio import Recordatorio
import uuid


class RecordatorioRepository:

    def obtener_por_id(self, db: Session, recordatorio_id: str) -> Recordatorio | None:
        return (
            db.query(Recordatorio)
            .options(
                joinedload(Recordatorio.vehiculo),
                joinedload(Recordatorio.tipo_mantenimiento),
            )
            .filter(Recordatorio.id == uuid.UUID(recordatorio_id))
            .first()
        )

    def listar_por_usuario(self, db: Session, usuario_id: str) -> list[Recordatorio]:
        return (
            db.query(Recordatorio)
            .options(
                joinedload(Recordatorio.vehiculo),
                joinedload(Recordatorio.tipo_mantenimiento),
            )
            .filter(
                Recordatorio.usuario_id == uuid.UUID(usuario_id),
                Recordatorio.estado == "activo",
            )
            .order_by(Recordatorio.fecha_programada.asc().nulls_last())
            .all()
        )

    def existe_activo_mismo_tipo(
        self, db: Session, vehiculo_id: str, tipo_mantenimiento_id: str
    ) -> bool:
        count = (
            db.query(Recordatorio)
            .filter(
                Recordatorio.vehiculo_id == uuid.UUID(vehiculo_id),
                Recordatorio.tipo_mantenimiento_id == uuid.UUID(tipo_mantenimiento_id),
                Recordatorio.estado == "activo",
            )
            .count()
        )
        return count > 0

    def crear(
        self,
        db: Session,
        usuario_id: str,
        vehiculo_id: str,
        tipo_mantenimiento_id: str,
        fecha_programada=None,
        kilometraje_programado=None,
        texto_personalizado=None,
    ) -> Recordatorio:
        recordatorio = Recordatorio(
            usuario_id=uuid.UUID(usuario_id),
            vehiculo_id=uuid.UUID(vehiculo_id),
            tipo_mantenimiento_id=uuid.UUID(tipo_mantenimiento_id),
            origen="manual",
            fecha_programada=fecha_programada,
            kilometraje_programado=kilometraje_programado,
            texto_personalizado=texto_personalizado,
            estado="activo",
        )
        db.add(recordatorio)
        db.commit()
        db.refresh(recordatorio)
        return self.obtener_por_id(db, str(recordatorio.id))

    def eliminar(self, db: Session, recordatorio: Recordatorio) -> None:
        db.delete(recordatorio)
        db.commit()
