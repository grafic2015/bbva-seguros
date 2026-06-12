"""
Agente 3 — Envío de correos con el CV.
- Si GEMINI_API_KEY está configurado, redacta un cuerpo de email personalizado con IA.
- Si PUBLIC_URL está configurado, añade un píxel de rastreo para detectar aperturas.
- Genera un ID único por oferta para el tracking.
- Envía emails en HTML para soportar el píxel de rastreo.
"""

import os
import sys
import json
import time
import uuid
import smtplib
import itertools
import requests
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import config

GMAIL_DAILY_LIMIT = 450

# La consola de Windows (cp1252) no soporta ✓/✗/⚠ → forzar UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HISTORY_FILE = Path(__file__).resolve().parent.parent / "sent_history.json"


def _load_history() -> dict:
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_history(history: dict) -> None:
    try:
        HISTORY_FILE.write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        print(f"[Agente 3] ⚠️  No se pudo guardar el historial: {e}")


def _read_cv_text() -> str:
    cv_path = getattr(config, "CV_FILE_PATH", "cv.pdf")
    if not os.path.isfile(cv_path):
        return ""
    try:
        import PyPDF2
        text = ""
        with open(cv_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return ""


def _generate_with_gemini(company: str, job_title: str, description: str) -> str:
    """Desactivado temporalmente por petición del usuario para ahorrar cuota de API."""
    return ""
    
    cv_text = _read_cv_text()
    perfil_default = (
        "Emilio Pujalka, con experiencia en soporte técnico, administración de sistemas "
        "Windows, Microsoft 365, Intune, redes y asistencia a usuarios."
    )
    perfil = f"Mi CV completo es el siguiente:\n{cv_text[:3000]}" if cv_text else f"Mi perfil: {perfil_default}"
    
    prompt = (
        f"Redactá un email de presentación profesional y personalizado en español "
        f"para postularme al puesto de '{job_title}' en la empresa '{company}'. "
        f"Descripción del puesto: {description[:1000] if description else 'No disponible'}.\n\n"
        f"{perfil}\n\n"
        f"INSTRUCCIONES CRÍTICAS:\n"
        f"- Hacé match exacto entre la descripción del puesto y mi CV. Mencioná 1 o 2 tecnologías/experiencias de mi CV que coincidan perfecto con lo que piden.\n"
        f"- El email debe ser breve (máximo 3 párrafos), formal pero cercano, sin asunto.\n"
        f"- Comenzar con 'Estimado equipo de {company}:' y terminar con 'Saludos cordiales,\nEmilio Pujalka'."
    )

    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        if text.strip():
            print(f"[Agente 3] ✨ Carta personalizada generada con Gemini para {company}")
            return text.strip()
    except Exception as e:
        print(f"[Agente 3] ⚠️  Gemini error: {e} — usando plantilla por defecto")
    return ""


def _guess_email_with_gemini(company: str) -> str:
    """Intenta averiguar el correo de RRHH de una empresa usando Gemini."""
    api_key = config.GEMINI_API_KEY
    if not api_key or not company.strip() or company.lower() in ["web:", ""]:
        return ""
    
    prompt = (
        f"¿Cuál es el correo electrónico público de recursos humanos, empleos, reclutamiento o contacto "
        f"de la empresa '{company}' en Argentina?\n"
        f"IMPORTANTE: Responde ÚNICAMENTE con la dirección de correo electrónico (ejemplo: rrhh@empresa.com).\n"
        f"Si no estás 100% seguro o la empresa no es conocida, responde exactamente con la palabra 'NOT_FOUND'. No agregues texto adicional."
    )
    
    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        ).strip()
        
        # Validación estricta para evitar alucinaciones con texto adicional
        if "@" in text and "NOT_FOUND" not in text and len(text.split()) == 1:
            print(f"[Agente 3] 🤖 Gemini encontró el email de {company}: {text}")
            return text
    except Exception as e:
        print(f"[Agente 3] ⚠️  Error al consultar email a Gemini para {company}: {e}")
    return ""


def _build_html(body_text: str, company: str, job_title: str, job_id: str) -> str:
    """Construye el HTML del email con el texto y el píxel de rastreo si está configurado."""
    public_url = getattr(config, "PUBLIC_URL", "").rstrip("/")
    
    paragraphs = "".join(
        f"<p style='margin:0 0 12px 0;'>{p}</p>"
        for p in body_text.split("\n")
        if p.strip()
    )
    
    tracking_pixel = ""
    if public_url:
        tracking_pixel = (
            f"<img src='{public_url}/api/track/{job_id}' "
            f"width='1' height='1' style='display:none;border:0;' alt='' />"
        )
    
    return f"""<!DOCTYPE html>
<html lang="es">
<body style="font-family:Arial,sans-serif;font-size:14px;color:#222;line-height:1.6;max-width:600px;margin:auto;padding:20px;">
{paragraphs}
{tracking_pixel}
</body>
</html>"""


def send_emails(jobs: list[dict]) -> None:
    """Envía un correo a cada empresa que tenga dirección de correo."""
    config.load_settings()

    dry_run = getattr(config, "DRY_RUN", False)
    if dry_run:
        print("[Agente 3] 🧪 MODO DRY RUN activado — no se envían emails reales")

    cv_path = config.CV_FILE_PATH
    if not dry_run and not os.path.isfile(cv_path):
        print(f"[Agente 3] ⚠️  No se encontró el CV en '{cv_path}'.")
        return

    if not dry_run and (not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD):
        print("[Agente 3] ⚠️  Configura EMAIL_ADDRESS y EMAIL_PASSWORD en Configuración.")
        return

    # Intentar completar correos faltantes usando manual_emails.json o Gemini
    manual_path = Path(__file__).resolve().parent.parent / "manual_emails.json"
    manual_emails = {}
    if manual_path.exists():
        try:
            manual_emails = json.loads(manual_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[Agente 3] ⚠️  No se pudo cargar manual_emails.json: {e}")

    # Bandera para saber si aprendimos nuevos correos y debemos guardar
    nuevos_correos = False

    for j in jobs:
        if not j.get("email") and j.get("company"):
            company_name = j.get("company", "")
            found_email = ""
            
            # 1. Buscar en manual_emails
            for m_comp, m_email in manual_emails.items():
                if m_comp.lower() in company_name.lower() or company_name.lower() in m_comp.lower():
                    found_email = m_email
                    break
            
            # 2. Si no se encontró, preguntarle a Gemini
            if not found_email and not dry_run:
                # Evitamos preguntar por cadenas muy genéricas
                if company_name.lower() not in ["confidencial", "importante empresa"]:
                    found_email = _guess_email_with_gemini(company_name)
                    if found_email:
                        manual_emails[company_name] = found_email
                        nuevos_correos = True
            
            if found_email:
                j["email"] = found_email

    # Si aprendimos correos nuevos, los guardamos en manual_emails.json
    if nuevos_correos:
        try:
            manual_path.write_text(json.dumps(manual_emails, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[Agente 3] ⚠️  No se pudo guardar manual_emails.json actualizado: {e}")

    # Filtrar correos en la lista negra (emails exactos y patrones)
    blacklist_emails = [e.strip().lower() for e in (config.BLACKLIST_EMAILS or [])]
    blacklist_patterns = [p.strip().lower() for p in (config.BLACKLIST_EMAIL_PATTERNS or [])]

    all_with_email = [j for j in jobs if j.get("email")]
    targets = []
    filtered_count = 0

    for j in all_with_email:
        email_lower = j.get("email", "").strip().lower()

        # Filtro 1: Email exacto en blacklist
        if email_lower in blacklist_emails:
            filtered_count += 1
            print(f"[Agente 3]   ⚠️  Filtrado (exacto): {email_lower}")
            continue

        # Filtro 2: Email contiene patrón en blacklist
        if any(pattern in email_lower for pattern in blacklist_patterns):
            filtered_count += 1
            print(f"[Agente 3]   ⚠️  Filtrado (patrón): {email_lower}")
            continue

        targets.append(j)

    if filtered_count > 0:
        print(f"[Agente 3] ⚠️  {filtered_count} correo(s) filtrado(s) por blacklist")

    if not targets:
        print("[Agente 3] No hay correos a los que enviar.")
        return

    batch_size  = getattr(config, "EMAIL_BATCH_SIZE",  10)
    batch_pause = getattr(config, "EMAIL_BATCH_PAUSE", 300)
    biz_hours   = getattr(config, "EMAIL_BUSINESS_HOURS", False)
    bh_start    = getattr(config, "EMAIL_BH_START", 9)
    bh_end      = getattr(config, "EMAIL_BH_END",   18)

    accounts = getattr(config, "EMAIL_ACCOUNTS", [])
    if not accounts and getattr(config, "EMAIL_ADDRESS", ""):
        accounts = [{"email": config.EMAIL_ADDRESS, "password": config.EMAIL_PASSWORD}]
        
    if not dry_run and not accounts:
        print("[Agente 3] ⚠️  No hay cuentas de correo configuradas.")
        return

    history = _load_history()
    enviados_ahora: set[str] = set()
    enviados_urls: set[str] = set()  # Rastrear URLs para deduplicación más precisa

    # Cargar URLs ya enviadas del historial
    for clave, datos in history.items():
        if clave.startswith("_") or "|" not in clave:
            continue
        apply_url = datos.get("apply_url", "")
        if apply_url:
            enviados_urls.add(apply_url.strip().lower())

    today = time.strftime("%Y-%m-%d")
    today_count = history.get("_daily", {}).get(today, 0)
    if today_count >= GMAIL_DAILY_LIMIT:
        print(f"[Agente 3] ⚠️  Límite diario de Gmail alcanzado ({GMAIL_DAILY_LIMIT} correos hoy). Abortando.")
        return

    def _wait_business_hours():
        """Espera hasta el inicio del horario laboral si es necesario."""
        if not biz_hours:
            return
        import datetime
        now = datetime.datetime.now()
        hora = now.hour
        if bh_start <= hora < bh_end:
            return
        # Calcular segundos hasta el inicio del próximo período
        if hora >= bh_end:
            # Esperar hasta mañana
            next_start = datetime.datetime.combine(
                now.date() + datetime.timedelta(days=1),
                datetime.time(bh_start)
            )
        else:
            next_start = datetime.datetime.combine(now.date(), datetime.time(bh_start))
        wait_s = (next_start - now).total_seconds()
        print(f"[Agente 3] 🕒 Fuera de horario laboral. Esperando {wait_s/3600:.1f}hs hasta las {bh_start}:00...")
        time.sleep(wait_s)

    if dry_run:
        print(f"[Agente 3] 🧪 Dry run: se enviarían {len(targets)} emails:")
        for t in targets:
            print(f"  → {t.get('email')} ({t.get('company', '?')}) — {t.get('job_title', '?')}")
            t["sent"] = False
            t["dry_run"] = True
        return

    print(f"[Agente 3] Conectando al servidor SMTP {config.SMTP_SERVER}:{config.SMTP_PORT} ...")

    try:
        import itertools
        account_cycle = itertools.cycle(accounts)
        
        # En vez de un solo smtp, creamos una conexión dinámica por cada email enviado
        # o reconectamos si falla. Pero para no abrir/cerrar por cada uno, podemos iterar
        
        for i, job in enumerate(targets):
            # Horario laboral
            _wait_business_hours()

            to_email  = job["email"]
            company   = job.get("company", "la empresa")
            job_title = job.get("job_title", config.JOB_KEYWORDS)
            description = job.get("description", "")
            apply_url = (job.get("apply_url") or "").strip().lower()
            clave = f"{to_email.strip().lower()}|{job_title.strip().lower()}"

            # DEDUPLICACIÓN 1: Verificar por URL (más preciso)
            if apply_url and apply_url in enviados_urls:
                job["sent"]    = True
                job["skipped"] = True
                print(f"[Agente 3] ↷ Omitido (URL duplicada): {to_email} ({company}) — {job_title}")
                continue

            # DEDUPLICACIÓN 2: Verificar por email + título
            if clave in history or clave in enviados_ahora:
                prev = history.get(clave, {}).get("sent_at", "")
                job["sent"]    = True
                job["skipped"] = True
                job["sent_at"] = prev or job.get("sent_at", "")

                # Verificar si está dentro del período de resend
                resend_days = getattr(config, "EMAIL_RESEND_DAYS", 30)
                if resend_days > 0 and clave in history and prev:
                    try:
                        import datetime
                        prev_dt = datetime.datetime.strptime(prev, "%Y-%m-%d %H:%M:%S")
                        now_dt = datetime.datetime.now()
                        days_ago = (now_dt - prev_dt).days
                        if days_ago < resend_days:
                            source = f"hace {days_ago} día(s)"
                            print(f"[Agente 3] ↷ Omitido ({source}): {to_email} ({company}) — {job_title}")
                            continue
                    except Exception:
                        pass

                source = "previamente" if clave in history else "en esta sesión"
                print(f"[Agente 3] ↷ Omitido ({source}): {to_email} ({company}) — {job_title}")
                continue

            if not job.get("_id"):
                job["_id"] = str(uuid.uuid4())[:8]
            job_id = job["_id"]

            gemini_body = _generate_with_gemini(company, job_title, description)
            body_text = gemini_body if gemini_body else config.EMAIL_BODY.format(
                company_name=company, job_title=job_title,
            )

            # Obtener cuenta para este email
            acc = next(account_cycle)
            from_email = acc["email"]
            acc_pass = acc["password"]

            msg = MIMEMultipart("mixed")
            msg["From"]    = from_email
            msg["To"]      = to_email
            msg["Subject"] = config.EMAIL_SUBJECT.format(job_title=job_title)

            html_content = _build_html(body_text, company, job_title, job_id)
            alt_part = MIMEMultipart("alternative")
            alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
            alt_part.attach(MIMEText(html_content, "html", "utf-8"))
            msg.attach(alt_part)

            with open(cv_path, "rb") as f:
                cv_data = f.read()
            cv_filename = os.path.basename(cv_path)
            part = MIMEBase("application", "octet-stream")
            part.set_payload(cv_data)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{cv_filename}"')
            msg.attach(part)

            # Verificar límite diario antes de cada envío
            if today_count >= GMAIL_DAILY_LIMIT:
                print(f"[Agente 3] ⚠️  Límite diario de Gmail alcanzado ({GMAIL_DAILY_LIMIT}). Deteniendo.")
                break

            sent_ok = False
            for attempt in range(3):
                try:
                    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.login(from_email, acc_pass)
                        smtp.sendmail(from_email, to_email, msg.as_string())
                    sent_ok = True
                    break
                except Exception as e:
                    if attempt < 2:
                        wait = 5 * (2 ** attempt)
                        print(f"[Agente 3] ⚠️  Intento {attempt+1}/3 fallido: {e}. Reintentando en {wait}s...")
                        time.sleep(wait)
                    else:
                        job["sent"]       = False
                        job["sent_error"] = str(e)
                        print(f"[Agente 3] ✗ Falló envío a {to_email} ({company}): {e}")

            if sent_ok:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                job["sent"]    = True
                job["sent_at"] = ts
                # Guardar en historial con URL para deduplicación futura
                history[clave] = {
                    "company": company,
                    "sent_at": ts,
                    "apply_url": apply_url  # Guardar URL para deduplicación más precisa
                }
                history.setdefault("_daily", {})[today] = today_count + 1
                today_count += 1
                enviados_ahora.add(clave)
                if apply_url:
                    enviados_urls.add(apply_url)
                print(f"[Agente 3] ✓ Correo enviado a {to_email} ({company}) [Via: {from_email}] [{today_count}/{GMAIL_DAILY_LIMIT} hoy]")

            # Pausa entre tandas
            if (i + 1) % batch_size == 0 and (i + 1) < len(targets):
                restantes = len(targets) - (i + 1)
                print(f"[Agente 3] ⏳ Tanda completa ({batch_size} emails). "
                      f"Pausa de {batch_pause}s antes de los {restantes} restantes...")
                time.sleep(batch_pause)

    except Exception as e:
        print(f"[Agente 3] ✗ Error crítico: {e}")

    _save_history(history)
    print("[Agente 3] Proceso de envío finalizado.")

def send_followups(jobs: list[dict]) -> None:
    """Revisa los correos enviados hace más de 5 días sin respuesta/apertura y manda follow-up."""
    config.load_settings()
    import datetime

    dry_run = getattr(config, "DRY_RUN", False)
    targets = []
    now = datetime.datetime.now()

    for j in jobs:
        if j.get("sent") and not j.get("opened") and j.get("status") in [None, "Enviado"]:
            sent_at = j.get("sent_at")
            if sent_at:
                try:
                    dt = datetime.datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S")
                    if (now - dt).days >= 5:
                        targets.append(j)
                except Exception:
                    pass

    if not targets:
        return

    print(f"[Agente 3] Preparando follow-ups para {len(targets)} empresas...")
    
    if dry_run:
        print("[Agente 3] 🧪 MODO DRY RUN activado — no se envían follow-ups reales")
        return

    accounts = getattr(config, "EMAIL_ACCOUNTS", [])
    if not accounts and getattr(config, "EMAIL_ADDRESS", ""):
        accounts = [{"email": config.EMAIL_ADDRESS, "password": config.EMAIL_PASSWORD}]

    if not accounts:
        print("[Agente 3] ⚠️  No hay cuentas de correo configuradas.")
        return

    try:
        account_cycle = itertools.cycle(accounts)
        
        for job in targets:
            to_email = job["email"]
            company = job.get("company", "la empresa")
            job_title = job.get("job_title", config.JOB_KEYWORDS)
            
            body_text = f"Estimado equipo de {company}:\n\nLes escribo brevemente para saber si tuvieron oportunidad de revisar el CV que les envié hace unos días para la posición de {job_title}.\nSigo muy interesado en la oportunidad.\n\nSaludos cordiales,\nEmilio Pujalka"
            
            acc = next(account_cycle)
            from_email = acc["email"]
            acc_pass = acc["password"]

            msg = MIMEMultipart("mixed")
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = f"Seguimiento: Postulación a {job_title}"
            
            html_content = _build_html(body_text, company, job_title, job.get("_id", ""))
            alt_part = MIMEMultipart("alternative")
            alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
            alt_part.attach(MIMEText(html_content, "html", "utf-8"))
            msg.attach(alt_part)
            
            try:
                with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(from_email, acc_pass)
                    smtp.sendmail(from_email, to_email, msg.as_string())
                job["status"] = "Seguimiento Enviado"
                print(f"[Agente 3] ✓ Follow-up enviado a {to_email} ({company}) [Via: {from_email}]")
            except Exception as e:
                print(f"[Agente 3] ✗ Falló follow-up a {to_email} ({company}): {e}")
                
            time.sleep(5)
                
    except Exception as e:
        print(f"[Agente 3] ✗ Error en follow-up: {e}")
