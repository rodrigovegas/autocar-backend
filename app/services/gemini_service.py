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

    def generar_template_formulario(self, descripcion: str) -> str:
        """Genera un template de formulario de mantenimiento basado en la descripción del usuario."""
        try:
            client = get_gemini_client()

            prompt = f"""
Eres un mecánico experto. Un usuario describió el siguiente problema o necesidad con su vehículo:

"{descripcion}"

Genera un template de formulario de revisión técnica específico para este caso.
El template debe:
- Ser específico para el problema descrito
- Tener entre 5 y 10 ítems de revisión
- Cada ítem debe tener opciones de estado separadas por " / "
- Incluir siempre al menos una opción "No revisado"
- Terminar con una línea de "OBSERVACIONES ADICIONALES:"
- Estar en español
- Ser conciso y profesional

Responde ÚNICAMENTE con el template, sin explicaciones adicionales.

Ejemplo de formato:
REVISIÓN POR RUIDO AL FRENAR:
- Estado pastillas delanteras: Buenas / Desgastadas / Requieren cambio
- Estado pastillas traseras: Buenas / Desgastadas / Requieren cambio
- Discos: Buen estado / Rayados / Desgastados
- Líquido de frenos: Normal / Bajo / Contaminado
- Pinzas de freno: Funcionando / Con fuga / Bloqueadas

OBSERVACIONES ADICIONALES:
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception:
            return f"REVISIÓN - {descripcion.upper()}:\n- Estado general: Bueno / Regular / Malo / No revisado\n- Problema específico: Identificado / No identificado\n\nOBSERVACIONES ADICIONALES:\n"