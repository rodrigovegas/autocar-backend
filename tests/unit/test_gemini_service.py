import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from app.services.gemini_service import GeminiService


@pytest.fixture
def service():
    return GeminiService()


@pytest.fixture
def mock_gemini_client(mocker):
    client = MagicMock()
    mocker.patch("app.services.gemini_service.get_gemini_client", return_value=client)
    return client


def test_generar_respuesta_exitosa_retorna_texto(service, mock_gemini_client):
    mock_gemini_client.models.generate_content.return_value.text = "Respuesta de prueba"

    result = service.generar_respuesta("¿Cuándo debo cambiar el aceite?")

    assert result == "Respuesta de prueba"
    mock_gemini_client.models.generate_content.assert_called_once()


def test_generar_respuesta_falla_lanza_value_error(service, mock_gemini_client):
    mock_gemini_client.models.generate_content.side_effect = Exception("API caída")

    with pytest.raises(ValueError, match="Error al generar respuesta:"):
        service.generar_respuesta("¿Cuándo debo cambiar el aceite?")


def test_validar_contenido_educativo_construye_prompt_con_titulo_y_categoria(
    service, mock_gemini_client,
):
    mock_gemini_client.models.generate_content.return_value.text = "Apto"

    service.validar_contenido_educativo(
        titulo="Cambio de aceite",
        cuerpo="El aceite lubrica el motor y debe cambiarse regularmente.",
        categoria="Motor",
    )

    call = mock_gemini_client.models.generate_content.call_args
    # validar_contenido_educativo pasa contents como kwarg
    contents = call.kwargs.get("contents") or call[1].get("contents") or call[0][1]

    assert "Cambio de aceite" in contents
    assert "Motor" in contents
    assert "El aceite lubrica el motor" in contents


def test_validar_contenido_educativo_falla_lanza_value_error(service, mock_gemini_client):
    mock_gemini_client.models.generate_content.side_effect = Exception("Timeout")

    with pytest.raises(ValueError, match="Error al validar contenido:"):
        service.validar_contenido_educativo(
            titulo="Cambio de aceite",
            cuerpo="El aceite es importante.",
            categoria="Motor",
        )
