import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from app.services.taller_mantenimiento_service import TallerMantenimientoService
from app.services.recordatorio_service import RecordatorioService
from app.schemas.mantenimiento_registro import MantenimientoRegistroCreate
from app.models.reserva import Reserva
from app.models.mantenimiento import Mantenimiento


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return TallerMantenimientoService()


@pytest.fixture
def taller_id():
    return uuid.uuid4()


@pytest.fixture
def reserva_fake():
    r = MagicMock()
    r.id = uuid.uuid4()
    r.usuario_id = uuid.uuid4()
    r.vehiculo_id = uuid.uuid4()
    r.taller_id = uuid.uuid4()
    r.estado = "confirmada"
    return r


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_datos(
    reserva_id,
    crear_recordatorio=False,
    km_proximo=None,
    fecha_proximo=None,
    recomendaciones=None,
):
    return MantenimientoRegistroCreate(
        reserva_id=str(reserva_id),
        kilometraje_registro=50000,
        fecha_realizado=date.today(),
        crear_recordatorio_proximo=crear_recordatorio,
        km_proximo_mantenimiento=km_proximo,
        fecha_proximo_mantenimiento=fecha_proximo,
        recomendaciones=recomendaciones,
    )


def _make_db_mock(reserva=None, tipo_id=None):
    """
    Devuelve un mock de db con:
      - query(Reserva)     → reserva
      - query(Mantenimiento) → None  (sin duplicado)
      - query(ServicioTaller.tipo_mantenimiento_id) → (tipo_id,) o None
    """
    mock_db = MagicMock()

    def query_side_effect(model):
        q = MagicMock()
        if model is Reserva:
            q.filter.return_value.first.return_value = reserva
        elif model is Mantenimiento:
            q.filter.return_value.first.return_value = None
        else:
            # ServicioTaller.tipo_mantenimiento_id (column attribute)
            row = (tipo_id,) if tipo_id is not None else None
            q.join.return_value.filter.return_value.first.return_value = row
        return q

    mock_db.query.side_effect = query_side_effect
    return mock_db


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_registrar_mantenimiento_sin_checkbox_no_invoca_recordatorio(
    service, reserva_fake, taller_id, mocker,
):
    mock_rec = mocker.patch(
        "app.services.taller_mantenimiento_service.recordatorio_service"
    )
    mock_db = _make_db_mock(reserva=reserva_fake)
    datos = _make_datos(reserva_fake.id, crear_recordatorio=False)

    service.registrar_mantenimiento(db=mock_db, datos=datos, taller_id=taller_id)

    mock_rec.crear_automatico_desde_mantenimiento.assert_not_called()


def test_registrar_mantenimiento_con_checkbox_invoca_recordatorio(
    service, reserva_fake, taller_id, mocker,
):
    tipo_id = uuid.uuid4()
    mock_rec = mocker.patch(
        "app.services.taller_mantenimiento_service.recordatorio_service"
    )
    mock_db = _make_db_mock(reserva=reserva_fake, tipo_id=tipo_id)
    datos = _make_datos(
        reserva_fake.id,
        crear_recordatorio=True,
        km_proximo=60000,
        fecha_proximo=date.today() + timedelta(days=180),
    )

    service.registrar_mantenimiento(db=mock_db, datos=datos, taller_id=taller_id)

    mock_rec.crear_automatico_desde_mantenimiento.assert_called_once()
    kwargs = mock_rec.crear_automatico_desde_mantenimiento.call_args.kwargs
    assert kwargs["tipo_mantenimiento_id"] == str(tipo_id)
    assert kwargs["kilometraje_programado"] == 60000


def test_registrar_mantenimiento_con_checkbox_sin_datos_proximo_lanza_value_error(
    service, reserva_fake, taller_id, mocker,
):
    tipo_id = uuid.uuid4()
    mock_rec = mocker.patch(
        "app.services.taller_mantenimiento_service.recordatorio_service"
    )
    mock_rec.crear_automatico_desde_mantenimiento.side_effect = ValueError(
        "Para crear el recordatorio debe especificar fecha o kilometraje"
    )
    mock_db = _make_db_mock(reserva=reserva_fake, tipo_id=tipo_id)
    datos = _make_datos(reserva_fake.id, crear_recordatorio=True)  # sin km ni fecha próximos

    with pytest.raises(ValueError):
        service.registrar_mantenimiento(db=mock_db, datos=datos, taller_id=taller_id)


def test_registrar_mantenimiento_con_error_en_recordatorio_hace_rollback(
    service, reserva_fake, taller_id, mocker,
):
    tipo_id = uuid.uuid4()
    mock_rec = mocker.patch(
        "app.services.taller_mantenimiento_service.recordatorio_service"
    )
    mock_rec.crear_automatico_desde_mantenimiento.side_effect = ValueError(
        "Error al crear recordatorio"
    )
    mock_db = _make_db_mock(reserva=reserva_fake, tipo_id=tipo_id)
    datos = _make_datos(reserva_fake.id, crear_recordatorio=True)

    with pytest.raises(ValueError):
        service.registrar_mantenimiento(db=mock_db, datos=datos, taller_id=taller_id)

    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()


def test_recordatorio_automatico_usa_origen_automatico(
    mock_db_session, vehiculo_fake, tipo_mantenimiento_fake, mocker,
):
    """Verifica directamente en RecordatorioService que crear_flush recibe origen='automatico'."""
    rec_service = RecordatorioService()
    mock_repo = mocker.patch("app.services.recordatorio_service.recordatorio_repo")
    mock_repo.obtener_activo_por_vehiculo_y_tipo.return_value = None

    nuevo = MagicMock()
    nuevo.origen = "automatico"
    mock_repo.crear_flush.return_value = nuevo

    result = rec_service.crear_automatico_desde_mantenimiento(
        db=mock_db_session,
        usuario_id=str(vehiculo_fake.usuario_id),
        vehiculo_id=str(vehiculo_fake.id),
        tipo_mantenimiento_id=str(tipo_mantenimiento_fake.id),
        fecha_programada=date.today() + timedelta(days=30),
        kilometraje_programado=None,
    )

    _, kwargs = mock_repo.crear_flush.call_args
    assert kwargs.get("origen") == "automatico"
    assert result.origen == "automatico"


def test_recordatorio_automatico_trunca_recomendaciones_a_200_chars(
    service, reserva_fake, taller_id, mocker,
):
    tipo_id = uuid.uuid4()
    mock_rec = mocker.patch(
        "app.services.taller_mantenimiento_service.recordatorio_service"
    )
    mock_db = _make_db_mock(reserva=reserva_fake, tipo_id=tipo_id)

    datos = _make_datos(
        reserva_fake.id,
        crear_recordatorio=True,
        km_proximo=60000,
        recomendaciones="R" * 500,
    )

    service.registrar_mantenimiento(db=mock_db, datos=datos, taller_id=taller_id)

    kwargs = mock_rec.crear_automatico_desde_mantenimiento.call_args.kwargs
    texto = kwargs.get("texto_personalizado")
    assert texto is not None
    assert len(texto) <= 200
