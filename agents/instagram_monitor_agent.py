import json
import time
from datetime import datetime
from config import (
    INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD, TRIGGER_KEYWORDS,
    AUTO_RESPONSE_MESSAGE, LEADS_FILE
)

# Importar el agente de OpenAI
try:
    from openai_agent import generate_response, extract_info_from_message, qualify_lead
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def load_leads():
    """Carga el archivo de leads"""
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"leads": [], "total_contacts": 0, "total_interested": 0}

def save_leads(leads_data):
    """Guarda el archivo de leads"""
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads_data, f, indent=2, ensure_ascii=False)

def login_instagram():
    """Autentica en Instagram (simulado)"""
    print("✅ Modo de demostración: Instagram Monitor listo")
    print(f"   Email: {INSTAGRAM_EMAIL}")
    print(f"   Buscando: {TRIGGER_KEYWORDS}")
    return True

def check_comments_for_keywords(client=None):
    """Monitorea comentarios en posts recientes buscando keywords"""
    try:
        print(f"\n📱 Monitoreando comentarios...")
        print(f"   Keywords: {TRIGGER_KEYWORDS}")
        print(f"   Mensaje automático: {AUTO_RESPONSE_MESSAGE[:50]}...")

        leads_data = load_leads()
        contacted_usernames = {lead["usuario"] for lead in leads_data["leads"]}

        # Simulación de comentarios encontrados (para demostración)
        # En producción, esto se conectaría a la API real de Instagram
        demo_comments = [
            {"username": "maria_gomez", "text": "Quiero información sobre seguros"},
            {"username": "carlos_lopez", "text": "Estoy interesado, quiero cotizar"},
            {"username": "juan_hernandez", "text": "Quiero saber los precios"},
        ]

        nuevos_leads = 0
        for comment in demo_comments:
            commenter = comment["username"]
            comment_text = comment["text"].lower()

            # Verificar si contiene keywords
            has_keyword = any(kw.lower() in comment_text for kw in TRIGGER_KEYWORDS)

            if has_keyword and commenter not in contacted_usernames:
                print(f"🎯 Encontrado '{TRIGGER_KEYWORDS}' de @{commenter}")

                # Extraer información del comentario si OpenAI está disponible
                extracted_info = {}
                lead_quality = {"calificacion": "medio"}
                if HAS_OPENAI:
                    extracted_info = extract_info_from_message(comment_text)
                    lead_quality = qualify_lead(comment_text)

                # Enviar DM automático (con OpenAI si está disponible)
                send_dm(commenter, comment_text)

                # Guardar lead con información mejorada
                new_lead = {
                    "id": f"ig_{int(time.time())}_{nuevos_leads}",
                    "nombre": commenter,
                    "usuario": commenter,
                    "estado": "nuevo",
                    "fecha": datetime.now().isoformat(),
                    "comentario": comment_text,
                    "respuesta": "DM enviado automáticamente",
                    "calificacion": lead_quality.get("calificacion", "medio"),
                    "vehiculo": extracted_info.get("marca"),
                    "modelo": extracted_info.get("modelo"),
                    "año": extracted_info.get("año")
                }

                leads_data["leads"].append(new_lead)
                leads_data["total_contacts"] += 1
                contacted_usernames.add(commenter)
                nuevos_leads += 1

                print(f"✅ Lead guardado: @{commenter}")

        save_leads(leads_data)
        print(f"\n📊 Total de leads contactados: {leads_data['total_contacts']}")

    except Exception as e:
        print(f"❌ Error monitoreando comentarios: {e}")

def send_dm(username, user_message=""):
    """Envía DM automático (puede usar OpenAI si está disponible)"""
    try:
        # Si OpenAI está disponible, generar respuesta más inteligente
        if HAS_OPENAI and user_message:
            message = generate_response(user_message)
            print(f"📨 DM enviado a @{username}")
            print(f"   Mensaje IA: {message}")
        else:
            # Fallback al mensaje por defecto
            message = AUTO_RESPONSE_MESSAGE
            print(f"📨 DM enviado a @{username}")
            print(f"   Mensaje: {message}")
        return True
    except Exception as e:
        print(f"❌ Error enviando DM a @{username}: {e}")
        return False

def monitor_loop(interval_minutes=5):
    """Loop continuo de monitoreo"""
    client = login_instagram()
    if not client:
        return

    print(f"\n🔄 Iniciando monitoreo cada {interval_minutes} minutos...")

    try:
        while True:
            check_comments_for_keywords(client)
            print(f"⏳ Próxima revisión en {interval_minutes} minutos...")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")

if __name__ == "__main__":
    monitor_loop()
