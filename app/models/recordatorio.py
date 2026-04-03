from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Recordatorio(Base):
    __tablename__ = "recordatorio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("vehiculo.id"), nullable=False)
    tipo_mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("tipo_mantenimiento.id"), nullable=False)
    origen = Column(String(20), nullable=False)
    fecha_programada = Column(Date, nullable=True)
    kilometraje_programado = Column(Integer, nullable=True)
    texto_personalizado = Column(Text, nullable=True)
    estado = Column(String(20), default="activo", nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_envio = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship("Usuario", back_populates="recordatorios")
    vehiculo = relationship("Vehiculo", back_populates="recordatorios")
    tipo_mantenimiento = relationship("TipoMantenimiento", back_populates="recordatorios")