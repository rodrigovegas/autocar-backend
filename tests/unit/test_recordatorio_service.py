import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from app.services.recordatorio_service import RecordatorioService
from app.models.vehiculo import Vehiculo
from app.models.tipo_mantenimiento import TipoMantenimiento


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _setup_db_para_crear(mock_db, vehiculo, tipo):
    """Configura mock_db para devolver vehiculo y tipo según el modelo consultado."""
    def query_side_effect(model):
        q = MagicMock()
        if model is Vehiculo:
            q.filter.return_value.first.return_value = vehiculo
        elif model is TipoMantenimiento:
            q.filter.return_value.first.return_value = tipo
        else:
            q.filter.return_value.first.return_value = None
        return q
    mock_db.query.side_effect = query_side_effect


@pytest.fixture
def service():
    return RecordatorioService()


# ---------------------------------------------------------------------------
# Tests: crear()
# ---------------------------------------------------------------------------

def test_crear_recordatorio_con_fecha_y_km_exitoso(
    service, mock_db_session, vehiculo_fake, tipo_mantenimiento_fake,
    recordatorio_fake, mocker,
):
    _setup_db_para_crear(mock_db_session, vehiculo_fake, tipo_mantenimiento_fake)
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.existe_activo_mismo_tipo.return_value = False
    mock_repo.crear.return_value = recordatorio_fake

    result = service.crear(
        db=mock_db_session,
        usuario_id=str(vehiculo_fake.usuario_id),
        vehiculo_id=str(vehiculo_fake.id),
        tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
        fecha_programada=date.today() + timedelta(days=30),
        kilometraje_programado=55000,
    )

    assert result == recordatorio_fake
    mock_repo.crear.assert_called_once()


def test_crear_recordatorio_solo_con_fecha_exitoso(
    service, mock_db_session, vehiculo_fake, tipo_mantenimiento_fake,
    recordatorio_fake, mocker,
):
    _setup_db_para_crear(mock_db_session, vehiculo_fake, tipo_mantenimiento_fake)
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.existe_activo_mismo_tipo.return_value = False
    mock_repo.crear.return_value = recordatorio_fake

    result = service.crear(
        db=mock_db_session,
        usuario_id=str(vehiculo_fake.usuario_id),
        vehiculo_id=str(vehiculo_fake.id),
        tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
        fecha_programada=date.today() + timedelta(days=10),
    )

    assert result == recordatorio_fake


def test_crear_recordatorio_solo_con_km_exitoso(
    service, mock_db_session, vehiculo_fake, tipo_mantenimiento_fake,
    recordatorio_fake, mocker,
):
    _setup_db_para_crear(mock_db_session, vehiculo_fake, tipo_mantenimiento_fake)
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.existe_activo_mismo_tipo.return_value = False
    mock_repo.crear.return_value = recordatorio_fake

    result = service.crear(
        db=mock_db_session,
        usuario_id=str(vehiculo_fake.usuario_id),
        vehiculo_id=str(vehiculo_fake.id),
        tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
        kilometraje_programado=60000,
    )

    assert result == recordatorio_fake


def test_crear_recordatorio_sin_fecha_ni_km_lanza_value_error(
    service, mock_db_session,
):
    with pytest.raises(ValueError, match="Debe especificar fecha o kilometraje"):
        service.crear(
            db=mock_db_session,
            usuario_id=str(uuid.uuid4()),
            vehiculo_id=str(uuid.uuid4()),
            tipo_mantenimiento_id=str(uuid.uuid4()),
        )


def test_crear_recordatorio_con_km_menor_al_actual_lanza_value_error(
    service, mock_db_session, vehiculo_fake, mocker,
):
    # vehiculo_fake.kilometraje_actual = 50000; programado = 40000 → debe fallar
    _setup_db_para_crear(mock_db_session, vehiculo_fake, MagicMock())
    mocker.patch("app.services.recordatorio_service.recordatorio_repo")

    with pytest.raises(ValueError):
        service.crear(
            db=mock_db_session,
            usuario_id=str(vehiculo_fake.usuario_id),
            vehiculo_id=str(vehiculo_fake.id),
            tipo_mantenimiento_id=str(uuid.uuid4()),
            kilometraje_programado=40000,
        )


def test_crear_recordatorio_con_fecha_pasada_lanza_value_error(
    service, mock_db_session,
):
    with pytest.raises(ValueError, match="no puede ser en el pasado"):
        service.crear(
            db=mock_db_session,
            usuario_id=str(uuid.uuid4()),
            vehiculo_id=str(uuid.uuid4()),
            tipo_mantenimiento_id=str(uuid.uuid4()),
            fecha_programada=date.today() - timedelta(days=1),
        )


def test_crear_recordatorio_duplicado_mismo_tipo_lanza_value_error(
    service, mock_db_session, vehiculo_fake, tipo_mantenimiento_fake, mocker,
):
    _setup_db_para_crear(mock_db_session, vehiculo_fake, tipo_mantenimiento_fake)
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.existe_activo_mismo_tipo.return_value = True

    with pytest.raises(ValueError, match="Ya existe un recordatorio activo"):
        service.crear(
            db=mock_db_session,
            usuario_id=str(vehiculo_fake.usuario_id),
            vehiculo_id=str(vehiculo_fake.id),
            tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
            fecha_programada=date.today() + timedelta(days=15),
        )


# ---------------------------------------------------------------------------
# Tests: eliminar()
# ---------------------------------------------------------------------------

def test_eliminar_recordatorio_de_otro_usuario_lanza_permission_error(
    service, mock_db_session, recordatorio_fake, mocker,
):
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.obtener_por_id.return_value = recordatorio_fake

    with pytest.raises(PermissionError):
        service.eliminar(
            db=mock_db_session,
            recordatorio_id=str(recordatorio_fake.id),
            usuario_id=str(uuid.uuid4()),  # diferente al recordatorio_fake.usuario_id
        )


def test_eliminar_recordatorio_inexistente_lanza_value_error(
    service, mock_db_session, mocker,
):
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.obtener_por_id.return_value = None

    with pytest.raises(ValueError, match="Recordatorio no encontrado"):
        service.eliminar(
            db=mock_db_session,
            recordatorio_id=str(uuid.uuid4()),
            usuario_id=str(uuid.uuid4()),
        )


# ---------------------------------------------------------------------------
# Tests: crear_automatico_desde_mantenimiento()
# ---------------------------------------------------------------------------

def test_crear_automatico_desde_mantenimiento_elimina_manual_existente(
    service, mock_db_session, vehiculo_fake, tipo_mantenimiento_fake,
    recordatorio_fake, mocker,
):
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.obtener_activo_por_vehiculo_y_tipo.return_value = recordatorio_fake

    nuevo_recordatorio = MagicMock()
    nuevo_recordatorio.origen = "automatico"
    mock_repo.crear_flush.return_value = nuevo_recordatorio

    result = service.crear_automatico_desde_mantenimiento(
        db=mock_db_session,
        usuario_id=str(vehiculo_fake.usuario_id),
        vehiculo_id=str(vehiculo_fake.id),
        tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
        fecha_programada=date.today() + timedelta(days=30),
        kilometraje_programado=55000,
    )

    # eliminar_flush debe haberse llamado ANTES que crear_flush
    mock_repo.eliminar_flush.assert_called_once_with(mock_db_session, recordatorio_fake)
    mock_repo.crear_flush.assert_called_once()

    # el nuevo recordatorio debe tener origen="automatico"
    _, kwargs = mock_repo.crear_flush.call_args
    assert kwargs.get("origen") == "automatico"
    assert result.origen == "automatico"
