"""
Instagram Monitor Agent
Monitorea comentarios en Instagram buscando palabras clave ("quiero", "interesado", etc.)
y captura leads de personas interesadas en seguros.

Fuente de verdad ÚNICA: la base de datos (backend.models / Supabase).
"""

from datetime import datetime

from config import (
    INSTAGRAM_EMAIL,
    INSTAGRAM_PASSWORD,
    INSTAGRAM_ACCOUNTS,
    TRIGGER_KEYWORDS,
    AUTO_RESPONSE_MESSAGE,
)
from backend.models import SessionLocal, Lead


def detect_trigger_keyword(text: str) -> bool:
    """Detecta si el texto contiene palabras clave de interés."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in TRIGGER_KEYWORDS)


def monitor_instagram() -> int:
    """
    Monitorea comentarios en Instagram.
    Devuelve la cantidad de nuevos leads encontrados.

    NOTA: la integración real con la API de Instagram aún no está implementada.
    Los leads reales entran vía `process_comment()` (webhook) o carga manual.
    """
    if not INSTAGRAM_EMAIL or not INSTAGRAM_PASSWORD:
        print("[Instagram Monitor] ⚠️  Falta configurar INSTAGRAM_EMAIL y INSTAGRAM_PASSWORD")
        return 0

    print("[Instagram Monitor] 📸 Iniciando monitoreo de Instagram...")
    # TODO: integrar la API de Instagram. Por ahora no captura comentarios reales.
    return 0


def process_comment(username: str, comment_text: str, post_url: str = "") -> dict:
    """
    Procesa un comentario detectado en Instagram.
    Si contiene palabras clave, lo guarda como lead en la base de datos.
    """
    if not detect_trigger_keyword(comment_text):
        return {"captured": False}

    db = SessionLocal()
    try:
        # Evitar duplicados por usuario de Instagram
        existente = db.query(Lead).filter(Lead.usuario_instagram == username).first()
        if existente:
            return {"captured": False, "reason": "duplicate"}

        lead = Lead(
            nombre=username,
            usuario_instagram=username,
            comentario_inicial=comment_text,
            estado="nuevo",
            fuente="instagram",
            fecha_creacion=datetime.utcnow(),
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        print(f"[Instagram Monitor] 🎯 Lead capturado: {username} - '{comment_text[:50]}...'")
        return {
            "captured": True,
            "lead": {"id": lead.id, "usuario": username, "comentario": comment_text},
            "message": AUTO_RESPONSE_MESSAGE,
        }
    finally:
        db.close()


def get_leads_summary() -> dict:
    """Retorna un resumen de los leads capturados (delegado al Leads Manager)."""
    from agents.leads_manager_agent import get_all_leads, get_leads_summary as _summary
    summary = _summary()
    return {
        "total_leads": summary["total_leads"],
        "total_interested": summary["by_status"].get("interesado", 0),
        "last_check": summary.get("last_update"),
        "leads": get_all_leads(),
    }
