from sqlalchemy import Column, Boolean, SmallInteger, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class DisponibilidadTaller(Base):
    __tablename__ = "disponibilidad_taller"
    __table_args__ = (
        UniqueConstraint("taller_id", "fecha", "hora_inicio", "hora_fin", name="uq_disponibilidad"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taller_id = Column(UUID(as_uuid=True), ForeignKey("taller.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    cupos_totales = Column(SmallInteger, nullable=False)
    cupos_ocupados = Column(SmallInteger, default=0, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    taller = relationship("Taller", back_populates="disponibilidades")
    reservas = relationship("Reserva", back_populates="disponibilidad")