from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.administrador import Administrador

class AuthRepository:

    def obtener_usuario_por_firebase_uid(self, db: Session, firebase_uid: str):
        return db.query(Usuario).filter(Usuario.firebase_uid == firebase_uid).first()

    def obtener_taller_por_firebase_uid(self, db: Session, firebase_uid: str):
        return db.query(Taller).filter(Taller.firebase_uid == firebase_uid).first()

    def obtener_admin_por_firebase_uid(self, db: Session, firebase_uid: str):
        return db.query(Administrador).filter(Administrador.firebase_uid == firebase_uid).first()

    def obtener_usuario_por_correo(self, db: Session, correo: str):
        return db.query(Usuario).filter(Usuario.correo == correo).first()

    def obtener_taller_por_correo(self, db: Session, correo: str):
        return db.query(Taller).filter(Taller.correo == correo).first()

    def crear_usuario(self, db: Session, firebase_uid: str, nombre_completo: str, correo: str):
        usuario = Usuario(
            firebase_uid=firebase_uid,
            nombre_completo=nombre_completo,
            correo=correo
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def crear_taller(self, db: Session, firebase_uid: str, nombre: str,
                     especialidad: str, direccion_texto: str,
                     telefono: str, correo: str):
        taller = Taller(
            firebase_uid=firebase_uid,
            nombre=nombre,
            especialidad_id=especialidad,
            direccion_texto=direccion_texto,
            telefono=telefono,
            correo=correo,
            estado="pendiente"
        )
        db.add(taller)
        db.commit()
        db.refresh(taller)
        return taller
