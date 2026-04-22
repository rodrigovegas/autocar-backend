from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Especialidad(Base):
    __tablename__ = "especialidad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    talleres = relationship("Taller", back_populates="especialidad_rel")