from sqlalchemy import Column, String, DateTime, Text, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Reserva(Base):
    __tablename__ = "reserva"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    taller_id = Column(UUID(as_uuid=True), ForeignKey("taller.id"), nullable=False)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("vehiculo.id"), nullable=False)
    disponibilidad_id = Column(UUID(as_uuid=True), ForeignKey("disponibilidad_taller.id"), nullable=False)
    estado = Column(String(20), default="pendiente", nullable=False)
    motivo_rechazo = Column(Text, nullable=True)
    descripcion_otro = Column(Text, nullable=True)
    calificacion = Column(SmallInteger, nullable=True)
    comentario_calificacion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="reservas")
    taller = relationship("Taller", back_populates="reservas")
    vehiculo = relationship("Vehiculo", back_populates="reservas")
    disponibilidad = relationship("DisponibilidadTaller", back_populates="reservas")
    servicios = relationship("ReservaServicio", back_populates="reserva")
    mantenimiento = relationship("Mantenimiento", back_populates="reserva", uselist=False)