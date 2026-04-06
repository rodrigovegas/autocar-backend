from sqlalchemy.orm import Session
from app.repositories.mantenimiento_repository import MantenimientoRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.mantenimiento import MantenimientoCreate
from fastapi import HTTPException

class MantenimientoService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = MantenimientoRepository(db)
        self.vehiculo_repo = VehiculoRepository()

    def registrar(self, datos: MantenimientoCreate, usuario_id: str):
        vehiculo = self.vehiculo_repo.obtener_por_id(self.db, datos.vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise HTTPException(status_code=403, detail="No tienes permiso sobre este vehículo")
        return self.repo.crear(datos)

    def listar_por_vehiculo(self, vehiculo_id: str, usuario_id: str):
        vehiculo = self.vehiculo_repo.obtener_por_id(self.db, vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise HTTPException(status_code=403, detail="No tienes permiso sobre este vehículo")
        return self.repo.listar_por_vehiculo(vehiculo_id)

    def eliminar(self, mantenimiento_id: int, usuario_id: str):
        registro = self.repo.obtener_por_id(mantenimiento_id)
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        vehiculo = self.vehiculo_repo.obtener_por_id(self.db, str(registro.vehiculo_id))
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise HTTPException(status_code=403, detail="No tienes permiso")
        self.repo.eliminar(registro)
        return {"mensaje": "Registro eliminado correctamente"}

    def listar_tipos(self):
        return self.repo.listar_tipos()