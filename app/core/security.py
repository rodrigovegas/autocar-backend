import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings
import requests

# Inicializar Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

def verificar_token_firebase(id_token: str) -> dict:
    """Verifica el token JWT de Firebase y retorna los datos del usuario."""
    try:
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=60)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Token inválido: {str(e)}")

def crear_usuario_firebase(correo: str, contrasena: str) -> str:
    """Crea un usuario en Firebase Authentication y retorna su UID."""
    try:
        user = auth.create_user(
            email=correo,
            password=contrasena
        )
        return user.uid
    except auth.EmailAlreadyExistsError:
        raise ValueError("El correo ya está registrado")
    except Exception as e:
        raise ValueError(f"Error al crear usuario: {str(e)}")

def obtener_token_firebase(correo: str, contrasena: str, api_key: str) -> str:
    """Obtiene el id_token de Firebase usando correo y contraseña."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": correo,
        "password": contrasena,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise ValueError("Credenciales incorrectas")
    return response.json()["idToken"]