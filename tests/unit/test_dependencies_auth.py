import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import uuid

from fastapi import HTTPException

from app.core.dependencies import get_current_user, get_current_taller, get_current_admin


def test_get_current_user_con_token_valido_retorna_usuario(
    mocker, mock_db_session, usuario_fake,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        return_value={"uid": usuario_fake.firebase_uid},
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = usuario_fake

    credentials = MagicMock()
    credentials.credentials = "token_valido"

    result = get_current_user(credentials=credentials, db=mock_db_session)

    assert result == usuario_fake


def test_get_current_user_con_token_invalido_lanza_http_401(
    mocker, mock_db_session,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        side_effect=Exception("Token inválido"),
    )
    credentials = MagicMock()
    credentials.credentials = "token_invalido"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=mock_db_session)

    assert exc_info.value.status_code == 401


def test_get_current_user_usuario_inactivo_lanza_http_401(
    mocker, mock_db_session,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        return_value={"uid": "some_uid"},
    )
    # La query filtra por activo=True → si el usuario está inactivo, first() retorna None
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    credentials = MagicMock()
    credentials.credentials = "token_valido"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=mock_db_session)

    assert exc_info.value.status_code == 401


def test_get_current_taller_con_taller_pendiente_lanza_http_403(
    mocker, mock_db_session,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        return_value={"uid": "some_uid"},
    )
    # El filtro incluye Taller.estado == "activo"; un taller pendiente no aparece
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    credentials = MagicMock()
    credentials.credentials = "token_valido"

    with pytest.raises(HTTPException) as exc_info:
        get_current_taller(credentials=credentials, db=mock_db_session)

    assert exc_info.value.status_code == 403


def test_get_current_admin_usuario_no_admin_lanza_http_403(
    mocker, mock_db_session,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        return_value={"uid": "some_uid"},
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    credentials = MagicMock()
    credentials.credentials = "token_valido"

    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(credentials=credentials, db=mock_db_session)

    assert exc_info.value.status_code == 403


def test_get_current_user_filtra_por_firebase_uid_y_activo_true(
    mocker, mock_db_session, usuario_fake,
):
    mocker.patch(
        "app.core.dependencies.verificar_token_firebase",
        return_value={"uid": usuario_fake.firebase_uid},
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = usuario_fake

    credentials = MagicMock()
    credentials.credentials = "token_valido"

    get_current_user(credentials=credentials, db=mock_db_session)

    # Verifica que filter recibió exactamente 2 criterios: firebase_uid y activo
    filter_call_args = mock_db_session.query.return_value.filter.call_args[0]
    assert len(filter_call_args) == 2
