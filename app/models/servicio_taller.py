from sqlalchemy import Column, String, Boolean, SmallInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class ServicioTaller(Base):
    __tablename__ = "servicio_taller"
    __table_args__ = (
        UniqueConstraint("taller_id", "tipo_mantenimiento_id", name="uq_taller_tipo"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taller_id = Column(UUID(as_uuid=True), ForeignKey("taller.id"), nullable=False)
    tipo_mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("tipo_mantenimiento.id"), nullable=False)
    nombre_personalizado = Column(String(100), nullable=True)
    descripcion_personalizada = Column(Text, nullable=True)
    tiempo_estimado_minutos = Column(SmallInteger, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    taller = relationship("Taller", back_populates="servicios")
    tipo_mantenimiento = relationship("TipoMantenimiento", back_populates="servicios")
    reservas_servicio = relationship("ReservaServicio", back_populates="servicio_taller")