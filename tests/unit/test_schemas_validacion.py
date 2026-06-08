import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from pydantic import ValidationError

from app.schemas.recordatorio import RecordatorioCreateSchema
from app.schemas.vehiculo import VehiculoCreateSchema
from app.schemas.auth import RegistroUsuarioSchema
from app.schemas.asistente import ConsultaAsistenteSchema


def test_recordatorio_create_schema_acepta_uuid_strings():
    schema = RecordatorioCreateSchema(
        vehiculo_id=str(uuid.uuid4()),
        tipo_mantenimiento_id=str(uuid.uuid4()),
        fecha_programada=date.today() + timedelta(days=10),
    )
    assert schema.vehiculo_id is not None
    assert schema.tipo_mantenimiento_id is not None


def test_vehiculo_create_schema_rechaza_anio_no_numerico():
    with pytest.raises(ValidationError):
        VehiculoCreateSchema(
            marca="Toyota",
            modelo="Corolla",
            anio="dos mil veinte",
            kilometraje_actual=50000,
        )


def test_registro_usuario_schema_valida_email():
    with pytest.raises(ValidationError):
        RegistroUsuarioSchema(
            nombre_completo="Juan Pérez",
            correo="no-es-email",
            contrasena="password123",
        )


def test_consulta_asistente_schema_acepta_historial_vacio():
    schema_sin_historial = ConsultaAsistenteSchema(mensaje="Hola")
    assert schema_sin_historial.historial == []

    schema_historial_vacio = ConsultaAsistenteSchema(mensaje="Hola", historial=[])
    assert schema_historial_vacio.historial == []
