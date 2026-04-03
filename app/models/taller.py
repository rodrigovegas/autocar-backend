from sqlalchemy import Column, String, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Taller(Base):
    __tablename__ = "taller"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    especialidad = Column(String(100), nullable=False)
    direccion_texto = Column(String(250), nullable=False)
    telefono = Column(String(20), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    latitud = Column(Numeric(10, 7), nullable=True)
    longitud = Column(Numeric(10, 7), nullable=True)
    estado = Column(String(20), default="pendiente", nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    fecha_activacion = Column(DateTime(timezone=True), nullable=True)

    servicios = relationship("ServicioTaller", back_populates="taller")
    disponibilidades = relationship("DisponibilidadTaller", back_populates="taller")
    reservas = relationship("Reserva", back_populates="taller")
    mantenimientos = relationship("Mantenimiento", back_populates="taller")
    contenidos = relationship("ContenidoEducativo", back_populates="taller")
    