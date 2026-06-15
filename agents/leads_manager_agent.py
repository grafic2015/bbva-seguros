"""
Leads Manager Agent
Gestiona los leads almacenados en la base de datos (Supabase).
Permite listar, actualizar estado y obtener resúmenes estadísticos.

Fuente de verdad ÚNICA: la base de datos (backend.models / Supabase).
"""

from datetime import datetime
from typing import List, Dict, Optional

from backend.models import SessionLocal, Lead, EstadoLead


# ── Mapeo DB → shape que consume el panel 3D (frontend) ─────────────────────────

def _lead_to_dict(lead: Lead) -> dict:
    """Convierte un Lead de la DB al shape que espera el frontend del panel 3D."""
    estado = lead.estado.value if hasattr(lead.estado, "value") else lead.estado
    return {
        "id": lead.id,
        "usuario": lead.usuario_instagram,
        "nombre": lead.nombre,
        "comentario": lead.comentario_inicial,
        "estado": estado,
        "telefono": lead.telefono,
        "email": lead.email,
        "fecha_contacto": lead.fecha_creacion.isoformat() if lead.fecha_creacion else None,
        "actualizado": lead.fecha_actualizacion.isoformat() if lead.fecha_actualizacion else None,
        "dm_enviado": bool(lead.cotizacion_generada),
    }


# ── Lecturas ────────────────────────────────────────────────────────────────────

def get_all_leads() -> List[dict]:
    """Obtiene todos los leads desde la base de datos."""
    db = SessionLocal()
    try:
        leads = db.query(Lead).order_by(Lead.fecha_creacion.desc()).all()
        return [_lead_to_dict(l) for l in leads]
    finally:
        db.close()


def get_lead_by_username(username: str) -> Optional[dict]:
    """Busca un lead por usuario de Instagram."""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.usuario_instagram == username).first()
        return _lead_to_dict(lead) if lead else None
    finally:
        db.close()


def get_leads_by_status(status: str) -> List[dict]:
    """Obtiene todos los leads con un estado específico."""
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(Lead.estado == status).all()
        return [_lead_to_dict(l) for l in leads]
    finally:
        db.close()


def get_hot_leads() -> List[dict]:
    """Retorna los leads 'calientes' (nuevos o interesados)."""
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(
            Lead.estado.in_([EstadoLead.NUEVO, EstadoLead.INTERESADO])
        ).all()
        return [_lead_to_dict(l) for l in leads]
    finally:
        db.close()


def get_leads_summary() -> dict:
    """Retorna un resumen estadístico de los leads (estados en español)."""
    db = SessionLocal()
    try:
        leads = db.query(Lead).all()
        total = len(leads)

        def count(estado: EstadoLead) -> int:
            return len([l for l in leads if l.estado == estado])

        by_status = {
            "nuevo":          count(EstadoLead.NUEVO),
            "interesado":     count(EstadoLead.INTERESADO),
            "en_seguimiento": count(EstadoLead.EN_SEGUIMIENTO),
            "convertido":     count(EstadoLead.CONVERTIDO),
            "rechazado":      count(EstadoLead.RECHAZADO),
        }

        conversion_rate = 0
        if total > 0:
            conversion_rate = round((by_status["convertido"] / total) * 100, 2)

        return {
            "total_leads": total,
            "by_status": by_status,
            "conversion_rate": conversion_rate,
            "last_update": datetime.now().isoformat(),
        }
    finally:
        db.close()


# ── Escrituras ──────────────────────────────────────────────────────────────────

VALID_STATUSES = ["nuevo", "interesado", "en_seguimiento", "convertido", "rechazado"]


def update_lead_status(username: str, new_status: str) -> bool:
    """Actualiza el estado de un lead identificándolo por usuario de Instagram."""
    if new_status not in VALID_STATUSES:
        print(f"[Leads Manager] Estado inválido: {new_status}")
        return False

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.usuario_instagram == username).first()
        if not lead:
            return False

        lead.estado = new_status
        lead.fecha_actualizacion = datetime.utcnow()
        if new_status == "convertido":
            lead.fecha_conversion = datetime.utcnow()

        db.add(lead)
        db.commit()
        print(f"[Leads Manager] Lead {username} actualizado a: {new_status}")
        return True
    finally:
        db.close()
