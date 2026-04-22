from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime
import uuid

from app.models.taller import Taller
from app.models.usuario import Usuario
from app.models.contenido_educativo import ContenidoEducativo
from app.models.reserva import Reserva
from app.models.mantenimiento import Mantenimiento
from app.models.tipo_mantenimiento import TipoMantenimiento


class AdminService:

    # ─── ESTADÍSTICAS ─────────────────────────────────────────

    def obtener_estadisticas(self, db: Session, ahora: datetime) -> dict:
        total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0
        talleres_activos = (
            db.query(func.count(Taller.id))
            .filter(Taller.estado == "activo")
            .scalar() or 0
        )
        reservas_mes = (
            db.query(func.count(Reserva.id))
            .filter(
                extract("month", Reserva.fecha_creacion) == ahora.month,
                extract("year", Reserva.fecha_creacion) == ahora.year,
            )
            .scalar() or 0
        )
        mantenimientos_completados = (
            db.query(func.count(Mantenimiento.id)).scalar() or 0
        )
        return {
            "total_usuarios": total_usuarios,
            "talleres_activos": talleres_activos,
            "reservas_mes": reservas_mes,
            "mantenimientos_completados": mantenimientos_completados,
        }

    # ─── TALLERES ────────────────────────────────────────────

    def listar_talleres(self, db: Session) -> List[Taller]:
        return db.query(Taller).order_by(Taller.fecha_registro.desc()).all()

    def activar_taller(self, db: Session, taller_id: str, latitud, longitud) -> Taller:
        taller = db.query(Taller).filter(Taller.id == uuid.UUID(taller_id)).first()
        if not taller:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        taller.estado = "activo"
        taller.latitud = latitud
        taller.longitud = longitud
        db.commit()
        db.refresh(taller)
        return taller

    def desactivar_taller(self, db: Session, taller_id: str) -> Taller:
        taller = db.query(Taller).filter(Taller.id == uuid.UUID(taller_id)).first()
        if not taller:
            raise HTTPException(status_code=404, detail="Taller no encontrado")
        taller.estado = "inactivo"
        db.commit()
        db.refresh(taller)
        return taller

    # ─── USUARIOS ────────────────────────────────────────────

    def listar_usuarios(self, db: Session) -> List[Usuario]:
        return db.query(Usuario).order_by(Usuario.fecha_registro.desc()).all()

    def toggle_usuario(self, db: Session, usuario_id: str, activo: bool) -> Usuario:
        usuario = db.query(Usuario).filter(
            Usuario.id == uuid.UUID(usuario_id)
        ).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        usuario.activo = activo
        db.commit()
        db.refresh(usuario)
        return usuario

    # ─── CONTENIDO EDUCATIVO ─────────────────────────────────

    def listar_contenidos_pendientes(self, db: Session) -> List[ContenidoEducativo]:
        return (
            db.query(ContenidoEducativo)
            .filter(ContenidoEducativo.estado == "pendiente")
            .order_by(ContenidoEducativo.fecha_publicacion.asc())
            .all()
        )

    def listar_todos_contenidos(self, db: Session) -> List[ContenidoEducativo]:
        return (
            db.query(ContenidoEducativo)
            .order_by(ContenidoEducativo.fecha_publicacion.desc())
            .all()
        )

    def aprobar_contenido(self, db: Session, contenido_id: str) -> ContenidoEducativo:
        contenido = db.query(ContenidoEducativo).filter(
            ContenidoEducativo.id == uuid.UUID(contenido_id)
        ).first()
        if not contenido:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        contenido.estado = "publicado"
        db.commit()
        db.refresh(contenido)
        return contenido

    def rechazar_contenido(
        self, db: Session, contenido_id: str, motivo: str
    ) -> ContenidoEducativo:
        contenido = db.query(ContenidoEducativo).filter(
            ContenidoEducativo.id == uuid.UUID(contenido_id)
        ).first()
        if not contenido:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        contenido.estado = "rechazado"
        contenido.motivo_rechazo = motivo
        db.commit()
        db.refresh(contenido)
        return contenido

    def eliminar_contenido(self, db: Session, contenido_id: str) -> None:
        contenido = db.query(ContenidoEducativo).filter(
            ContenidoEducativo.id == uuid.UUID(contenido_id)
        ).first()
        if not contenido:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        db.delete(contenido)
        db.commit()

    # ─── TIPOS DE MANTENIMIENTO ───────────────────────────────

    def listar_tipos(self, db: Session) -> List[TipoMantenimiento]:
        return (
            db.query(TipoMantenimiento)
            .order_by(TipoMantenimiento.estado, TipoMantenimiento.nombre)
            .all()
        )

    def crear_tipo(
        self, db: Session, nombre: str, descripcion: str
    ) -> TipoMantenimiento:
        nombre = nombre.strip()
        existente = db.query(TipoMantenimiento).filter(
            TipoMantenimiento.nombre.ilike(nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=400, detail="Ya existe un tipo con ese nombre"
            )
        tipo = TipoMantenimiento(
            nombre=nombre,
            descripcion_base=descripcion.strip(),
            estado="aprobado",
            activo=True,
        )
        db.add(tipo)
        db.commit()
        db.refresh(tipo)
        return tipo

    def aprobar_tipo(self, db: Session, tipo_id: str) -> TipoMantenimiento:
        tipo = db.query(TipoMantenimiento).filter(
            TipoMantenimiento.id == uuid.UUID(tipo_id)
        ).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo no encontrado")
        tipo.estado = "aprobado"
        tipo.activo = True
        db.commit()
        db.refresh(tipo)
        return tipo

    def rechazar_tipo(self, db: Session, tipo_id: str) -> TipoMantenimiento:
        tipo = db.query(TipoMantenimiento).filter(
            TipoMantenimiento.id == uuid.UUID(tipo_id)
        ).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo no encontrado")
        tipo.estado = "rechazado"
        tipo.activo = False
        db.commit()
        db.refresh(tipo)
        return tipo
