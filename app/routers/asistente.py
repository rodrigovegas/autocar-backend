from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.schemas.asistente import ConsultaAsistenteSchema, RespuestaAsistenteSchema, GenerarTemplateSchema
from app.services.gemini_service import GeminiService
from app.services.asistente_service import buscar_contenido_relevante, obtener_vehiculo
from app.models.usuario import Usuario
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
        vehiculo = None
        if datos.vehiculo_id:
            vehiculo = obtener_vehiculo(db, datos.vehiculo_id, str(current_user.id))

        contenidos = buscar_contenido_relevante(db, datos.mensaje)

        respuesta = gemini_service.generar_respuesta_con_contexto(
            mensaje=datos.mensaje,
            historial=datos.historial,
            vehiculo=vehiculo,
            contenidos_educativos=contenidos
        )
        return RespuestaAsistenteSchema(respuesta=respuesta)
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
        template = gemini_service.generar_template_formulario(datos.descripcion)
        return {"template": template}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
