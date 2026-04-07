from sqlalchemy import Column, Integer, Text, Date, DateTime, Numeric, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Mantenimiento(Base):
    __tablename__ = "mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reserva_id = Column(UUID(as_uuid=True), ForeignKey("reserva.id"), unique=True, nullable=False)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("vehiculo.id"), nullable=False)
    taller_id = Column(UUID(as_uuid=True), ForeignKey("taller.id"), nullable=False)
    kilometraje_registro = Column(Integer, nullable=False)
    observaciones = Column(Text, nullable=True)
    fecha_realizado = Column(Date, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    costo = Column(Numeric(10, 2), nullable=True)
    detalle_tecnico = Column(Text, nullable=True)
    problemas_detectados = Column(Text, nullable=True)
    gravedad_problemas = Column(String(10), nullable=True)
    km_proximo_mantenimiento = Column(Integer, nullable=True)
    fecha_proximo_mantenimiento = Column(Date, nullable=True)
    recomendaciones = Column(Text, nullable=True)

    reserva = relationship("Reserva", back_populates="mantenimiento")
    vehiculo = relationship("Vehiculo", back_populates="mantenimientos")
    taller = relationship("Taller", back_populates="mantenimientos")