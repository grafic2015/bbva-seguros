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
)
from backend.models import SessionLocal, Lead, Conversacion

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
        for cuenta in INSTAGRAM_ACCOUNTS:
            cuenta = cuenta.strip().lstrip("@")
            if not cuenta:
                continue
            try:
                user_id = cl.user_id_from_username(cuenta)
                medias = cl.user_medias(user_id, amount=IG_POSTS_TO_CHECK)
            except Exception as e:
                _log(f"No se pudieron leer posts de @{cuenta}: {e}")
                continue

            for media in medias:
                try:
                    comentarios = cl.media_comments(media.id, amount=50)
                except Exception as e:
                    _log(f"No se pudieron leer comentarios del post {media.id}: {e}")
                    continue

                for c in comentarios:
                    if not detect_trigger_keyword(c.text):
                        continue
                    autor = c.user.username
                    # Saltar comentarios de la propia cuenta
                    if autor.lower() == cuenta.lower():
                        continue
                    # Dedup: si ya es lead, no re-procesar
                    if db.query(Lead).filter(Lead.usuario_instagram == autor).first():
                        continue

                    nombre = getattr(c.user, "full_name", "") or autor
                    _log(f"🎯 Lead detectado: @{autor} — '{c.text[:40]}'")

                    # a) Responder el comentario públicamente
                    try:
                        cl.media_comment(media.id, "¡Genial! Te mandamos un DM con la info 📩",
                                         replied_to_comment_id=c.pk)
                    except Exception as e:
                        _log(f"No se pudo responder el comentario de @{autor}: {e}")
                    _human_delay()

                    # b) Crear el lead en la DB
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

def _procesar_dms(cl) -> int:
    """Lee DMs entrantes de leads conocidos y los responde con Groq. Devuelve mensajes respondidos."""
    respondidos = 0
    db = SessionLocal()
    try:
        try:
            threads = cl.direct_threads(amount=20)
        except Exception as e:
            _log(f"No se pudieron leer los DMs: {e}")
            return 0

        for th in threads:
            try:
                otros = [u for u in th.users]
                if not otros:
                    continue
                username = otros[0].username
                lead = db.query(Lead).filter(Lead.usuario_instagram == username).first()
                if not lead:
                    continue  # solo conversamos con leads ya capturados

                mensajes = cl.direct_messages(th.id, amount=5)
                # El más reciente debe ser del usuario (no nuestro)
                if not mensajes:
                    continue
                ultimo = mensajes[0]
                if str(ultimo.user_id) == str(cl.user_id):
                    continue  # el último mensaje es nuestro: esperamos respuesta

                texto_usuario = (ultimo.text or "").strip()
                if not texto_usuario:
                    continue

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

                # Marcar como interesado al primer ida y vuelta
                if lead.estado == "nuevo":
                    lead.estado = "interesado"
                    db.add(lead)
                    db.commit()

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
