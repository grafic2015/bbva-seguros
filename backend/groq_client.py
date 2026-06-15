# ═════════════════════════════════════════════════════════════════════════
# Cliente de Groq para IA
# ═════════════════════════════════════════════════════════════════════════

import os
from groq import Groq

# Inicializar cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def generar_respuesta(mensaje: str, sistema: str = None) -> str:
    """
    Generar respuesta usando Groq

    Args:
        mensaje: Mensaje del usuario
        sistema: Sistema prompt (contexto)

    Returns:
        Respuesta generada por Groq
    """
    try:
        messages = []

        if sistema:
            messages.append({
                "role": "system",
                "content": sistema
            })

        messages.append({
            "role": "user",
            "content": mensaje
        })

        response = client.chat.completions.create(
            messages=messages,
            model=MODEL,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generando respuesta con Groq: {e}")
        return None


def generar_mensaje_dm(nombre_usuario: str, producto: str = "seguro auto") -> str:
    """
    Generar mensaje personalizado para DM en Instagram

    Args:
        nombre_usuario: Nombre del usuario
        producto: Tipo de producto

    Returns:
        Mensaje generado
    """
    sistema = f"""Eres un vendedor de {producto}s para BBVA.
Debes generar un mensaje corto y amigable para enviar por DM en Instagram.
El mensaje debe ser:
- Máximo 150 caracteres
- Incluir oferta (35% descuento)
- Incluir teléfono/WhatsApp para contacto
- Ser profesional pero casual"""

    mensaje = f"Genera un DM para {nombre_usuario} que vio nuestro post y quiere información sobre {producto}s"

    return generar_respuesta(mensaje, sistema)


def clasificar_respuesta(mensaje: str) -> str:
    """
    Clasificar la respuesta de un usuario como: interesado, no_interesado, etc.

    Args:
        mensaje: Respuesta del usuario

    Returns:
        Clasificación: "interesado", "no_interesado", "indeciso"
    """
    sistema = """Analiza el siguiente mensaje y clasifícalo como:
- "interesado": Si muestra interés en el producto
- "no_interesado": Si rechaza claramente
- "indeciso": Si no está seguro

Responde SOLO con una palabra."""

    respuesta = generar_respuesta(mensaje, sistema)

    if respuesta:
        return respuesta.lower().strip()
    return "indeciso"


# Ejemplo de uso
if __name__ == "__main__":
    # Test
    msg = generar_mensaje_dm("@juanperez", "seguro auto")
    print(f"Mensaje generado: {msg}")

    # Clasificar
    clasificacion = clasificar_respuesta("Sí, me interesa. ¿Cuánto cuesta?")
    print(f"Clasificación: {clasificacion}")
