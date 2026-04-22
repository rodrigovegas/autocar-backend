from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.models.administrador import Administrador
from app.models.taller import Taller
from app.models.tipo_mantenimiento import TipoMantenimiento
from app.schemas.admin import (
    TallerAdminResponse,
    ActivarTallerSchema,
    UsuarioAdminResponse,
    ContenidoAdminResponse,
    RechazarContenidoSchema,
    TipoMantenimientoAdminResponse,
    CrearTipoMantenimientoSchema,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Administración"])
admin_service = AdminService()


# ─── HELPERS ─────────────────────────────────────────────────

def _taller_to_response(t: Taller) -> TallerAdminResponse:
    return TallerAdminResponse(
        id=t.id,
        nombre=t.nombre,
        especialidad_nombre=t.especialidad_rel.nombre if t.especialidad_rel else None,
        direccion_texto=t.direccion_texto,
        telefono=t.telefono,
        correo=t.correo,
        estado=t.estado,
        latitud=float(t.latitud) if t.latitud else None,
        longitud=float(t.longitud) if t.longitud else None,
        fecha_registro=t.fecha_registro,
    )


def _tipo_to_response(t: TipoMantenimiento) -> TipoMantenimientoAdminResponse:
    return TipoMantenimientoAdminResponse(
        id=t.id,
        nombre=t.nombre,
        descripcion_base=t.descripcion_base,
        estado=t.estado,
    )


# ─── ESTADÍSTICAS ─────────────────────────────────────────────

@router.get("/estadisticas")
def obtener_estadisticas(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.obtener_estadisticas(db, datetime.now())


# ─── TALLERES ────────────────────────────────────────────────

@router.get("/talleres", response_model=List[TallerAdminResponse])
def listar_talleres(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return [_taller_to_response(t) for t in admin_service.listar_talleres(db)]


@router.patch("/talleres/{taller_id}/activar", response_model=TallerAdminResponse)
def activar_taller(
    taller_id: str,
    datos: ActivarTallerSchema,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _taller_to_response(
        admin_service.activar_taller(db, taller_id, datos.latitud, datos.longitud)
    )


@router.patch("/talleres/{taller_id}/desactivar", response_model=TallerAdminResponse)
def desactivar_taller(
    taller_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _taller_to_response(admin_service.desactivar_taller(db, taller_id))


# ─── USUARIOS ────────────────────────────────────────────────

@router.get("/usuarios", response_model=List[UsuarioAdminResponse])
def listar_usuarios(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.listar_usuarios(db)


@router.patch("/usuarios/{usuario_id}/desactivar", response_model=UsuarioAdminResponse)
def desactivar_usuario(
    usuario_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.toggle_usuario(db, usuario_id, activo=False)


@router.patch("/usuarios/{usuario_id}/activar", response_model=UsuarioAdminResponse)
def activar_usuario(
    usuario_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.toggle_usuario(db, usuario_id, activo=True)


# ─── CONTENIDO EDUCATIVO ─────────────────────────────────────

@router.get("/contenidos", response_model=List[ContenidoAdminResponse])
def listar_contenidos_pendientes(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.listar_contenidos_pendientes(db)


@router.get("/contenidos/todos", response_model=List[ContenidoAdminResponse])
def listar_todos_los_contenidos(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lista todos los contenidos educativos sin filtrar por estado."""
    return admin_service.listar_todos_contenidos(db)


@router.delete("/contenidos/{contenido_id}", status_code=204)
def eliminar_contenido(
    contenido_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Elimina un contenido educativo. Solo el administrador puede hacerlo."""
    admin_service.eliminar_contenido(db, contenido_id)


@router.patch("/contenidos/{contenido_id}/aprobar", response_model=ContenidoAdminResponse)
def aprobar_contenido(
    contenido_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.aprobar_contenido(db, contenido_id)


@router.patch("/contenidos/{contenido_id}/rechazar", response_model=ContenidoAdminResponse)
def rechazar_contenido(
    contenido_id: str,
    datos: RechazarContenidoSchema,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.rechazar_contenido(db, contenido_id, datos.motivo)


# ─── TIPOS DE MANTENIMIENTO ───────────────────────────────────

@router.get("/tipos-mantenimiento", response_model=List[TipoMantenimientoAdminResponse])
def listar_tipos(
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lista TODOS los tipos — aprobados, pendientes y rechazados."""
    return [_tipo_to_response(t) for t in admin_service.listar_tipos(db)]


@router.post("/tipos-mantenimiento", status_code=201)
def crear_tipo_mantenimiento(
    datos: CrearTipoMantenimientoSchema,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin crea un tipo directamente — queda aprobado."""
    return _tipo_to_response(
        admin_service.crear_tipo(db, datos.nombre, datos.descripcion_base)
    )


@router.patch(
    "/tipos-mantenimiento/{tipo_id}/aprobar",
    response_model=TipoMantenimientoAdminResponse,
)
def aprobar_tipo(
    tipo_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _tipo_to_response(admin_service.aprobar_tipo(db, tipo_id))


@router.patch(
    "/tipos-mantenimiento/{tipo_id}/rechazar",
    response_model=TipoMantenimientoAdminResponse,
)
def rechazar_tipo(
    tipo_id: str,
    current_admin: Administrador = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _tipo_to_response(admin_service.rechazar_tipo(db, tipo_id))
