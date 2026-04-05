from sqlalchemy.orm import Session
from app.models.mantenimiento import Mantenimiento
from app.models.tipo_mantenimiento import TipoMantenimiento
from app.schemas.mantenimiento import MantenimientoCreate

class MantenimientoRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, datos: MantenimientoCreate) -> Mantenimiento:
        registro = Mantenimiento(**datos.model_dump())
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def listar_por_vehiculo(self, vehiculo_id: int) -> list[Mantenimiento]:
        return (
            self.db.query(Mantenimiento)
            .filter(Mantenimiento.vehiculo_id == vehiculo_id)
            .order_by(Mantenimiento.fecha.desc())
            .all()
        )

    def obtener_por_id(self, mantenimiento_id: int) -> Mantenimiento | None:
        return (
            self.db.query(Mantenimiento)
            .filter(Mantenimiento.id == mantenimiento_id)
            .first()
        )

    def eliminar(self, mantenimiento: Mantenimiento):
        self.db.delete(mantenimiento)
        self.db.commit()

    def listar_tipos(self) -> list[TipoMantenimiento]:
        return self.db.query(TipoMantenimiento).all()