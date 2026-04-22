from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.models.administrador import Administrador
from app.models.especialidad import Especialidad
import uuid

router = APIRouter(tags=["Especialidades"])


# ── Público — para el dropdown de registro ────────────────────

@router.get("/especialidades")
def listar_especialidades(db: Session = Depends(get_db)):
    """Lista especialidades activas. Sin autenticación — usado en registro."""
    return [
        {"id": str(e.id), "nombre": e.nombre}
        for e in db.query(Especialidad)
        .filter(Especialidad.activo == True)
        .order_by(Especialidad.nombre)
        .all()
    ]


# ── Admin — gestión de especialidades ────────────────────────

@router.get("/admin/especialidades")
def listar_todas_especialidades(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lista todas las especialidades (activas e inactivas) para el admin."""
    return [
        {"id": str(e.id), "nombre": e.nombre, "activo": e.activo}
        for e in db.query(Especialidad).order_by(Especialidad.nombre).all()
    ]


@router.post("/admin/especialidades", status_code=201)
def crear_especialidad(
    datos: dict,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre es requerido")

    existente = db.query(Especialidad).filter(
        Especialidad.nombre.ilike(nombre)
    ).first()
    if existente:
        raise HTTPException(
            status_code=400, detail="Ya existe una especialidad con ese nombre"
        )

    esp = Especialidad(nombre=nombre, activo=True)
    db.add(esp)
    db.commit()
    db.refresh(esp)
    return {"id": str(esp.id), "nombre": esp.nombre, "activo": esp.activo}


@router.patch("/admin/especialidades/{especialidad_id}/toggle")
def toggle_especialidad(
    especialidad_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    esp = db.query(Especialidad).filter(
        Especialidad.id == uuid.UUID(especialidad_id)
    ).first()
    if not esp:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")

    esp.activo = not esp.activo
    db.commit()
    db.refresh(esp)
    return {"id": str(esp.id), "nombre": esp.nombre, "activo": esp.activo}