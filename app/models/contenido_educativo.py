from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class ContenidoEducativo(Base):
    __tablename__ = "contenido_educativo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taller_id = Column(UUID(as_uuid=True), ForeignKey("taller.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    cuerpo = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False)
    url_imagen = Column(String(500), nullable=True)
    url_video = Column(String(500), nullable=True)
    estado = Column(String(20), default="pendiente", nullable=False)
    informe_ia = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    fecha_publicacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_revision = Column(DateTime(timezone=True), nullable=True)

    taller = relationship("Taller", back_populates="contenidos")