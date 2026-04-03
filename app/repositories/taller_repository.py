from sqlalchemy.orm import Session
from app.models.taller import Taller

class TallerRepository:

    def obtener_activos(self, db: Session):
        """Obtiene todos los talleres activos con coordenadas asignadas."""
        return db.query(Taller).filter(
            Taller.estado == "activo",
            Taller.latitud.isnot(None),
            Taller.longitud.isnot(None)
        ).all()

    def obtener_por_id(self, db: Session, taller_id: str):
        """Obtiene un taller por su ID."""
        return db.query(Taller).filter(
            Taller.id == taller_id
        ).first()

    def obtener_activo_por_id(self, db: Session, taller_id: str):
        """Obtiene un taller activo por su ID."""
        return db.query(Taller).filter(
            Taller.id == taller_id,
            Taller.estado == "activo"
        ).first()

    def actualizar_perfil(self, db: Session, taller: Taller,
                          nombre: str = None, especialidad: str = None,
                          direccion_texto: str = None, telefono: str = None):
        """Actualiza el perfil del taller."""
        if nombre is not None:
            taller.nombre = nombre
        if especialidad is not None:
            taller.especialidad = especialidad
        if direccion_texto is not None:
            taller.direccion_texto = direccion_texto
        if telefono is not None:
            taller.telefono = telefono
        db.commit()
        db.refresh(taller)
        return taller