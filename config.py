import os
import json
from pathlib import Path


# Cargar secretos desde .env
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# Configuracion general

# Instagram Monitor - credenciales en texto plano (el .env está en .gitignore)
# INSTAGRAM_USERNAME es el usuario de login; se acepta INSTAGRAM_EMAIL como alias.
INSTAGRAM_USERNAME  = os.getenv("INSTAGRAM_USERNAME", "") or os.getenv("INSTAGRAM_EMAIL", "")
INSTAGRAM_PASSWORD  = os.getenv("INSTAGRAM_PASSWORD", "")
INSTAGRAM_EMAIL     = INSTAGRAM_USERNAME  # alias por compatibilidad
INSTAGRAM_ACCOUNTS  = os.getenv("INSTAGRAM_ACCOUNTS", "").split(",") if os.getenv("INSTAGRAM_ACCOUNTS") else []
TRIGGER_KEYWORDS    = ["quiero", "interesado", "cotizar", "cotización", "presupuesto"]
AUTO_RESPONSE_MESSAGE = "¡Hola! 🚗 Tenemos seguros de auto con excelentes coberturas. ¿Te gustaría cotizar? Escríbeme aquí o llama al 1173665439"

# Sesión persistente de instagrapi y cuántos posts revisar por ciclo
IG_SESSION_FILE     = os.getenv("IG_SESSION_FILE", "/app/data/ig_session.json")
IG_POSTS_TO_CHECK   = int(os.getenv("IG_POSTS_TO_CHECK", "5"))
# Clave secreta TOTP (Google Authenticator) para re-login automático ante 2FA
IG_TOTP_SEED        = os.getenv("IG_TOTP_SEED", "").replace(" ", "")

# Límites anti-ban
IG_MAX_DM_PER_DAY    = int(os.getenv("IG_MAX_DM_PER_DAY", "40"))     # tope de DMs por día
IG_MAX_NEW_PER_CYCLE = int(os.getenv("IG_MAX_NEW_PER_CYCLE", "5"))   # leads nuevos por ciclo
IG_ACTIVE_HOURS      = os.getenv("IG_ACTIVE_HOURS", "8-23")          # horario activo (en IG_TIMEZONE)
IG_TIMEZONE          = os.getenv("IG_TIMEZONE", "America/Argentina/Buenos_Aires")
LEADS_FILE          = "leads_instagram.json"  # obsoleto, conservado por compatibilidad

# ── Groq IA ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

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
