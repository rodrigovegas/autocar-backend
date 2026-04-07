from sqlalchemy.orm import Session
from app.repositories.vehiculo_repository import VehiculoRepository

vehiculo_repo = VehiculoRepository()

class VehiculoService:

    def obtener_vehiculos_usuario(self, db: Session, usuario_id: str):
        return vehiculo_repo.obtener_por_usuario(db, usuario_id)

    def registrar_vehiculo(self, db: Session, usuario_id: str,
                           marca: str, modelo: str,
                           anio: int, kilometraje_actual: int,
                           placa: str = None, color: str = None,
                           tipo_combustible: str = None):
        return vehiculo_repo.crear(
            db, usuario_id, marca, modelo, anio, kilometraje_actual,
            placa, color, tipo_combustible
        )

    def actualizar_vehiculo(self, db: Session, vehiculo_id: str,
                            usuario_id: str, marca: str = None,
                            modelo: str = None, anio: int = None,
                            kilometraje_actual: int = None,
                            placa: str = None, color: str = None,
                            tipo_combustible: str = None):
        vehiculo = vehiculo_repo.obtener_por_id(db, vehiculo_id)
        if not vehiculo:
            raise ValueError("Vehículo no encontrado")
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise PermissionError("No tiene permisos para modificar este vehículo")
        if not vehiculo.activo:
            raise ValueError("El vehículo no está activo")
        return vehiculo_repo.actualizar(
            db, vehiculo, marca, modelo, anio, kilometraje_actual,
            placa, color, tipo_combustible
        )

    def eliminar_vehiculo(self, db: Session, vehiculo_id: str, usuario_id: str):
        vehiculo = vehiculo_repo.obtener_por_id(db, vehiculo_id)
        if not vehiculo:
            raise ValueError("Vehículo no encontrado")
        if str(vehiculo.usuario_id) != str(usuario_id):
            raise PermissionError("No tiene permisos para eliminar este vehículo")
        if vehiculo_repo.tiene_reservas_activas(db, vehiculo_id):
            raise ValueError(
                "No se puede eliminar el vehículo porque tiene reservas "
                "en estado pendiente o confirmada."
            )
        return vehiculo_repo.desactivar(db, vehiculo)