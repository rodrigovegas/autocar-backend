from datetime import date
from sqlalchemy.orm import Session
from app.repositories.recordatorio_repository import RecordatorioRepository
from app.models.vehiculo import Vehiculo
from app.models.tipo_mantenimiento import TipoMantenimiento
import uuid

recordatorio_repo = RecordatorioRepository()


class RecordatorioService:

    def listar_por_usuario(self, db: Session, usuario_id: str):
        return recordatorio_repo.listar_por_usuario(db, usuario_id)

    def crear(
        self,
        db: Session,
        usuario_id: str,
        vehiculo_id: str,
        tipo_mantenimiento_id: str,
        fecha_programada=None,
        kilometraje_programado=None,
        texto_personalizado=None,
    ):
        if fecha_programada is None and kilometraje_programado is None:
            raise ValueError("Debe especificar fecha o kilometraje (al menos uno)")

        if fecha_programada is not None and fecha_programada < date.today():
            raise ValueError("La fecha programada no puede ser en el pasado")

        vehiculo = db.query(Vehiculo).filter(
            Vehiculo.id == uuid.UUID(vehiculo_id)
        ).first()
        if not vehiculo:
            raise ValueError("Vehículo no encontrado")
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise PermissionError("No tiene permisos sobre este vehículo")
        if not vehiculo.activo:
            raise ValueError("El vehículo no está activo")

        if (
            kilometraje_programado is not None
            and kilometraje_programado <= vehiculo.kilometraje_actual
        ):
            raise ValueError(
                "El kilometraje del recordatorio debe ser mayor al kilometraje actual del vehículo"
            )

        tipo = db.query(TipoMantenimiento).filter(
            TipoMantenimiento.id == uuid.UUID(tipo_mantenimiento_id)
        ).first()
        if not tipo:
            raise ValueError("Tipo de mantenimiento no encontrado")
        if not tipo.activo or tipo.estado != "aprobado":
            raise ValueError("El tipo de mantenimiento no está disponible")

        if recordatorio_repo.existe_activo_mismo_tipo(
            db, vehiculo_id, tipo_mantenimiento_id
        ):
            raise ValueError(
                "Ya existe un recordatorio activo de ese tipo para este vehículo"
            )

        return recordatorio_repo.crear(
            db,
            usuario_id,
            vehiculo_id,
            tipo_mantenimiento_id,
            fecha_programada,
            kilometraje_programado,
            texto_personalizado,
        )

    def eliminar(self, db: Session, recordatorio_id: str, usuario_id: str):
        recordatorio = recordatorio_repo.obtener_por_id(db, recordatorio_id)
        if not recordatorio:
            raise ValueError("Recordatorio no encontrado")
        if str(recordatorio.usuario_id) != str(usuario_id):
            raise PermissionError(
                "No tiene permisos para eliminar este recordatorio"
            )
        recordatorio_repo.eliminar(db, recordatorio)
