from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.schemas.taller import (
    TallerResumenResponse,
    TallerDetalleResponse,
    TallerPerfilUpdateSchema,
    ServicioEnTallerResponse
)
from app.services.taller_service import TallerService
from app.models.usuario import Usuario
from app.models.taller import Taller

router = APIRouter(prefix="/talleres", tags=["Talleres"])
taller_service = TallerService()

@router.get("", response_model=List[TallerResumenResponse])
def listar_talleres_activos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos los talleres activos con coordenadas geográficas."""
    talleres = taller_service.obtener_talleres_activos(db)
    return [TallerResumenResponse(
        id=str(t.id),
        nombre=t.nombre,
        especialidad=t.especialidad,
        direccion_texto=t.direccion_texto,
        telefono=t.telefono,
        latitud=t.latitud,
        longitud=t.longitud
    ) for t in talleres]

@router.get("/perfil", response_model=TallerResumenResponse)
def obtener_perfil_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Obtiene el perfil del taller autenticado."""
    return TallerResumenResponse(
        id=str(current_taller.id),
        nombre=current_taller.nombre,
        especialidad=current_taller.especialidad,
        direccion_texto=current_taller.direccion_texto,
        telefono=current_taller.telefono,
        latitud=current_taller.latitud,
        longitud=current_taller.longitud
    )

@router.get("/{taller_id}", response_model=TallerDetalleResponse)
def obtener_detalle_taller(
    taller_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna el detalle de un taller activo con sus servicios."""
    try:
        taller = taller_service.obtener_detalle_taller(db, taller_id)
        servicios = [ServicioEnTallerResponse(
            id=str(s.id),
            nombre=s.nombre_personalizado or s.tipo_mantenimiento.nombre,
            descripcion=s.descripcion_personalizada or s.tipo_mantenimiento.descripcion_base,
            tiempo_estimado_minutos=s.tiempo_estimado_minutos
        ) for s in taller.servicios if s.activo]

        return TallerDetalleResponse(
            id=str(taller.id),
            nombre=taller.nombre,
            especialidad=taller.especialidad,
            direccion_texto=taller.direccion_texto,
            telefono=taller.telefono,
            latitud=taller.latitud,
            longitud=taller.longitud,
            servicios=servicios
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/perfil", response_model=TallerResumenResponse)
def actualizar_perfil(
    datos: TallerPerfilUpdateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db)
):
    """Actualiza el perfil del taller autenticado."""
    try:
        taller = taller_service.actualizar_perfil(
            db, str(current_taller.id),
            datos.nombre, datos.especialidad,
            datos.direccion_texto, datos.telefono
        )
        return TallerResumenResponse(
            id=str(taller.id),
            nombre=taller.nombre,
            especialidad=taller.especialidad,
            direccion_texto=taller.direccion_texto,
            telefono=taller.telefono,
            latitud=taller.latitud,
            longitud=taller.longitud
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))