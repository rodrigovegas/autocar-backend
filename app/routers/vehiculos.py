from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.vehiculo import (
    VehiculoCreateSchema,
    VehiculoUpdateSchema,
    VehiculoResponse
)
from app.services.vehiculo_service import VehiculoService
from app.models.usuario import Usuario

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])
vehiculo_service = VehiculoService()

@router.get("", response_model=List[VehiculoResponse])
def listar_vehiculos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos los vehículos activos del usuario autenticado."""
    vehiculos = vehiculo_service.obtener_vehiculos_usuario(
        db, str(current_user.id)
    )
    return [VehiculoResponse(
        id=str(v.id),
        marca=v.marca,
        modelo=v.modelo,
        anio=v.anio,
        kilometraje_actual=v.kilometraje_actual,
        activo=v.activo,
        fecha_registro=v.fecha_registro
    ) for v in vehiculos]

@router.post("", response_model=VehiculoResponse, status_code=201)
def registrar_vehiculo(
    datos: VehiculoCreateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra un nuevo vehículo para el usuario autenticado."""
    try:
        vehiculo = vehiculo_service.registrar_vehiculo(
            db,
            str(current_user.id),
            datos.marca,
            datos.modelo,
            datos.anio,
            datos.kilometraje_actual
        )
        return VehiculoResponse(
            id=str(vehiculo.id),
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            kilometraje_actual=vehiculo.kilometraje_actual,
            activo=vehiculo.activo,
            fecha_registro=vehiculo.fecha_registro
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(
    vehiculo_id: str,
    datos: VehiculoUpdateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza la información de un vehículo del usuario autenticado."""
    try:
        vehiculo = vehiculo_service.actualizar_vehiculo(
            db,
            vehiculo_id,
            str(current_user.id),
            datos.marca,
            datos.modelo,
            datos.anio,
            datos.kilometraje_actual
        )
        return VehiculoResponse(
            id=str(vehiculo.id),
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            kilometraje_actual=vehiculo.kilometraje_actual,
            activo=vehiculo.activo,
            fecha_registro=vehiculo.fecha_registro
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{vehiculo_id}", status_code=204)
def eliminar_vehiculo(
    vehiculo_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desactiva un vehículo del usuario autenticado."""
    try:
        vehiculo_service.eliminar_vehiculo(
            db,
            vehiculo_id,
            str(current_user.id)
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))