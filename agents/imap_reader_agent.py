"""
Agente 4 — Lector IMAP.
Se conecta a la bandeja de entrada para detectar respuestas de las empresas
a las que les enviamos correos.
"""

import json
import time
from pathlib import Path
from imap_tools import MailBox, AND
import config

ROOT = Path(__file__).resolve().parent.parent
EMAILS_FILE = ROOT / "results_emails.json"

def check_replies() -> int:
    """Revisa la bandeja de entrada y marca como 'Respuesta' las ofertas que contestaron."""
    email_address = getattr(config, "EMAIL_ADDRESS", "")
    password = getattr(config, "EMAIL_PASSWORD", "")
    if not email_address or not password:
        print("[Lector IMAP] Faltan credenciales de correo en la configuración.")
        return 0

    if not EMAILS_FILE.exists():
        return 0

    try:
        results = json.loads(EMAILS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return 0

    # Crear diccionario de correos enviados a los que estamos esperando respuesta
    # (ignorando los que ya fueron rechazados o tienen oferta, etc., aunque para simplificar trackeamos todos)
    sent_emails = {
        r.get("email", "").lower().strip(): r 
        for r in results 
        if r.get("email") and r.get("sent")
    }

    if not sent_emails:
        return 0

    respuestas_nuevas = 0
    try:
        # Usamos imap_tools para conectarnos a Gmail
        with MailBox('imap.gmail.com').login(email_address, password) as mailbox:
            # Buscamos los correos recibidos en los últimos 30 días para no iterar toda la historia
            import datetime
            date_limit = datetime.date.today() - datetime.timedelta(days=30)
            
            for msg in mailbox.fetch(AND(date_gte=date_limit)):
                sender = msg.from_.lower().strip()
                # Si el remitente es uno de los que le mandamos mail
                if sender in sent_emails:
                    job = sent_emails[sender]
                    # Si el estado no es respuesta/entrevista, lo actualizamos
                    current_status = job.get("status", "Enviado")
                    if current_status not in ["Respuesta", "Entrevista", "Oferta", "Rechazado"]:
                        job["status"] = "Respuesta"
                        respuestas_nuevas += 1
                        print(f"[Lector IMAP] ¡Nueva respuesta detectada de {sender}!")

        # Guardar si hubo cambios
        if respuestas_nuevas > 0:
            EMAILS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            
    except Exception as e:
        print(f"[Lector IMAP] Error al conectar/leer IMAP: {e}")

    return respuestas_nuevas

if __name__ == "__main__":
    check_replies()
