from sqlalchemy.orm import Session
from app.repositories.taller_repository import TallerRepository
from app.repositories.disponibilidad_repository import DisponibilidadRepository

taller_repo = TallerRepository()
disponibilidad_repo = DisponibilidadRepository()


class TallerService:

    def obtener_talleres_activos(self, db: Session):
        return taller_repo.obtener_activos(db)

    def obtener_detalle_taller(self, db: Session, taller_id: str):
        taller = taller_repo.obtener_activo_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado o no activo")
        return taller

    def actualizar_perfil(
        self,
        db: Session,
        taller_id: str,
        nombre: str = None,
        direccion_texto: str = None,
        telefono: str = None,
    ):
        taller = taller_repo.obtener_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado")
        return taller_repo.actualizar_perfil(
            db, taller, nombre, direccion_texto, telefono
        )

    def obtener_disponibilidad_taller(self, db: Session, taller_id: str):
        return disponibilidad_repo.obtener_por_taller(db, taller_id)

    def obtener_disponibilidad_para_reserva(self, db: Session, taller_id: str):
        taller = taller_repo.obtener_activo_por_id(db, taller_id)
        if not taller:
            raise ValueError("Taller no encontrado o no activo")
        return disponibilidad_repo.obtener_disponible_por_taller(db, taller_id)

    def crear_disponibilidad(
        self, db: Session, taller_id: str,
        fecha, hora_inicio, hora_fin, cupos_totales: int,
    ):
        if cupos_totales <= 0:
            raise ValueError("El número de cupos debe ser mayor a cero")
        if disponibilidad_repo.verificar_duplicado(
            db, taller_id, fecha, hora_inicio, hora_fin
        ):
            raise ValueError(
                "Ya existe una franja horaria configurada para esa fecha y horario"
            )
        return disponibilidad_repo.crear(
            db, taller_id, fecha, hora_inicio, hora_fin, cupos_totales
        )

    def actualizar_estado_disponibilidad(
        self, db: Session, disponibilidad_id: str,
        taller_id: str, activo: bool,
    ):
        disponibilidad = disponibilidad_repo.obtener_por_id(db, disponibilidad_id)
        if not disponibilidad:
            raise ValueError("Franja horaria no encontrada")
        if str(disponibilidad.taller_id) != str(taller_id):
            raise PermissionError(
                "No tiene permisos para modificar esta franja horaria"
            )
        return disponibilidad_repo.actualizar_estado(db, disponibilidad, activo)