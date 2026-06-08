import pytest
import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_session():
    mock = MagicMock()
    # query_mock es reutilizable en cadena: .filter().filter().first() etc.
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.join.return_value = query_mock
    query_mock.options.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.first.return_value = None
    query_mock.all.return_value = []
    mock.query.return_value = query_mock
    return mock


@pytest.fixture
def usuario_fake():
    usuario = MagicMock()
    usuario.id = uuid.uuid4()
    usuario.firebase_uid = "firebase_uid_fake_abc123"
    usuario.correo = "usuario_fake@example.com"
    usuario.nombre_completo = "Usuario Fake"
    usuario.activo = True
    return usuario


@pytest.fixture
def vehiculo_fake(usuario_fake):
    vehiculo = MagicMock()
    vehiculo.id = uuid.uuid4()
    vehiculo.usuario_id = usuario_fake.id
    vehiculo.marca = "Toyota"
    vehiculo.modelo = "Corolla"
    vehiculo.anio = 2020
    vehiculo.kilometraje_actual = 50000
    vehiculo.activo = True
    return vehiculo


@pytest.fixture
def tipo_mantenimiento_fake():
    tipo = MagicMock()
    tipo.id = uuid.uuid4()
    tipo.nombre = "Cambio de aceite"
    tipo.estado = "aprobado"
    tipo.activo = True
    return tipo


@pytest.fixture
def recordatorio_fake(usuario_fake, vehiculo_fake, tipo_mantenimiento_fake):
    recordatorio = MagicMock()
    recordatorio.id = uuid.uuid4()
    recordatorio.usuario_id = usuario_fake.id
    recordatorio.vehiculo_id = vehiculo_fake.id
    recordatorio.tipo_mantenimiento_id = tipo_mantenimiento_fake.id
    recordatorio.origen = "manual"
    recordatorio.estado = "activo"
    recordatorio.fecha_programada = date.today() + timedelta(days=30)
    recordatorio.kilometraje_programado = 55000
    return recordatorio
