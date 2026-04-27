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

    # ── FASE 2: recordatorio automático desde mantenimiento del taller ──

    def crear_automatico_desde_mantenimiento(
        self,
        db: Session,
        usuario_id: str,
        vehiculo_id: str,
        tipo_mantenimiento_id: str,
        fecha_programada: date | None,
        kilometraje_programado: int | None,
        texto_personalizado: str | None = None,
    ):
        """Crea un recordatorio automático al registrar un mantenimiento.

        No hace commit: deja la transacción abierta para que el servicio de
        mantenimientos confirme todo de forma atómica con db.commit().

        No repite las validaciones de 'vehículo activo' ni 'tipo aprobado'
        porque ambas condiciones ya están garantizadas por la reserva
        confirmada que originó este mantenimiento.
        """
        if fecha_programada is None and kilometraje_programado is None:
            raise ValueError(
                "Para crear el recordatorio debe especificar fecha o "
                "kilometraje del próximo mantenimiento"
            )

        # Si existe un recordatorio activo del mismo tipo+vehículo (sea manual
        # o automático), el dato del taller es más preciso: se reemplaza.
        existente = recordatorio_repo.obtener_activo_por_vehiculo_y_tipo(
            db, vehiculo_id, tipo_mantenimiento_id
        )
        if existente:
            recordatorio_repo.eliminar_flush(db, existente)

        return recordatorio_repo.crear_flush(
            db,
            usuario_id=usuario_id,
            vehiculo_id=vehiculo_id,
            tipo_mantenimiento_id=tipo_mantenimiento_id,
            origen="automatico",
            fecha_programada=fecha_programada,
            kilometraje_programado=kilometraje_programado,
            texto_personalizado=texto_personalizado,
        )


# Instancia de módulo — importable por otros servicios (ej. taller_mantenimiento_service)
recordatorio_service = RecordatorioService()
