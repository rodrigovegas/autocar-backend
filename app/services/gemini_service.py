from google import genai
from google.genai import types
from app.core.config import settings

PROMPT_SISTEMA = """
Eres AutoCar Asistente, un asistente educativo especializado EXCLUSIVAMENTE en mantenimiento preventivo vehicular.

Tu función es ayudar a propietarios de vehículos sin conocimientos técnicos avanzados, explicando conceptos de manera clara y accesible.

PUEDES responder ÚNICAMENTE sobre:
- Qué es el mantenimiento preventivo y por qué es importante
- Intervalos recomendados de revisión: aceite, frenos, neumáticos, batería, refrigerante, filtros, bujías
- Señales de alerta que indican que un vehículo necesita mantenimiento
- Diferencia entre mantenimiento preventivo y correctivo
- Consejos básicos para el cuidado del vehículo
- Explicación de términos técnicos de mecánica automotriz en lenguaje sencillo

DEBES RECHAZAR cualquier pregunta que NO sea sobre mantenimiento vehicular.

Cuando recibas una pregunta fuera de tu dominio responde EXACTAMENTE así:
"Lo siento, solo puedo ayudarte con preguntas sobre mantenimiento preventivo vehicular. ¿Tienes alguna duda sobre el cuidado de tu auto, como cambios de aceite, revisión de frenos o neumáticos?"

NUNCA respondas preguntas sobre:
- Geografía, historia, ciencias, matemáticas o cualquier tema general
- Política, entretenimiento, cocina u otros temas no relacionados
- Diagnósticos de fallas mecánicas específicas
- Precios, marcas o recomendaciones de talleres específicos

Responde siempre en español con tono amigable y lenguaje sencillo.
"""

# Singleton — cliente Gemini inicializado una sola vez
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class GeminiService:

    def generar_respuesta(self, mensaje: str, historial: list = []) -> str:
        """Genera una respuesta del asistente conversacional."""
        try:
            client = get_gemini_client()

            # Construir historial de conversación
            historial_genai = []
            for msg in historial:
                rol = "user" if msg.rol == "user" else "model"
                historial_genai.append(
                    types.Content(
                        role=rol,
                        parts=[types.Part(text=msg.contenido)]
                    )
                )

            # Agregar mensaje actual
            historial_genai.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=mensaje)]
                )
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=historial_genai,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_SISTEMA,
                    temperature=0.7,
                )
            )

            return response.text

        except Exception as e:
            raise ValueError(f"Error al generar respuesta: {str(e)}")

    def validar_contenido_educativo(self, titulo: str, cuerpo: str,
                                     categoria: str) -> str:
        """Valida contenido educativo publicado por un taller."""
        try:
            client = get_gemini_client()

            prompt = f"""
Analiza el siguiente contenido educativo sobre mantenimiento vehicular 
publicado por un taller mecánico:

TÍTULO: {titulo}
CATEGORÍA: {categoria}
CONTENIDO: {cuerpo}

Evalúa en base a:
1. Claridad para usuarios sin conocimientos técnicos
2. Coherencia técnica
3. Pertinencia con mantenimiento preventivo vehicular
4. Seguridad de la información

Proporciona:
- Puntuación: Apto / Requiere revisión / No apto
- Observaciones en 2-3 oraciones
- Sugerencias de mejora si aplica

Responde en español de forma concisa.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            raise ValueError(f"Error al validar contenido: {str(e)}")

    def personalizar_recordatorio(self, tipo_mantenimiento: str,
                                   marca: str, modelo: str,
                                   anio: int, kilometraje: int) -> str:
        """Genera texto personalizado para un recordatorio."""
        try:
            client = get_gemini_client()

            prompt = f"""
Genera un mensaje de recordatorio amigable para un propietario de vehículo:

Vehículo: {marca} {modelo} {anio}
Kilometraje actual: {kilometraje} km
Mantenimiento requerido: {tipo_mantenimiento}

El mensaje debe ser breve (máximo 2 oraciones), explicar por qué es importante
y usar un tono amigable. Solo responde con el mensaje, sin explicaciones adicionales.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            return f"Es momento de realizar el {tipo_mantenimiento} de tu {marca} {modelo}. Mantén tu vehículo en óptimas condiciones."