from sqlalchemy.orm import Session
from app.models.contenido_educativo import ContenidoEducativo
from app.schemas.educativo import ContenidoCreateSchema
import uuid

class EducativoRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, taller_id: str, datos: ContenidoCreateSchema) -> ContenidoEducativo:
        contenido = ContenidoEducativo(
            taller_id=uuid.UUID(taller_id),
            titulo=datos.titulo,
            cuerpo=datos.cuerpo,
            categoria=datos.categoria,
            url_imagen=datos.url_imagen,
            url_video=datos.url_video,
            estado="pendiente"
        )
        self.db.add(contenido)
        self.db.commit()
        self.db.refresh(contenido)
        return contenido

    def listar_publicados(self) -> list[ContenidoEducativo]:
        return (
            self.db.query(ContenidoEducativo)
            .filter(ContenidoEducativo.estado == "publicado")
            .order_by(ContenidoEducativo.fecha_publicacion.desc())
            .all()
        )

    def listar_por_taller(self, taller_id: str) -> list[ContenidoEducativo]:
        return (
            self.db.query(ContenidoEducativo)
            .filter(ContenidoEducativo.taller_id == uuid.UUID(taller_id))
            .order_by(ContenidoEducativo.fecha_publicacion.desc())
            .all()
        )

    def listar_pendientes(self) -> list[ContenidoEducativo]:
        return (
            self.db.query(ContenidoEducativo)
            .filter(ContenidoEducativo.estado == "pendiente")
            .order_by(ContenidoEducativo.fecha_publicacion.asc())
            .all()
        )

    def obtener_por_id(self, contenido_id: str) -> ContenidoEducativo | None:
        return (
            self.db.query(ContenidoEducativo)
            .filter(ContenidoEducativo.id == uuid.UUID(contenido_id))
            .first()
        )

    def actualizar_estado(self, contenido: ContenidoEducativo,
                          estado: str, motivo: str = None,
                          informe_ia: str = None) -> ContenidoEducativo:
        contenido.estado = estado
        if motivo:
            contenido.motivo_rechazo = motivo
        if informe_ia:
            contenido.informe_ia = informe_ia
        self.db.commit()
        self.db.refresh(contenido)
        return contenido