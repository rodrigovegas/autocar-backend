from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Notificacion(Base):
    __tablename__ = "notificacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destinatario_tipo = Column(String(20), nullable=False)
    destinatario_id = Column(UUID(as_uuid=True), nullable=False)
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=False)
    leida = Column(Boolean, default=False, nullable=False)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())