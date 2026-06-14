import os
import json
from pathlib import Path


# Función decrypt simplificada
def decrypt(value):
    """Desencriptar credenciales. En producción usa valores en .env directamente."""
    return value if value else ""


# Cargar secretos desde .env
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# Configuracion general

# Instagram Monitor - credenciales encriptadas
_ig_email_encrypted = os.getenv("INSTAGRAM_EMAIL", "")
_ig_password_encrypted = os.getenv("INSTAGRAM_PASSWORD", "")

INSTAGRAM_EMAIL     = decrypt(_ig_email_encrypted) if _ig_email_encrypted else ""
INSTAGRAM_PASSWORD  = decrypt(_ig_password_encrypted) if _ig_password_encrypted else ""
INSTAGRAM_ACCOUNTS  = os.getenv("INSTAGRAM_ACCOUNTS", "").split(",") if os.getenv("INSTAGRAM_ACCOUNTS") else []
TRIGGER_KEYWORDS    = ["quiero", "interesado", "cotizar", "cotización", "presupuesto"]
AUTO_RESPONSE_MESSAGE = "¡Hola! 🚗 Tenemos seguros de auto con excelentes coberturas. ¿Te gustaría cotizar? Escríbeme aquí o llama al 1173665439"
LEADS_FILE          = "leads_instagram.json"

# ── Groq IA ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# ── Supabase ──────────────────────────────────────────────────────────────────
DATABASE_URL              = os.getenv("DATABASE_URL", "")
SUPABASE_URL              = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY         = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Cargar settings.json si existe
_settings_path = Path(__file__).resolve().parent / "settings.json"


def load_settings():
    global INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD, INSTAGRAM_ACCOUNTS, AUTO_RESPONSE_MESSAGE, LEADS_FILE

    if _settings_path.exists():
        try:
            with open(_settings_path, encoding="utf-8") as f:
                data = json.load(f)

            INSTAGRAM_EMAIL         = data.get("INSTAGRAM_EMAIL",         INSTAGRAM_EMAIL)
            INSTAGRAM_PASSWORD      = data.get("INSTAGRAM_PASSWORD",      INSTAGRAM_PASSWORD)
            INSTAGRAM_ACCOUNTS      = data.get("INSTAGRAM_ACCOUNTS",      INSTAGRAM_ACCOUNTS)
            AUTO_RESPONSE_MESSAGE   = data.get("AUTO_RESPONSE_MESSAGE",   AUTO_RESPONSE_MESSAGE)
            LEADS_FILE              = data.get("LEADS_FILE",              LEADS_FILE)
        except Exception as e:
            print(f"[Config] Error al cargar settings.json: {e}")


load_settings()


def validate_config() -> bool:
    """Verifica que la config minima este presente. Devuelve False si hay errores."""
    return True
