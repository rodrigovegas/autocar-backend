from sqlalchemy import Column, String, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class TipoMantenimiento(Base):
    __tablename__ = "tipo_mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion_base = Column(Text, nullable=False)
    intervalo_km = Column(Integer, nullable=True)
    intervalo_dias = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    estado = Column(String(20), default="aprobado", nullable=False)

    servicios = relationship("ServicioTaller", back_populates="tipo_mantenimiento")
    recordatorios = relationship("Recordatorio", back_populates="tipo_mantenimiento")