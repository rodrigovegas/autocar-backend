from sqlalchemy.orm import Session
from app.repositories.educativo_repository import EducativoRepository
from app.schemas.educativo import ContenidoCreateSchema
from app.services.gemini_service import GeminiService
from fastapi import HTTPException

class EducativoService:

    def __init__(self, db: Session):
        self.repo = EducativoRepository(db)
        self.gemini = GeminiService()

    def publicar_contenido(self, taller_id: str,
                           datos: ContenidoCreateSchema):
        try:
            informe = self.gemini.validar_contenido_educativo(
                datos.titulo, datos.cuerpo, datos.categoria
            )
        except Exception:
            informe = "No se pudo validar con IA automáticamente."

        contenido = self.repo.crear(taller_id, datos)
        contenido.informe_ia = informe
        self.repo.db.commit()
        self.repo.db.refresh(contenido)
        return contenido

    def listar_publicados(self):
        return self.repo.listar_publicados()

    def listar_por_taller(self, taller_id: str):
        return self.repo.listar_por_taller(taller_id)

    def listar_pendientes(self):
        return self.repo.listar_pendientes()

    def aprobar(self, contenido_id: str, admin_id: str):
        contenido = self.repo.obtener_por_id(contenido_id)
        if not contenido:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        if contenido.estado != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden aprobar contenidos pendientes")
        return self.repo.actualizar_estado(contenido, "publicado")

    def rechazar(self, contenido_id: str, motivo: str):
        contenido = self.repo.obtener_por_id(contenido_id)
        if not contenido:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        return self.repo.actualizar_estado(contenido, "rechazado", motivo=motivo)