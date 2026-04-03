from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class ReservaServicio(Base):
    __tablename__ = "reserva_servicio"
    __table_args__ = (
        UniqueConstraint("reserva_id", "servicio_taller_id", name="uq_reserva_servicio"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reserva_id = Column(UUID(as_uuid=True), ForeignKey("reserva.id"), nullable=False)
    servicio_taller_id = Column(UUID(as_uuid=True), ForeignKey("servicio_taller.id"), nullable=False)

    reserva = relationship("Reserva", back_populates="servicios")
    servicio_taller = relationship("ServicioTaller", back_populates="reservas_servicio")