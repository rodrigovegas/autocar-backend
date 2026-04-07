from sqlalchemy.orm import Session
from app.models.vehiculo import Vehiculo
from app.models.reserva import Reserva
import uuid

class VehiculoRepository:

    def obtener_por_usuario(self, db: Session, usuario_id: str):
        return db.query(Vehiculo).filter(
            Vehiculo.usuario_id == usuario_id,
            Vehiculo.activo == True
        ).all()

    def obtener_por_id(self, db: Session, vehiculo_id: str):
        return db.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id
        ).first()

    def crear(self, db: Session, usuario_id: str, marca: str,
              modelo: str, anio: int, kilometraje_actual: int,
              placa: str = None, color: str = None,
              tipo_combustible: str = None):
        vehiculo = Vehiculo(
            usuario_id=usuario_id,
            marca=marca,
            modelo=modelo,
            anio=anio,
            kilometraje_actual=kilometraje_actual,
            placa=placa,
            color=color,
            tipo_combustible=tipo_combustible,
        )
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        return vehiculo

    def actualizar(self, db: Session, vehiculo: Vehiculo,
                   marca: str = None, modelo: str = None,
                   anio: int = None, kilometraje_actual: int = None,
                   placa: str = None, color: str = None,
                   tipo_combustible: str = None):
        if marca is not None:
            vehiculo.marca = marca
        if modelo is not None:
            vehiculo.modelo = modelo
        if anio is not None:
            vehiculo.anio = anio
        if kilometraje_actual is not None:
            vehiculo.kilometraje_actual = kilometraje_actual
        if placa is not None:
            vehiculo.placa = placa
        if color is not None:
            vehiculo.color = color
        if tipo_combustible is not None:
            vehiculo.tipo_combustible = tipo_combustible
        db.commit()
        db.refresh(vehiculo)
        return vehiculo

    def desactivar(self, db: Session, vehiculo: Vehiculo):
        vehiculo.activo = False
        db.commit()
        return vehiculo

    def tiene_reservas_activas(self, db: Session, vehiculo_id: str) -> bool:
        count = db.query(Reserva).filter(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado.in_(["pendiente", "confirmada"])
        ).count()
        return count > 0