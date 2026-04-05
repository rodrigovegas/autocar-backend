import google.generativeai as genai
from app.core.config import settings

# Singleton — inicializar Gemini una sola vez
genai.configure(api_key=settings.GEMINI_API_KEY)

PROMPT_SISTEMA = """
Eres un asistente educativo especializado exclusivamente en mantenimiento preventivo vehicular.

Tu función es ayudar a propietarios de vehículos que NO tienen conocimientos técnicos avanzados 
en mecánica automotriz, explicando conceptos de manera clara, sencilla y accesible.

PUEDES responder preguntas sobre:
- Conceptos básicos de mantenimiento preventivo vehicular
- Explicación de qué es y para qué sirve cada tipo de mantenimiento
- Intervalos recomendados de revisión (aceite, frenos, neumáticos, batería, etc.)
- Señales de alerta que indican que un vehículo necesita mantenimiento
- Diferencia entre mantenimiento preventivo y correctivo
- Consejos generales para el cuidado del vehículo

NO PUEDES:
- Realizar diagnósticos mecánicos específicos de fallas
- Reemplazar la evaluación de un mecánico profesional
- Responder preguntas no relacionadas con el mantenimiento vehicular
- Dar recomendaciones de marcas, precios o talleres específicos

Si el usuario pregunta algo fuera de tu dominio, declina amablemente y 
recuérdale que puedes ayudarle con preguntas sobre mantenimiento preventivo vehicular.

Responde siempre en español, con un tono amigable y en lenguaje sencillo.
"""

class GeminiService:
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=PROMPT_SISTEMA
        )
    
    def generar_respuesta(self, mensaje: str, historial: list = []) -> str:
        """Genera una respuesta del asistente conversacional."""
        try:
            # Construir el historial de conversación
            historial_gemini = []
            for msg in historial:
                historial_gemini.append({
                    "role": msg.rol,
                    "parts": [msg.contenido]
                })
            
            # Iniciar o continuar la conversación
            chat = self.model.start_chat(history=historial_gemini)
            respuesta = chat.send_message(mensaje)
            return respuesta.text
            
        except Exception as e:
            raise ValueError(f"Error al generar respuesta: {str(e)}")
    
    def validar_contenido_educativo(self, titulo: str, cuerpo: str, 
                                     categoria: str) -> str:
        """Valida contenido educativo publicado por un taller."""
        try:
            prompt = f"""
Analiza el siguiente contenido educativo sobre mantenimiento vehicular 
que fue publicado por un taller mecánico:

TÍTULO: {titulo}
CATEGORÍA: {categoria}
CONTENIDO: {cuerpo}

Evalúa el contenido en base a estos criterios:
1. Claridad: ¿Es comprensible para usuarios sin conocimientos técnicos?
2. Coherencia: ¿Es coherente y tiene sentido técnico?
3. Pertinencia: ¿Está relacionado con mantenimiento preventivo vehicular?
4. Seguridad: ¿No contiene información que pueda ser peligrosa o engañosa?

Proporciona un informe breve con:
- Puntuación general (Apto / Requiere revisión / No apto)
- Observaciones principales en 2-3 oraciones
- Sugerencias de mejora si aplica

Responde en español de forma concisa.
"""
            respuesta = self.model.generate_content(prompt)
            return respuesta.text
            
        except Exception as e:
            raise ValueError(f"Error al validar contenido: {str(e)}")
    
    def personalizar_recordatorio(self, tipo_mantenimiento: str, 
                                   marca: str, modelo: str, 
                                   anio: int, kilometraje: int) -> str:
        """Genera texto personalizado para un recordatorio de mantenimiento."""
        try:
            prompt = f"""
Genera un mensaje de recordatorio amigable y motivador para un propietario 
de vehículo que debe realizar el siguiente mantenimiento:

Vehículo: {marca} {modelo} {anio}
Kilometraje actual: {kilometraje} km
Tipo de mantenimiento: {tipo_mantenimiento}

El mensaje debe:
- Ser breve (máximo 2 oraciones)
- Explicar brevemente por qué es importante este mantenimiento
- Usar un tono amigable y no alarmante
- Estar en español

Solo responde con el mensaje de recordatorio, sin explicaciones adicionales.
"""
            respuesta = self.model.generate_content(prompt)
            return respuesta.text
            
        except Exception as e:
            return f"Recordatorio: Es momento de realizar el {tipo_mantenimiento} de tu {marca} {modelo}."