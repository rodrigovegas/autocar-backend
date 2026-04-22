from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.asistente import ConsultaAsistenteSchema, RespuestaAsistenteSchema
from app.services.gemini_service import GeminiService
from app.models.usuario import Usuario
from app.core.dependencies import get_current_taller
from app.schemas.asistente import ConsultaAsistenteSchema, RespuestaAsistenteSchema, GenerarTemplateSchema
from app.models.taller import Taller

router = APIRouter(prefix="/asistente", tags=["Asistente IA"])
gemini_service = GeminiService()

@router.post("/consulta", response_model=RespuestaAsistenteSchema)
def consultar_asistente(
    datos: ConsultaAsistenteSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        respuesta = gemini_service.generar_respuesta(
            datos.mensaje,
            datos.historial
        )
        return RespuestaAsistenteSchema(respuesta=respuesta)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    from app.schemas.asistente import GenerarTemplateSchema

@router.post("/generar-template")
def generar_template_mantenimiento(
    datos: GenerarTemplateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Genera un template de formulario basado en la descripción del usuario."""
    try:
        template = gemini_service.generar_template_formulario(
            datos.descripcion
        )
        return {"template": template}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    
@router.post("/generar-template")
def generar_template_mantenimiento(
    datos: GenerarTemplateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Genera un template de formulario basado en la descripción del usuario."""
    try:
        template = gemini_service.generar_template_formulario(
            datos.descripcion
        )
        return {"template": template}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )    
