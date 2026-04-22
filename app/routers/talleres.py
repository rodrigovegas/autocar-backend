from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user, get_current_taller
from app.schemas.taller import (
    TallerResumenResponse,
    TallerDetalleResponse,
    TallerPerfilUpdateSchema,
    ServicioEnTallerResponse,
    ProponerTipoSchema,
    AgregarServicioSchema,
)
from app.services.taller_service import TallerService
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.reserva import Reserva
from app.models.mantenimiento import Mantenimiento
from app.models.servicio_taller import ServicioTaller
from app.models.tipo_mantenimiento import TipoMantenimiento
import uuid

router = APIRouter(prefix="/talleres", tags=["Talleres"])
taller_service = TallerService()


def _calificacion_taller(db: Session, taller_id) -> tuple:
    """Devuelve (promedio, total) de calificaciones para un taller."""
    res = db.query(
        func.avg(Reserva.calificacion),
        func.count(Reserva.calificacion),
    ).filter(
        Reserva.taller_id == taller_id,
        Reserva.calificacion.isnot(None),
    ).first()
    promedio = round(float(res[0]), 1) if res and res[0] else None
    total = res[1] if res else 0
    return promedio, total


def _taller_resumen(t: Taller, promedio=None, total=0) -> TallerResumenResponse:
    return TallerResumenResponse(
        id=str(t.id),
        nombre=t.nombre,
        especialidad_nombre=t.especialidad_rel.nombre if t.especialidad_rel else None,
        direccion_texto=t.direccion_texto,
        telefono=t.telefono,
        latitud=t.latitud,
        longitud=t.longitud,
        calificacion_promedio=promedio,
        total_calificaciones=total,
    )


# ─── ESTADÍSTICAS ─────────────────────────────────────────────

@router.get("/estadisticas")
def obtener_estadisticas_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    tid = current_taller.id
    pendientes = db.query(func.count(Reserva.id)).filter(
        Reserva.taller_id == tid, Reserva.estado == "pendiente"
    ).scalar() or 0
    confirmadas = db.query(func.count(Reserva.id)).filter(
        Reserva.taller_id == tid, Reserva.estado == "confirmada"
    ).scalar() or 0
    rechazadas = db.query(func.count(Reserva.id)).filter(
        Reserva.taller_id == tid, Reserva.estado == "rechazada"
    ).scalar() or 0
    mantenimientos = db.query(func.count(Mantenimiento.id)).filter(
        Mantenimiento.taller_id == tid
    ).scalar() or 0
    clientes = db.query(func.count(distinct(Reserva.usuario_id))).filter(
        Reserva.taller_id == tid,
        Reserva.estado.in_(["confirmada", "completada"]),
    ).scalar() or 0
    return {
        "reservas_pendientes": pendientes,
        "reservas_confirmadas": confirmadas,
        "reservas_rechazadas": rechazadas,
        "mantenimientos_completados": mantenimientos,
        "clientes_atendidos": clientes,
    }


# ─── TIPOS DISPONIBLES — toda la lista sin filtro de especialidad ─

@router.get("/tipos-mantenimiento-disponibles")
def listar_tipos_disponibles(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    ids_existentes = {
        str(s.tipo_mantenimiento_id)
        for s in db.query(ServicioTaller)
        .filter(ServicioTaller.taller_id == current_taller.id)
        .all()
    }
    tipos = (
        db.query(TipoMantenimiento)
        .filter(
            TipoMantenimiento.estado == "aprobado",
            TipoMantenimiento.activo == True,
        )
        .order_by(TipoMantenimiento.nombre)
        .all()
    )
    return [
        {
            "id": str(t.id),
            "nombre": t.nombre,
            "ya_agregado": str(t.id) in ids_existentes,
        }
        for t in tipos
    ]


@router.post("/tipos-mantenimiento", status_code=201)
def proponer_tipo(
    datos: ProponerTipoSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    existente = db.query(TipoMantenimiento).filter(
        TipoMantenimiento.nombre.ilike(datos.nombre.strip())
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un tipo con ese nombre")
    tipo = TipoMantenimiento(
        nombre=datos.nombre.strip(),
        descripcion_base=datos.descripcion_base.strip(),
        estado="pendiente",
        activo=False,
    )
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return {
        "id": str(tipo.id),
        "nombre": tipo.nombre,
        "estado": tipo.estado,
        "mensaje": "Propuesta enviada. El administrador la revisará pronto.",
    }


@router.get("/mis-propuestas")
def listar_mis_propuestas(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    # Sin taller_creador_id, usamos nombre buscado por el taller
    # Retornamos todos los tipos pendientes para que el taller vea el estado
    tipos = (
        db.query(TipoMantenimiento)
        .filter(TipoMantenimiento.estado.in_(["pendiente", "rechazado"]))
        .order_by(TipoMantenimiento.nombre)
        .all()
    )
    return [
        {
            "id": str(t.id),
            "nombre": t.nombre,
            "descripcion_base": t.descripcion_base,
            "estado": t.estado,
        }
        for t in tipos
    ]


# ─── SERVICIOS DEL TALLER ─────────────────────────────────────

@router.get("/mis-servicios")
def listar_mis_servicios(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    servicios = (
        db.query(ServicioTaller)
        .filter(ServicioTaller.taller_id == current_taller.id)
        .all()
    )
    return [
        {
            "id": str(s.id),
            "tipo_mantenimiento_id": str(s.tipo_mantenimiento_id),
            "tipo_nombre": s.tipo_mantenimiento.nombre,
            "tiempo_estimado_minutos": s.tiempo_estimado_minutos,
            "activo": s.activo,
        }
        for s in servicios
    ]


@router.post("/mis-servicios/{tipo_id}", status_code=201)
def agregar_servicio(
    tipo_id: str,
    datos: AgregarServicioSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    tipo = db.query(TipoMantenimiento).filter(
        TipoMantenimiento.id == uuid.UUID(tipo_id),
        TipoMantenimiento.estado == "aprobado",
    ).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")

    existente = db.query(ServicioTaller).filter(
        ServicioTaller.taller_id == current_taller.id,
        ServicioTaller.tipo_mantenimiento_id == uuid.UUID(tipo_id),
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya ofreces este servicio")

    servicio = ServicioTaller(
        taller_id=current_taller.id,
        tipo_mantenimiento_id=uuid.UUID(tipo_id),
        tiempo_estimado_minutos=datos.tiempo_estimado_minutos,
        activo=True,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return {"id": str(servicio.id), "activo": servicio.activo}


@router.patch("/mis-servicios/{servicio_id}/toggle")
def toggle_servicio(
    servicio_id: str,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    servicio = db.query(ServicioTaller).filter(
        ServicioTaller.id == uuid.UUID(servicio_id),
        ServicioTaller.taller_id == current_taller.id,
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    servicio.activo = not servicio.activo
    db.commit()
    db.refresh(servicio)
    return {"id": str(servicio.id), "activo": servicio.activo}


@router.delete("/mis-servicios/{servicio_id}", status_code=204)
def eliminar_servicio(
    servicio_id: str,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    servicio = db.query(ServicioTaller).filter(
        ServicioTaller.id == uuid.UUID(servicio_id),
        ServicioTaller.taller_id == current_taller.id,
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()


# ─── ENDPOINTS PÚBLICOS ───────────────────────────────────────

@router.get("", response_model=List[TallerResumenResponse])
def listar_talleres_activos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    talleres = taller_service.obtener_talleres_activos(db)
    resultado = []
    for t in talleres:
        promedio, total = _calificacion_taller(db, t.id)
        resultado.append(_taller_resumen(t, promedio, total))
    return resultado


@router.get("/perfil", response_model=TallerResumenResponse)
def obtener_perfil_taller(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    return _taller_resumen(current_taller)


@router.get("/mi-calificacion")
def obtener_mi_calificacion(
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    """Retorna el promedio y total de calificaciones del taller autenticado."""
    promedio = db.query(func.avg(Reserva.calificacion)).filter(
        Reserva.taller_id == current_taller.id,
        Reserva.calificacion.isnot(None),
    ).scalar()
    total = db.query(func.count(Reserva.calificacion)).filter(
        Reserva.taller_id == current_taller.id,
        Reserva.calificacion.isnot(None),
    ).scalar() or 0
    return {
        "promedio": round(float(promedio), 1) if promedio else None,
        "total_calificaciones": total,
    }


@router.get("/{taller_id}", response_model=TallerDetalleResponse)
def obtener_detalle_taller(
    taller_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        taller = taller_service.obtener_detalle_taller(db, taller_id)
        servicios = [
            ServicioEnTallerResponse(
                id=str(s.id),
                nombre=s.tipo_mantenimiento.nombre,
                descripcion=s.tipo_mantenimiento.descripcion_base,
                tiempo_estimado_minutos=s.tiempo_estimado_minutos,
            )
            for s in taller.servicios
            if s.activo
        ]
        promedio, total = _calificacion_taller(db, taller.id)
        return TallerDetalleResponse(
            id=str(taller.id),
            nombre=taller.nombre,
            especialidad_nombre=taller.especialidad_rel.nombre
            if taller.especialidad_rel else None,
            direccion_texto=taller.direccion_texto,
            telefono=taller.telefono,
            latitud=taller.latitud,
            longitud=taller.longitud,
            servicios=servicios,
            calificacion_promedio=promedio,
            total_calificaciones=total,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/perfil", response_model=TallerResumenResponse)
def actualizar_perfil(
    datos: TallerPerfilUpdateSchema,
    current_taller: Taller = Depends(get_current_taller),
    db: Session = Depends(get_db),
):
    try:
        taller = taller_service.actualizar_perfil(
            db, str(current_taller.id),
            datos.nombre, datos.direccion_texto, datos.telefono,
        )
        return _taller_resumen(taller)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))