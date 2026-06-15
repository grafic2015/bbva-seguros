"""
Instagram Monitor Agent (instagrapi)
====================================
Flujo automático de captación de leads en Instagram:

  1. Monitorea los comentarios de los últimos posts de la(s) cuenta(s).
  2. Detecta comentarios con palabras clave ("quiero", etc.).
  3. Responde el comentario públicamente.
  4. Le envía un DM al autor con la primera pregunta (generada por Groq).
  5. Guarda el lead + la conversación en la base de datos (Supabase).
  6. En cada ciclo, también lee los DMs entrantes y los responde con Groq,
     calificando al lead (vehículo, año, localidad, etc.).

Requiere: instagrapi (pip install instagrapi) y credenciales en texto plano
(INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD en .env).

⚠️ Automatizar respuestas y DMs viola los términos de Instagram: hay riesgo de
bloqueo de la cuenta. Conviene usar una cuenta dedicada y mantener los límites
y demoras conservadores.
"""

import time
import random
from datetime import datetime
from pathlib import Path

from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    INSTAGRAM_ACCOUNTS,
    TRIGGER_KEYWORDS,
    IG_SESSION_FILE,
    IG_POSTS_TO_CHECK,
    IG_TOTP_SEED,
    IG_MAX_DM_PER_DAY,
    IG_MAX_NEW_PER_CYCLE,
    IG_ACTIVE_HOURS,
    IG_TIMEZONE,
)
from backend.models import SessionLocal, Lead, Conversacion, ComentarioProcesado

# Cliente global reutilizable (se loguea una sola vez por proceso)
_client = None


# ── Utilidades ───────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    print(f"[Instagram Monitor] {msg}")


def detect_trigger_keyword(text: str) -> bool:
    """¿El texto contiene alguna palabra clave de interés?"""
    text_lower = (text or "").lower()
    return any(keyword in text_lower for keyword in TRIGGER_KEYWORDS)


def _human_delay(a: float = 2.0, b: float = 6.0) -> None:
    """Pausa aleatoria para imitar comportamiento humano y reducir el riesgo de ban."""
    time.sleep(random.uniform(a, b))


def _en_horario() -> bool:
    """¿Estamos dentro del horario activo configurado (en IG_TIMEZONE)? Evita operar de madrugada."""
    try:
        from zoneinfo import ZoneInfo
        hora = datetime.now(ZoneInfo(IG_TIMEZONE)).hour
        ini, fin = IG_ACTIVE_HOURS.split("-")
        return int(ini) <= hora < int(fin)
    except Exception:
        return True


def _dms_enviados_hoy(db) -> int:
    """Cuenta los DMs (conversaciones) registrados hoy, para respetar el tope diario."""
    inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(Conversacion).filter(
        Conversacion.tipo == "dm_instagram",
        Conversacion.fecha >= inicio,
    ).count()


def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    return any(s in msg for s in ("429", "wait a few", "throttl", "rate limit", "too many"))


def _with_retry(fn, *args, retries: int = 2, base_wait: int = 45, **kwargs):
    """
    Ejecuta una llamada a la API reintentando ante rate limit (429) con backoff.
    Espera base_wait, 2*base_wait, ... entre reintentos. Si no es rate limit, re-lanza.
    """
    for intento in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if _is_rate_limit(e) and intento < retries:
                wait = base_wait * (intento + 1)
                _log(f"⏳ Rate limit (429): esperando {wait}s y reintentando ({intento + 1}/{retries})...")
                time.sleep(wait)
                continue
            raise


# ── Login con sesión persistente ─────────────────────────────────────────────

def get_client():
    """
    Devuelve un cliente de instagrapi logueado, reusando la sesión guardada
    (clave para no disparar challenges/verificaciones en cada arranque).
    """
    global _client
    if _client is not None:
        return _client

    try:
        from instagrapi import Client
    except ImportError:
        raise RuntimeError("Falta la dependencia: instalá 'instagrapi' (pip install instagrapi)")

    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        raise RuntimeError("Faltan INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD en el .env")

    cl = Client()
    cl.delay_range = [2, 5]  # demora interna entre requests

    def _do_login():
        """Login usando el código TOTP si hay una clave configurada (2FA automático)."""
        if IG_TOTP_SEED:
            code = cl.totp_generate_code(IG_TOTP_SEED)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, verification_code=code)
        else:
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    session_path = Path(IG_SESSION_FILE)
    if session_path.exists():
        try:
            cl.load_settings(session_path)
            cl.get_timeline_feed()  # valida que la sesión siga viva
            _log("Sesión reutilizada correctamente.")
            _client = cl
            return cl
        except Exception as e:
            _log(f"Sesión guardada inválida ({e}); re-logueando con 2FA automático...")
            # Conservar el device de la sesión vieja para que IG no sospeche
            try:
                old = cl.get_settings()
                cl.set_settings({})
                cl.set_uuids(old.get("uuids", {}))
            except Exception:
                pass

    # Login fresco (con TOTP si está configurado) y persistir la sesión
    _do_login()
    cl.dump_settings(session_path)
    _log("Login nuevo realizado y sesión guardada.")
    _client = cl
    return cl


# ── Groq: generar la próxima respuesta de la conversación ────────────────────

SISTEMA_VENTAS = """Sos un asesor de seguros de auto de BBVA, amable y profesional.
Tu objetivo es calificar al lead haciendo UNA pregunta por mensaje para reunir:
- tipo de vehículo (auto/moto) y marca/modelo
- año del vehículo
- localidad/provincia
- si ya tiene seguro hoy

Reglas:
- Mensajes cortos (máximo 2 oraciones), tono cercano y argentino.
- UNA sola pregunta por mensaje.
- Cuando ya tengas la info principal, agradecé y decile que un asesor lo
  contactará para pasarle la cotización con 35% de descuento.
- No inventes precios."""


def _generar_mensaje(historial: list[str], primer_contacto: bool = False) -> str:
    """Genera el próximo mensaje del asesor a partir del historial de la charla."""
    from backend.groq_client import generar_respuesta

    if primer_contacto:
        prompt = ("El usuario comentó 'quiero' en un post de seguros de auto. "
                  "Saludalo por DM, presentate brevemente y hacele la primera pregunta para calificarlo.")
    else:
        charla = "\n".join(historial[-10:])
        prompt = f"Esta es la conversación hasta ahora:\n{charla}\n\nGenerá tu próxima respuesta como asesor."

    respuesta = generar_respuesta(prompt, SISTEMA_VENTAS)
    return respuesta or "¡Hola! 🚗 Gracias por tu interés en seguros de auto BBVA. ¿Qué vehículo querés asegurar?"


# ── Persistencia de leads / conversaciones en la DB ───────────────────────────

def _get_or_create_lead(db, username: str, nombre: str, comentario: str) -> Lead:
    lead = db.query(Lead).filter(Lead.usuario_instagram == username).first()
    if lead:
        return lead
    lead = Lead(
        nombre=nombre or username,
        usuario_instagram=username,
        comentario_inicial=comentario,
        estado="nuevo",
        fuente="instagram",
        fecha_creacion=datetime.utcnow(),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _guardar_conversacion(db, lead_id: int, mensaje_usuario: str, mensaje_respuesta: str) -> None:
    db.add(Conversacion(
        lead_id=lead_id,
        mensaje_usuario=mensaje_usuario or "",
        mensaje_respuesta=mensaje_respuesta or "",
        tipo="dm_instagram",
        fecha=datetime.utcnow(),
    ))
    db.commit()


# ── 1) Procesar comentarios nuevos ────────────────────────────────────────────

def _procesar_comentarios(cl) -> int:
    """Revisa comentarios recientes, detecta keywords, responde y abre DM. Devuelve nuevos leads."""
    nuevos = 0
    db = SessionLocal()
    try:
        enviados_hoy = _dms_enviados_hoy(db)
        if enviados_hoy >= IG_MAX_DM_PER_DAY:
            _log(f"🛑 Tope diario de DMs alcanzado ({enviados_hoy}/{IG_MAX_DM_PER_DAY}). No se procesan comentarios.")
            return 0

        for cuenta in INSTAGRAM_ACCOUNTS:
            cuenta = cuenta.strip().lstrip("@")
            if not cuenta:
                continue
            try:
                user_id = _with_retry(cl.user_id_from_username, cuenta)
                medias = _with_retry(cl.user_medias, user_id, amount=IG_POSTS_TO_CHECK)
            except Exception as e:
                _log(f"No se pudieron leer posts de @{cuenta}: {e}")
                continue

            for media in medias:
                try:
                    comentarios = _with_retry(cl.media_comments, media.id, amount=50)
                except Exception as e:
                    _log(f"No se pudieron leer comentarios del post {media.id}: {e}")
                    continue

                for c in comentarios:
                    # Límites anti-ban: tope por ciclo y tope diario
                    if nuevos >= IG_MAX_NEW_PER_CYCLE:
                        _log(f"⏸️ Tope de leads por ciclo alcanzado ({IG_MAX_NEW_PER_CYCLE}). Continúa en el próximo ciclo.")
                        return nuevos
                    if enviados_hoy + nuevos >= IG_MAX_DM_PER_DAY:
                        _log(f"🛑 Tope diario de DMs alcanzado ({IG_MAX_DM_PER_DAY}).")
                        return nuevos

                    if not detect_trigger_keyword(c.text):
                        continue
                    autor = c.user.username
                    # Saltar comentarios de la propia cuenta
                    if autor.lower() == cuenta.lower():
                        continue
                    # Dedup POR COMENTARIO: si este comentario ya se respondió, saltarlo.
                    # (Si el usuario borra y vuelve a comentar, es un comentario nuevo y se procesa de nuevo.)
                    comment_pk = str(c.pk)
                    if db.query(ComentarioProcesado).filter(
                        ComentarioProcesado.comment_pk == comment_pk
                    ).first():
                        continue

                    nombre = getattr(c.user, "full_name", "") or autor
                    _log(f"🎯 Lead detectado: @{autor} — '{c.text[:40]}'")

                    # a) Responder el comentario públicamente
                    try:
                        cl.media_comment(media.id, "¡Genial! Te mandamos un DM con la info 📩",
                                         replied_to_comment_id=c.pk)
                    except Exception as e:
                        _log(f"No se pudo responder el comentario de @{autor}: {e}")
                    # Marcar el comentario como procesado para no responderlo dos veces
                    db.add(ComentarioProcesado(comment_pk=comment_pk, usuario=autor))
                    db.commit()
                    _human_delay()

                    # b) Crear el lead en la DB (no se duplica si ya existe)
                    lead = _get_or_create_lead(db, autor, nombre, c.text)

                    # c) Enviar DM inicial generado por Groq
                    mensaje = _generar_mensaje([], primer_contacto=True)
                    try:
                        cl.direct_send(mensaje, user_ids=[int(c.user.pk)])
                        _guardar_conversacion(db, lead.id, mensaje_usuario=c.text, mensaje_respuesta=mensaje)
                        nuevos += 1
                    except Exception as e:
                        _log(f"No se pudo enviar DM a @{autor}: {e}")
                    _human_delay(4, 9)
        return nuevos
    finally:
        db.close()


# ── 2) Responder DMs entrantes (conversación con Groq) ────────────────────────

def _procesar_thread(cl, db, th, es_pending: bool) -> bool:
    """Procesa un hilo de DM (principal o solicitud). Devuelve True si respondió."""
    otros = [u for u in th.users]
    if not otros:
        return False
    username = otros[0].username
    nombre = getattr(otros[0], "full_name", "") or username

    # En las solicitudes (pending) los mensajes vienen en el propio thread.
    if es_pending:
        mensajes = getattr(th, "messages", None) or []
    else:
        mensajes = cl.direct_messages(th.id, amount=5)
    if not mensajes:
        return False
    ultimo = mensajes[0]
    if str(ultimo.user_id) == str(cl.user_id):
        return False  # el último mensaje es nuestro: esperamos respuesta

    texto_usuario = (ultimo.text or "").strip()
    if not texto_usuario:
        return False

    lead = db.query(Lead).filter(Lead.usuario_instagram == username).first()
    if not lead:
        # Alguien nuevo escribiendo por DM: capturar solo si menciona la keyword.
        if not detect_trigger_keyword(texto_usuario):
            return False
        lead = _get_or_create_lead(db, username, nombre, texto_usuario)
        origen = "solicitud" if es_pending else "DM"
        _log(f"🎯 Lead nuevo por {origen}: @{username} — '{texto_usuario[:40]}'")

    # Si es una solicitud de mensaje, aprobarla para poder responder.
    if es_pending:
        try:
            cl.direct_pending_approve(th.id)
        except Exception as e:
            _log(f"No se pudo aprobar la solicitud de @{username}: {e}")

    # Reconstruir historial desde la DB
    convs = db.query(Conversacion).filter(
        Conversacion.lead_id == lead.id
    ).order_by(Conversacion.fecha.asc()).all()
    historial = []
    for cv in convs:
        if cv.mensaje_usuario:
            historial.append(f"Usuario: {cv.mensaje_usuario}")
        if cv.mensaje_respuesta:
            historial.append(f"Asesor: {cv.mensaje_respuesta}")
    historial.append(f"Usuario: {texto_usuario}")

    respuesta = _generar_mensaje(historial)
    cl.direct_send(respuesta, thread_ids=[th.id])
    _guardar_conversacion(db, lead.id, mensaje_usuario=texto_usuario, mensaje_respuesta=respuesta)

    if lead.estado == "nuevo":
        lead.estado = "interesado"
        db.add(lead)
        db.commit()
    return True


def _procesar_dms(cl) -> int:
    """
    Lee DMs entrantes (bandeja principal + solicitudes de mensaje) y los
    responde con Groq. Devuelve la cantidad de mensajes respondidos.
    - Si el remitente ya es lead: continúa la conversación.
    - Si es alguien nuevo y menciona una keyword ("quiero"...): lo captura
      como lead y arranca la conversación (aprobando la solicitud si hace falta).
    """
    respondidos = 0
    db = SessionLocal()
    try:
        enviados_hoy = _dms_enviados_hoy(db)
        try:
            principal = _with_retry(cl.direct_threads, amount=20)
        except Exception as e:
            _log(f"No se pudieron leer los DMs: {e}")
            principal = []
        try:
            pending = _with_retry(cl.direct_pending_inbox, amount=20)
        except Exception as e:
            _log(f"No se pudieron leer las solicitudes de mensaje: {e}")
            pending = []

        todos = [(t, False) for t in principal] + [(t, True) for t in pending]
        for th, es_pending in todos:
            if enviados_hoy + respondidos >= IG_MAX_DM_PER_DAY:
                _log(f"🛑 Tope diario de DMs alcanzado ({IG_MAX_DM_PER_DAY}). Se omiten respuestas restantes.")
                break
            try:
                if _procesar_thread(cl, db, th, es_pending):
                    respondidos += 1
                    _human_delay(3, 7)
            except Exception as e:
                _log(f"Error procesando un DM: {e}")
                continue
        return respondidos
    finally:
        db.close()


# ── Punto de entrada (lo invoca el panel 3D / el agente) ──────────────────────

def monitor_instagram() -> int:
    """
    Ejecuta un ciclo completo: procesa comentarios nuevos y responde DMs.
    Devuelve la cantidad de leads nuevos capturados.
    """
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        _log("⚠️  Falta configurar INSTAGRAM_USERNAME y INSTAGRAM_PASSWORD")
        return 0

    if not _en_horario():
        _log(f"😴 Fuera del horario activo ({IG_ACTIVE_HOURS}). Se omite el ciclo.")
        return 0

    _log("📸 Iniciando ciclo de monitoreo...")
    cl = get_client()

    nuevos = _procesar_comentarios(cl)
    respondidos = _procesar_dms(cl)
    _log(f"✅ Ciclo completo — {nuevos} leads nuevos, {respondidos} DMs respondidos")
    return nuevos


def process_comment(username: str, comment_text: str, post_url: str = "") -> dict:
    """
    Procesa un comentario individual (usado por el webhook /api/webhook/instagram/comment).
    Crea el lead en la DB si contiene palabras clave.
    """
    if not detect_trigger_keyword(comment_text):
        return {"captured": False}

    db = SessionLocal()
    try:
        if db.query(Lead).filter(Lead.usuario_instagram == username).first():
            return {"captured": False, "reason": "duplicate"}
        lead = _get_or_create_lead(db, username, username, comment_text)
        return {"captured": True, "lead_id": lead.id}
    finally:
        db.close()


def get_leads_summary() -> dict:
    """Resumen de leads (delegado al Leads Manager)."""
    from agents.leads_manager_agent import get_all_leads, get_leads_summary as _summary
    summary = _summary()
    return {
        "total_leads": summary["total_leads"],
        "total_interested": summary["by_status"].get("interesado", 0),
        "last_check": summary.get("last_update"),
        "leads": get_all_leads(),
    }
