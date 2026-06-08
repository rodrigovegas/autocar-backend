import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from app.services.vehiculo_service import VehiculoService


@pytest.fixture
def service():
    return VehiculoService()


def test_obtener_vehiculos_filtra_por_usuario(
    service, mock_db_session, vehiculo_fake, mocker,
):
    usuario_id = str(uuid.uuid4())
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_usuario.return_value = [vehiculo_fake]

    result = service.obtener_vehiculos_usuario(mock_db_session, usuario_id)

    mock_repo.obtener_por_usuario.assert_called_once_with(mock_db_session, usuario_id)
    assert result == [vehiculo_fake]


def test_registrar_vehiculo_exitoso(
    service, mock_db_session, vehiculo_fake, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.crear.return_value = vehiculo_fake

    result = service.registrar_vehiculo(
        db=mock_db_session,
        usuario_id=str(uuid.uuid4()),
        marca="Toyota",
        modelo="Corolla",
        anio=2020,
        kilometraje_actual=50000,
    )

    assert result == vehiculo_fake
    mock_repo.crear.assert_called_once()


def test_actualizar_vehiculo_de_otro_usuario_lanza_permission_error(
    service, mock_db_session, vehiculo_fake, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = vehiculo_fake

    with pytest.raises(PermissionError):
        service.actualizar_vehiculo(
            db=mock_db_session,
            vehiculo_id=str(vehiculo_fake.id),
            usuario_id=str(uuid.uuid4()),  # diferente al dueño
            marca="Honda",
        )


def test_actualizar_vehiculo_inactivo_lanza_value_error(
    service, mock_db_session, vehiculo_fake, mocker,
):
    vehiculo_fake.activo = False
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = vehiculo_fake

    with pytest.raises(ValueError, match="no está activo"):
        service.actualizar_vehiculo(
            db=mock_db_session,
            vehiculo_id=str(vehiculo_fake.id),
            usuario_id=str(vehiculo_fake.usuario_id),
            marca="Honda",
        )


def test_actualizar_vehiculo_inexistente_lanza_value_error(
    service, mock_db_session, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = None

    with pytest.raises(ValueError, match="no encontrado"):
        service.actualizar_vehiculo(
            db=mock_db_session,
            vehiculo_id=str(uuid.uuid4()),
            usuario_id=str(uuid.uuid4()),
            marca="Honda",
        )


def test_eliminar_vehiculo_con_reservas_activas_lanza_value_error(
    service, mock_db_session, vehiculo_fake, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = vehiculo_fake
    mock_repo.tiene_reservas_activas.return_value = True

    with pytest.raises(ValueError):
        service.eliminar_vehiculo(
            db=mock_db_session,
            vehiculo_id=str(vehiculo_fake.id),
            usuario_id=str(vehiculo_fake.usuario_id),
        )


def test_eliminar_vehiculo_de_otro_usuario_lanza_permission_error(
    service, mock_db_session, vehiculo_fake, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = vehiculo_fake

    with pytest.raises(PermissionError):
        service.eliminar_vehiculo(
            db=mock_db_session,
            vehiculo_id=str(vehiculo_fake.id),
            usuario_id=str(uuid.uuid4()),  # diferente al dueño
        )


def test_eliminar_vehiculo_lo_marca_inactivo(
    service, mock_db_session, vehiculo_fake, mocker,
):
    mock_repo = mocker.patch("app.services.vehiculo_service.vehiculo_repo")
    mock_repo.obtener_por_id.return_value = vehiculo_fake
    mock_repo.tiene_reservas_activas.return_value = False

    service.eliminar_vehiculo(
        db=mock_db_session,
        vehiculo_id=str(vehiculo_fake.id),
        usuario_id=str(vehiculo_fake.usuario_id),
    )

    mock_repo.desactivar.assert_called_once_with(mock_db_session, vehiculo_fake)
