import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

TIPOS_PERMITIDOS = {
    "image": ["image/jpeg", "image/png", "image/webp"],
    "video": ["video/mp4", "video/quicktime", "video/avi"],
    "raw":   ["application/pdf"]
}

MAX_TAMANIO_MB = 50


def obtener_tipo_cloudinary(content_type: str, nombre: str = "") -> str:
    for tipo, mimes in TIPOS_PERMITIDOS.items():
        if content_type in mimes:
            return tipo

    extension = nombre.lower().split(".")[-1] if "." in nombre else ""
    extensiones = {
        "jpg": "image", "jpeg": "image", "png": "image", "webp": "image",
        "mp4": "video", "mov": "video", "avi": "video",
        "pdf": "raw",
    }
    if extension in extensiones:
        return extensiones[extension]

    return "image"


def upload_archivo(archivo_bytes: bytes, content_type: str, nombre: str) -> dict:
    tipo = obtener_tipo_cloudinary(content_type, nombre)
    if not tipo:
        raise ValueError(f"Tipo de archivo no permitido: {content_type}")

    resultado = cloudinary.uploader.upload(
        archivo_bytes,
        folder="autocar/educativo",
        resource_type=tipo,
        use_filename=True,
        unique_filename=True,
        chunk_size=6000000,
    )

    return {
        "url": resultado["secure_url"],
        "public_id": resultado["public_id"],
        "tipo": tipo,
    }


def delete_archivo(public_id: str, tipo: str = "image") -> bool:
    resultado = cloudinary.uploader.destroy(public_id, resource_type=tipo)
    return resultado.get("result") == "ok"
