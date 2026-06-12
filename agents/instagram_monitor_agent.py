"""
Instagram Monitor Agent
Monitorea comentarios en Instagram buscando palabras clave ("quiero", "interesado", etc.)
y captura leads de personas interesadas en seguros.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from config import (
    INSTAGRAM_EMAIL,
    INSTAGRAM_PASSWORD,
    INSTAGRAM_ACCOUNTS,
    TRIGGER_KEYWORDS,
    AUTO_RESPONSE_MESSAGE,
    LEADS_FILE,
)


def load_leads() -> dict:
    """Carga el archivo de leads de Instagram."""
    leads_path = Path(LEADS_FILE)
    if leads_path.exists():
        try:
            return json.loads(leads_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"leads": [], "total_contacts": 0, "total_interested": 0, "last_check": None}


def save_leads(leads_data: dict) -> None:
    """Guarda el archivo de leads."""
    Path(LEADS_FILE).write_text(
        json.dumps(leads_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def detect_trigger_keyword(text: str) -> bool:
    """Detecta si el texto contiene palabras clave de interés."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in TRIGGER_KEYWORDS)


def monitor_instagram() -> int:
    """
    Monitorea comentarios en Instagram.
    Devuelve la cantidad de nuevos leads encontrados.
    """
    if not INSTAGRAM_EMAIL or not INSTAGRAM_PASSWORD:
        print("[Instagram Monitor] ⚠️  Falta configurar INSTAGRAM_EMAIL y INSTAGRAM_PASSWORD")
        return 0

    print("[Instagram Monitor] 📸 Iniciando monitoreo de Instagram...")
    leads_data = load_leads()

    # Simulación: En producción, aquí iría la API de Instagram
    # Por ahora, se prepara la estructura para capturar datos

    new_leads = 0
    leads_data["last_check"] = datetime.now().isoformat()

    if new_leads > 0:
        save_leads(leads_data)
        print(f"[Instagram Monitor] ✅ {new_leads} nuevo(s) lead(s) capturado(s)")

    return new_leads


def process_comment(username: str, comment_text: str, post_url: str) -> dict:
    """
    Procesa un comentario detectado en Instagram.
    Si contiene palabras clave, lo guarda como lead.
    """
    if not detect_trigger_keyword(comment_text):
        return {"captured": False}

    leads_data = load_leads()
    lead = {
        "username": username,
        "comment": comment_text,
        "post_url": post_url,
        "timestamp": datetime.now().isoformat(),
        "status": "new",
    }

    # Evitar duplicados
    for existing in leads_data["leads"]:
        if (
            existing.get("username") == username
            and existing.get("post_url") == post_url
        ):
            return {"captured": False, "reason": "duplicate"}

    leads_data["leads"].append(lead)
    leads_data["total_interested"] += 1
    save_leads(leads_data)

    print(
        f"[Instagram Monitor] 🎯 Lead capturado: {username} - '{comment_text[:50]}...'"
    )
    return {"captured": True, "lead": lead, "message": AUTO_RESPONSE_MESSAGE}


def get_leads_summary() -> dict:
    """Retorna un resumen de los leads capturados."""
    leads_data = load_leads()
    return {
        "total_leads": len(leads_data["leads"]),
        "total_interested": leads_data["total_interested"],
        "last_check": leads_data.get("last_check"),
        "leads": leads_data["leads"],
    }
