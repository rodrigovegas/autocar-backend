from sqlalchemy.orm import Session
from app.models.recordatorio import Recordatorio
from app.schemas.recordatorio import RecordatorioCreate

class RecordatorioRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, datos: RecordatorioCreate) -> Recordatorio:
        recordatorio = Recordatorio(**datos.model_dump())
        self.db.add(recordatorio)
        self.db.commit()
        self.db.refresh(recordatorio)
        return recordatorio

    def listar_por_vehiculo(self, vehiculo_id: int) -> list[Recordatorio]:
        return (
            self.db.query(Recordatorio)
            .filter(Recordatorio.vehiculo_id == vehiculo_id)
            .order_by(Recordatorio.fecha_programada.asc())
            .all()
        )

    def obtener_por_id(self, recordatorio_id: int) -> Recordatorio | None:
        return (
            self.db.query(Recordatorio)
            .filter(Recordatorio.id == recordatorio_id)
            .first()
        )

    def marcar_completado(self, recordatorio: Recordatorio) -> Recordatorio:
        recordatorio.completado = True
        self.db.commit()
        self.db.refresh(recordatorio)
        return recordatorio

    def eliminar(self, recordatorio: Recordatorio):
        self.db.delete(recordatorio)
        self.db.commit()