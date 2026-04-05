from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.asistente import ConsultaAsistenteSchema, RespuestaAsistenteSchema
from app.services.gemini_service import GeminiService
from app.models.usuario import Usuario

router = APIRouter(prefix="/asistente", tags=["Asistente IA"])
gemini_service = GeminiService()

@router.post("/consulta", response_model=RespuestaAsistenteSchema)
def consultar_asistente(
    datos: ConsultaAsistenteSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint del asistente conversacional educativo basado en Gemini.
    El historial de conversación se mantiene solo en la sesión del cliente.
    """
    try:
        respuesta = gemini_service.generar_respuesta(
            datos.mensaje,
            datos.historial
        )
        return RespuestaAsistenteSchema(respuesta=respuesta)
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail="El asistente no está disponible en este momento"
        )