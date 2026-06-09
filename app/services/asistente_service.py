from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.contenido_educativo import ContenidoEducativo
from app.models.vehiculo import Vehiculo


def buscar_contenido_relevante(db: Session, mensaje: str) -> list:
    """Busca contenidos educativos publicados relevantes al mensaje."""
    palabras = [p for p in mensaje.lower().split() if len(p) > 3]
    if not palabras:
        return []

    filtros = []
    for palabra in palabras[:5]:
        filtros.append(ContenidoEducativo.titulo.ilike(f"%{palabra}%"))
        filtros.append(ContenidoEducativo.cuerpo.ilike(f"%{palabra}%"))
        filtros.append(ContenidoEducativo.categoria.ilike(f"%{palabra}%"))

    contenidos = db.query(ContenidoEducativo).filter(
        ContenidoEducativo.estado == "publicado",
        or_(*filtros)
    ).limit(3).all()

    return [
        {
            "titulo": c.titulo,
            "cuerpo": c.cuerpo,
            "categoria": c.categoria,
        }
        for c in contenidos
    ]


def obtener_vehiculo(db: Session, vehiculo_id: str, usuario_id: str) -> dict | None:
    """Obtiene un vehículo específico del usuario."""
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id,
        Vehiculo.usuario_id == usuario_id,
        Vehiculo.activo == True
    ).first()

    if not vehiculo:
        return None

    return {
        "marca": vehiculo.marca,
        "modelo": vehiculo.modelo,
        "anio": vehiculo.anio,
        "kilometraje_actual": vehiculo.kilometraje_actual,
        "tipo_combustible": vehiculo.tipo_combustible,
    }
