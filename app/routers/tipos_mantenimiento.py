from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.tipo_mantenimiento import TipoMantenimiento
from app.models.usuario import Usuario

router = APIRouter(prefix="/tipos-mantenimiento", tags=["Tipos de Mantenimiento"])


class TipoMantenimientoPublicResponse(BaseModel):
    id: str
    nombre: str
    intervalo_km: Optional[int]
    intervalo_dias: Optional[int]


@router.get("", response_model=List[TipoMantenimientoPublicResponse])
def listar_tipos_mantenimiento(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista tipos de mantenimiento aprobados y activos para el dropdown del usuario."""
    tipos = (
        db.query(TipoMantenimiento)
        .filter(
            TipoMantenimiento.activo == True,
            TipoMantenimiento.estado == "aprobado",
        )
        .order_by(TipoMantenimiento.nombre)
        .all()
    )
    return [
        TipoMantenimientoPublicResponse(
            id=str(t.id),
            nombre=t.nombre,
            intervalo_km=t.intervalo_km,
            intervalo_dias=t.intervalo_dias,
        )
        for t in tipos
    ]
