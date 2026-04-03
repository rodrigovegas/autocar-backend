from sqlalchemy.orm import Session
from app.models.vehiculo import Vehiculo
from app.models.reserva import Reserva
import uuid

class VehiculoRepository:

    def obtener_por_usuario(self, db: Session, usuario_id: str):
        """Obtiene todos los vehículos activos de un usuario."""
        return db.query(Vehiculo).filter(
            Vehiculo.usuario_id == usuario_id,
            Vehiculo.activo == True
        ).all()

    def obtener_por_id(self, db: Session, vehiculo_id: str):
        """Obtiene un vehículo por su ID."""
        return db.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id
        ).first()

    def crear(self, db: Session, usuario_id: str, marca: str,
              modelo: str, anio: int, kilometraje_actual: int):
        """Crea un nuevo vehículo asociado al usuario."""
        vehiculo = Vehiculo(
            usuario_id=usuario_id,
            marca=marca,
            modelo=modelo,
            anio=anio,
            kilometraje_actual=kilometraje_actual
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return vehiculo

    def actualizar(self, db: Session, vehiculo: Vehiculo,
                   marca: str = None, modelo: str = None,
                   anio: int = None, kilometraje_actual: int = None):
        """Actualiza los datos de un vehículo."""
        if marca is not None:
            vehiculo.marca = marca
        if modelo is not None:
            vehiculo.modelo = modelo
        if anio is not None:
            vehiculo.anio = anio
        if kilometraje_actual is not None:
            vehiculo.kilometraje_actual = kilometraje_actual
        db.commit()
        db.refresh(vehiculo)
        return vehiculo

    def desactivar(self, db: Session, vehiculo: Vehiculo):
        """Desactiva un vehículo (eliminación lógica)."""
        vehiculo.activo = False
        db.commit()
        return vehiculo

    def tiene_reservas_activas(self, db: Session, vehiculo_id: str) -> bool:
        """Verifica si el vehículo tiene reservas en estado pendiente o confirmada."""
        count = db.query(Reserva).filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado.in_(["pendiente", "confirmada"])
        ).count()
        return count > 0