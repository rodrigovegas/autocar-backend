from sqlalchemy.orm import Session
from app.repositories.recordatorio_repository import RecordatorioRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.recordatorio import RecordatorioCreate
from fastapi import HTTPException

class RecordatorioService:

    def __init__(self, db: Session):
        self.repo = RecordatorioRepository(db)
        self.vehiculo_repo = VehiculoRepository(db)

    def _verificar_vehiculo(self, vehiculo_id: int, usuario_id: int):
        vehiculo = self.vehiculo_repo.obtener_por_id(vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        if vehiculo.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso sobre este vehículo")
        return vehiculo

    def crear(self, datos: RecordatorioCreate, usuario_id: int):
        self._verificar_vehiculo(datos.vehiculo_id, usuario_id)
        return self.repo.crear(datos)

    def listar_por_vehiculo(self, vehiculo_id: int, usuario_id: int):
        self._verificar_vehiculo(vehiculo_id, usuario_id)
        return self.repo.listar_por_vehiculo(vehiculo_id)

    def marcar_completado(self, recordatorio_id: int, usuario_id: int):
        recordatorio = self.repo.obtener_por_id(recordatorio_id)
        if not recordatorio:
            raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
        self._verificar_vehiculo(recordatorio.vehiculo_id, usuario_id)
        return self.repo.marcar_completado(recordatorio)

    def eliminar(self, recordatorio_id: int, usuario_id: int):
        recordatorio = self.repo.obtener_por_id(recordatorio_id)
        if not recordatorio:
            raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
        self._verificar_vehiculo(recordatorio.vehiculo_id, usuario_id)
        self.repo.eliminar(recordatorio)
        return {"mensaje": "Recordatorio eliminado correctamente"}