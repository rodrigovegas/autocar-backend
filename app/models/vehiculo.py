from sqlalchemy import Column, String, Boolean, DateTime, Integer, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    marca = Column(String(80), nullable=False)
    modelo = Column(String(80), nullable=False)
    anio = Column(SmallInteger, nullable=False)
    kilometraje_actual = Column(Integer, nullable=False)
    placa = Column(String(10), nullable=True, unique=True)
    color = Column(String(50), nullable=True)
    tipo_combustible = Column(String(20), nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True, nullable=False)

    usuario = relationship("Usuario", back_populates="vehiculos")
    reservas = relationship("Reserva", back_populates="vehiculo")
    mantenimientos = relationship("Mantenimiento", back_populates="vehiculo")
    recordatorios = relationship("Recordatorio", back_populates="vehiculo")