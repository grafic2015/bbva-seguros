"""
Leads Manager Agent
Gestiona los leads capturados desde Instagram.
Permite filtrar, actualizar estado, exportar datos y hacer seguimiento.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from config import LEADS_FILE


def load_leads() -> dict:
    """Carga el archivo de leads."""
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


def get_all_leads() -> List[dict]:
    """Obtiene todos los leads."""
    data = load_leads()
    return data.get("leads", [])


def get_lead_by_username(username: str) -> Optional[dict]:
    """Busca un lead por username."""
    leads = get_all_leads()
    for lead in leads:
        if lead.get("username", "").lower() == username.lower():
            return lead
    return None


def update_lead_status(username: str, new_status: str) -> bool:
    """
    Actualiza el estado de un lead.
    Estados: new, contacted, interested, converted, rejected
    """
    data = load_leads()
    valid_statuses = ["new", "contacted", "interested", "converted", "rejected"]

    if new_status not in valid_statuses:
        print(f"[Leads Manager] Estado invalido: {new_status}")
        return False

    for lead in data["leads"]:
        if lead.get("username", "").lower() == username.lower():
            lead["status"] = new_status
            lead["updated_at"] = datetime.now().isoformat()
            save_leads(data)
            print(f"[Leads Manager] Lead {username} actualizado a: {new_status}")
            return True

    return False


def add_note_to_lead(username: str, note: str) -> bool:
    """Agrega una nota a un lead."""
    data = load_leads()

    for lead in data["leads"]:
        if lead.get("username", "").lower() == username.lower():
            if "notes" not in lead:
                lead["notes"] = []
            lead["notes"].append({
                "text": note,
                "timestamp": datetime.now().isoformat()
            })
            save_leads(data)
            print(f"[Leads Manager] Nota agregada a {username}")
            return True

    return False


def get_leads_by_status(status: str) -> List[dict]:
    """Obtiene todos los leads con un estado especifico."""
    leads = get_all_leads()
    return [lead for lead in leads if lead.get("status") == status]


def get_leads_summary() -> dict:
    """Retorna un resumen estadistico de los leads."""
    data = load_leads()
    leads = data.get("leads", [])

    summary = {
        "total_leads": len(leads),
        "by_status": {
            "new": len([l for l in leads if l.get("status") == "new"]),
            "contacted": len([l for l in leads if l.get("status") == "contacted"]),
            "interested": len([l for l in leads if l.get("status") == "interested"]),
            "converted": len([l for l in leads if l.get("status") == "converted"]),
            "rejected": len([l for l in leads if l.get("status") == "rejected"]),
        },
        "conversion_rate": 0,
        "last_update": data.get("last_check"),
    }

    if len(leads) > 0:
        converted = summary["by_status"]["converted"]
        summary["conversion_rate"] = round((converted / len(leads)) * 100, 2)

    return summary


def export_leads_csv() -> str:
    """Exporta los leads a formato CSV."""
    leads = get_all_leads()

    if not leads:
        return ""

    csv_lines = ["username,comment,status,timestamp,post_url"]

    for lead in leads:
        username = lead.get("username", "").replace(",", ";")
        comment = lead.get("comment", "").replace(",", ";").replace("\n", " ")
        status = lead.get("status", "new")
        timestamp = lead.get("timestamp", "")
        post_url = lead.get("post_url", "").replace(",", ";")

        csv_line = f'"{username}","{comment}",{status},"{timestamp}","{post_url}"'
        csv_lines.append(csv_line)

    csv_content = "\n".join(csv_lines)

    # Guardar a archivo
    csv_path = Path("leads_export.csv")
    csv_path.write_text(csv_content, encoding="utf-8")

    print(f"[Leads Manager] Leads exportados a {csv_path}")
    return csv_content


def get_hot_leads() -> List[dict]:
    """Retorna los leads 'calientes' (nuevos y con interes potencial)."""
    leads = get_all_leads()
    return [
        l for l in leads
        if l.get("status") in ["new", "interested"]
    ]
