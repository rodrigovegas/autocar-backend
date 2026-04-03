from sqlalchemy.orm import Session
from app.repositories.taller_repository import TallerRepository
from app.repositories.disponibilidad_repository import DisponibilidadRepository

taller_repo = TallerRepository()
disponibilidad_repo = DisponibilidadRepository()

class TallerService:

    def obtener_talleres_activos(self, db: Session):
        """Retorna todos los talleres activos con coordenadas."""
        return taller_repo.obtener_activos(db)

    def obtener_detalle_taller(self, db: Session, taller_id: str):
        """Retorna el detalle de un taller activo con sus servicios."""
        taller = taller_repo.obtener_activo_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado o no activo")
        return taller

    def actualizar_perfil(self, db: Session, taller_id: str,
                          nombre: str = None, especialidad: str = None,
                          direccion_texto: str = None, telefono: str = None):
        """Actualiza el perfil del taller autenticado."""
        taller = taller_repo.obtener_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado")
        return taller_repo.actualizar_perfil(
            db, taller, nombre, especialidad, direccion_texto, telefono
        )

    def obtener_disponibilidad_taller(self, db: Session, taller_id: str):
        """Retorna toda la disponibilidad configurada por el taller."""
        return disponibilidad_repo.obtener_por_taller(db, taller_id)

    def obtener_disponibilidad_para_reserva(self, db: Session, taller_id: str):
        """Retorna franjas disponibles para que el usuario pueda reservar."""
        taller = taller_repo.obtener_activo_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado o no activo")
        return disponibilidad_repo.obtener_disponible_por_taller(db, taller_id)

    def crear_disponibilidad(self, db: Session, taller_id: str,
                             fecha, hora_inicio, hora_fin, cupos_totales: int):
        """Registra una nueva franja horaria de disponibilidad."""
        if cupos_totales <= 0:
            raise ValueError("El número de cupos debe ser mayor a cero")

        # Verifica que no exista una franja duplicada
        if disponibilidad_repo.verificar_duplicado(
            db, taller_id, fecha, hora_inicio, hora_fin
        ):
            raise ValueError(
                "Ya existe una franja horaria configurada para esa fecha y horario"
            )

        return disponibilidad_repo.crear(
            db, taller_id, fecha, hora_inicio, hora_fin, cupos_totales
        )

    def actualizar_estado_disponibilidad(self, db: Session,
                                         disponibilidad_id: str,
                                         taller_id: str, activo: bool):
        """Activa o desactiva una franja horaria del taller."""
        disponibilidad = disponibilidad_repo.obtener_por_id(db, disponibilidad_id)
        if not disponibilidad:
            raise ValueError("Franja horaria no encontrada")

        # RN-19: Solo el taller dueño puede modificar su disponibilidad
        if str(disponibilidad.taller_id) != str(taller_id):
            raise PermissionError(
                "No tiene permisos para modificar esta franja horaria"
            )
        return disponibilidad_repo.actualizar_estado(db, disponibilidad, activo)