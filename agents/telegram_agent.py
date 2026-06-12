"""
Agente para enviar notificaciones a Telegram.
"""
import requests
import config

def send_telegram_alert(msg: str) -> bool:
    """Envía un mensaje de alerta a Telegram."""
    config.load_settings()
    token = getattr(config, "TELEGRAM_TOKEN", "")
    chat_id = getattr(config, "TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] Error al enviar mensaje: {e}")
        return False

if __name__ == "__main__":
    send_telegram_alert("🚀 *Agente de Empleos* iniciado.")
