import sys
from unittest.mock import MagicMock

# Bloquea la inicialización de Firebase antes de que cualquier módulo de la
# app sea importado. security.py ejecuta firebase_admin.initialize_app() a
# nivel de módulo; si firebase_admin ya está en sys.modules como un Mock,
# esa llamada se convierte en un no-op seguro.
_firebase_mock = MagicMock()
sys.modules.setdefault("firebase_admin", _firebase_mock)
sys.modules.setdefault("firebase_admin.credentials", MagicMock())
sys.modules.setdefault("firebase_admin.auth", MagicMock())
