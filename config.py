import os
import json
from pathlib import Path

# ── Cargar secretos desde .env ────────────────────────────────────────────────
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# ── Búsqueda de trabajo ───────────────────────────────────────────────────────
JOB_KEYWORDS    = ""  # Se pide al iniciar main.py
JOB_LOCATION    = "Buenos Aires, Argentina"
JOB_MAX_RESULTS = 30
JOB_SOLO_HOY    = False

# Filtros de búsqueda
EXCLUDE_KEYWORDS   = []        # ej: ["senior", "líder", "5 años"]
BLACKLIST_COMPANIES = []       # ej: ["Empresa X", "Consultora Y"]
BLACKLIST_EMAILS   = []        # ej: ["minombre@ejemplo.com", "noreply@empresa.com"]
BLACKLIST_EMAIL_PATTERNS = []  # ej: ["ejemplo", "test", "demo"] — bloquea cualquier email que contenga estas palabras
JOB_MODALITY       = ""       # "" = todos | "remoto" | "hibrido" | "presencial"

# ── Correo saliente ───────────────────────────────────────────────────────────
SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 587
EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_ACCOUNTS = [] # Lista de diccionarios: [{"email": "...", "password": "..."}]

# ── CV ────────────────────────────────────────────────────────────────────────
CV_FILE_PATH = os.getenv("CV_FILE_PATH", "cv.pdf")

# ── Plantilla de correo ───────────────────────────────────────────────────────
EMAIL_SUBJECT = "Envío de CV - Emilio Pujalka – {job_title}"

EMAIL_BODY = """\
Estimado equipo de {company_name}:

Me pongo en contacto con ustedes para expresar mi interés en la posición de {job_title}.

Cuento con experiencia en soporte técnico, administración de sistemas Windows, Microsoft 365, Intune, redes y asistencia a usuarios. A lo largo de mi trayectoria he participado en tareas de implementación, mantenimiento y resolución de incidencias, brindando soporte tanto presencial como remoto.

Considero que mi perfil puede aportar valor a su equipo, combinando conocimientos técnicos, orientación al servicio y capacidad para resolver problemas de manera eficiente.

Adjunto mi currículum vitae para su consideración y quedo a disposición para ampliar cualquier información o coordinar una entrevista.

Saludos cordiales,

Emilio Pujalka
"""

# ── Envío en tandas ───────────────────────────────────────────────────────────
EMAIL_BATCH_SIZE   = 10       # emails por tanda
EMAIL_BATCH_PAUSE  = 300      # segundos entre tandas (5 minutos)
EMAIL_BUSINESS_HOURS = False  # True = solo enviar en horario laboral
EMAIL_BH_START     = 9        # hora inicio (ej: 9 = 09:00)
EMAIL_BH_END       = 18       # hora fin   (ej: 18 = 18:00)
EMAIL_RESEND_DAYS  = 30       # días mínimos entre envíos al mismo correo (0 = nunca reenviar)

# ── Modo Dry Run ──────────────────────────────────────────────────────────────
DRY_RUN = False               # True = ejecuta todo pero NO envía emails reales

# ── Funciones avanzadas ───────────────────────────────────────────────────────
GEMINI_API_KEY     = ""
PUBLIC_URL         = ""
SCHEDULER_ENABLED  = False
SCHEDULER_TIME     = "09:00"
TELEGRAM_TOKEN     = ""
TELEGRAM_CHAT_ID   = ""

# ── IMAP automático ───────────────────────────────────────────────────────────
IMAP_AUTO_ENABLED     = False
IMAP_INTERVAL_MINUTES = 30

# ── Cargar settings.json si existe ───────────────────────────────────────────
_settings_path = Path(__file__).resolve().parent / "settings.json"


def load_settings():
    global JOB_KEYWORDS, JOB_LOCATION, JOB_MAX_RESULTS, JOB_SOLO_HOY
    global EXCLUDE_KEYWORDS, BLACKLIST_COMPANIES, BLACKLIST_EMAILS, BLACKLIST_EMAIL_PATTERNS, JOB_MODALITY
    global EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_ACCOUNTS, CV_FILE_PATH, EMAIL_SUBJECT, EMAIL_BODY
    global EMAIL_BATCH_SIZE, EMAIL_BATCH_PAUSE, EMAIL_BUSINESS_HOURS, EMAIL_BH_START, EMAIL_BH_END, EMAIL_RESEND_DAYS
    global DRY_RUN, GEMINI_API_KEY, PUBLIC_URL, SCHEDULER_ENABLED, SCHEDULER_TIME
    global TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    global IMAP_AUTO_ENABLED, IMAP_INTERVAL_MINUTES

    if _settings_path.exists():
        try:
            with open(_settings_path, encoding="utf-8") as f:
                data = json.load(f)

            JOB_KEYWORDS        = data.get("JOB_KEYWORDS",        JOB_KEYWORDS)
            JOB_LOCATION        = data.get("JOB_LOCATION",        JOB_LOCATION)
            JOB_MAX_RESULTS     = data.get("JOB_MAX_RESULTS",     JOB_MAX_RESULTS)
            JOB_SOLO_HOY        = data.get("JOB_SOLO_HOY",        JOB_SOLO_HOY)
            EXCLUDE_KEYWORDS       = data.get("EXCLUDE_KEYWORDS",       EXCLUDE_KEYWORDS)
            BLACKLIST_COMPANIES    = data.get("BLACKLIST_COMPANIES",    BLACKLIST_COMPANIES)
            BLACKLIST_EMAILS       = data.get("BLACKLIST_EMAILS",       BLACKLIST_EMAILS)
            BLACKLIST_EMAIL_PATTERNS = data.get("BLACKLIST_EMAIL_PATTERNS", BLACKLIST_EMAIL_PATTERNS)
            JOB_MODALITY           = data.get("JOB_MODALITY",           JOB_MODALITY)
            EMAIL_ADDRESS       = data.get("EMAIL_ADDRESS",       EMAIL_ADDRESS)
            EMAIL_PASSWORD      = data.get("EMAIL_PASSWORD",      EMAIL_PASSWORD)
            EMAIL_ACCOUNTS      = data.get("EMAIL_ACCOUNTS",      EMAIL_ACCOUNTS)
            CV_FILE_PATH        = data.get("CV_FILE_PATH",        CV_FILE_PATH)
            EMAIL_SUBJECT       = data.get("EMAIL_SUBJECT",       EMAIL_SUBJECT)
            EMAIL_BODY          = data.get("EMAIL_BODY",          EMAIL_BODY)
            EMAIL_BATCH_SIZE    = data.get("EMAIL_BATCH_SIZE",    EMAIL_BATCH_SIZE)
            EMAIL_BATCH_PAUSE   = data.get("EMAIL_BATCH_PAUSE",   EMAIL_BATCH_PAUSE)
            EMAIL_BUSINESS_HOURS= data.get("EMAIL_BUSINESS_HOURS",EMAIL_BUSINESS_HOURS)
            EMAIL_BH_START      = data.get("EMAIL_BH_START",      EMAIL_BH_START)
            EMAIL_BH_END        = data.get("EMAIL_BH_END",        EMAIL_BH_END)
            EMAIL_RESEND_DAYS   = data.get("EMAIL_RESEND_DAYS",   EMAIL_RESEND_DAYS)
            DRY_RUN             = data.get("DRY_RUN",             DRY_RUN)
            GEMINI_API_KEY      = data.get("GEMINI_API_KEY",      GEMINI_API_KEY)
            PUBLIC_URL          = data.get("PUBLIC_URL",          PUBLIC_URL)
            SCHEDULER_ENABLED   = data.get("SCHEDULER_ENABLED",   SCHEDULER_ENABLED)
            SCHEDULER_TIME      = data.get("SCHEDULER_TIME",      SCHEDULER_TIME)
            TELEGRAM_TOKEN        = data.get("TELEGRAM_TOKEN",        TELEGRAM_TOKEN)
            TELEGRAM_CHAT_ID      = data.get("TELEGRAM_CHAT_ID",      TELEGRAM_CHAT_ID)
            IMAP_AUTO_ENABLED     = data.get("IMAP_AUTO_ENABLED",     IMAP_AUTO_ENABLED)
            IMAP_INTERVAL_MINUTES = data.get("IMAP_INTERVAL_MINUTES", IMAP_INTERVAL_MINUTES)
        except Exception as e:
            print(f"[Config] Error al cargar settings.json: {e}")


load_settings()


def validate_config() -> bool:
    """Verifica que la config mínima esté presente antes de arrancar. Devuelve False si hay errores."""
    errors = []
    if not EMAIL_ADDRESS:
        errors.append("EMAIL_ADDRESS no configurado (agregalo al .env)")
    if not EMAIL_PASSWORD:
        errors.append("EMAIL_PASSWORD no configurado (agregalo al .env)")
    if not os.path.isfile(CV_FILE_PATH):
        errors.append(f"CV no encontrado: {CV_FILE_PATH}")
    if errors:
        print("[Config] Errores de configuración:")
        for e in errors:
            print(f"  ✗ {e}")
        return False
    return True
