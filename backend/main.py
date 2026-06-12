"""
Backend FastAPI — puerto 8000
El frontend React (Vite :5173) hace proxy de /api y /ws hacia aquí.
"""

import asyncio
import io
import json
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from backend.events import bus

ROOT = Path(__file__).resolve().parent.parent


# ── Scheduler ──────────────────────────────────────────────────────────────────

async def _scheduler_loop() -> None:
    """Ejecuta el pipeline automáticamente según SCHEDULER_ENABLED y SCHEDULER_TIME."""
    last_run_date: str = ""
    while True:
        await asyncio.sleep(60)
        config.load_settings()
        if not getattr(config, "SCHEDULER_ENABLED", False):
            continue
        sched_time = getattr(config, "SCHEDULER_TIME", "09:00")
        now   = time.strftime("%H:%M")
        today = time.strftime("%Y-%m-%d")
        if now == sched_time and today != last_run_date:
            last_run_date = today
            msg = f"[Scheduler] ⏰ Ejecutando pipeline automático a las {now}"
            print(msg)
            bus.publish({"type": "agent_log", "agent": "busqueda", "line": msg})
            threading.Thread(target=_run_pipeline, args=(True, False), daemon=True).start()


async def _imap_auto_loop() -> None:
    """Revisa el IMAP periódicamente si IMAP_AUTO_ENABLED está activado."""
    while True:
        config.load_settings()
        interval = max(5, getattr(config, "IMAP_INTERVAL_MINUTES", 30))
        await asyncio.sleep(interval * 60)
        if getattr(config, "IMAP_AUTO_ENABLED", False):
            msg = f"[IMAP Auto] 📬 Revisando bandeja de entrada..."
            print(msg)
            bus.publish({"type": "agent_log", "agent": "extractor", "line": msg})
            threading.Thread(target=_run_imap, daemon=True).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    bus.set_loop(asyncio.get_running_loop())
    asyncio.create_task(_scheduler_loop())
    asyncio.create_task(_imap_auto_loop())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Estado compartido ──────────────────────────────────────────────────────────

_lock = threading.Lock()
_agents: dict[str, dict] = {
    "busqueda":  {"status": "idle", "mensaje": "", "total": 0,               "logs": []},
    "extractor": {"status": "idle", "mensaje": "", "total": 0, "con_email": 0, "logs": []},
    "enviador":  {"status": "idle", "mensaje": "", "enviados": 0,             "logs": []},
}

_chat_flow = {
    "state": "idle",
    "keywords": None,
    "location": None,
    "limit": None,
    "days": None
}


def _leer_json(filename: str) -> list:
    try:
        return json.loads((ROOT / filename).read_text(encoding="utf-8"))
    except Exception:
        return []


def _guardar_json(filename: str, data: Any) -> None:
    (ROOT / filename).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _ensure_ids(jobs: list) -> list:
    """Asigna un _id único a cada job que no tenga uno (necesario para el tracking pixel)."""
    for job in jobs:
        if not job.get("_id"):
            job["_id"] = str(uuid.uuid4())[:8]
    return jobs


def _set_agent(agent: str, **kwargs) -> None:
    with _lock:
        _agents[agent].update(kwargs)
        snap = dict(_agents[agent])
    bus.publish({"type": "agent_state", "agent": agent, "state": snap})
    bus.publish({
        "type":   "results",
        "jobs":   _leer_json("results_jobs.json"),
        "emails": _leer_json("results_emails.json"),
    })


def _notify_telegram(msg: str) -> None:
    try:
        from agents.telegram_agent import send_telegram_alert
        send_telegram_alert(msg)
    except Exception:
        pass


# ── Captura de logs del pipeline ───────────────────────────────────────────────

class _LogCapture(io.TextIOBase):
    def __init__(self, agent: str, original):
        self.agent    = agent
        self.original = original
        self._buf     = ""

    def write(self, text: str) -> int:
        self.original.write(text)
        self.original.flush()
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                with _lock:
                    logs = _agents[self.agent]["logs"]
                    logs.append(line)
                    if len(logs) > 200:
                        _agents[self.agent]["logs"] = logs[-200:]
                bus.publish({"type": "agent_log", "agent": self.agent, "line": line})
        return len(text)

    def flush(self):
        self.original.flush()


# ── Funciones del pipeline ─────────────────────────────────────────────────────

def _run_busqueda() -> list:
    orig, sys.stdout = sys.stdout, _LogCapture("busqueda", sys.stdout)
    try:
        config.load_settings()
        _set_agent("busqueda", status="running", mensaje="Buscando ofertas...", total=0, logs=[])
        from agents.job_search_agent import search_jobs
        import datetime

        jobs = search_jobs()

        # Cargar resultados anteriores y consolidar
        resultados_anteriores = _leer_json("results_jobs.json")

        # Agregar timestamp y keyword a cada resultado nuevo
        fecha_busqueda = datetime.datetime.now().isoformat()
        keyword_actual = config.JOB_KEYWORDS

        for job in jobs:
            job["search_date"] = fecha_busqueda
            job["search_keyword"] = keyword_actual

        # Consolidar: nuevos al inicio
        todos_jobs = jobs + resultados_anteriores

        # Deduplicar por URL (mantener el más reciente)
        vistos = {}
        jobs_dedup = []
        for job in todos_jobs:
            url = job.get("apply_url", "")
            if url not in vistos:
                vistos[url] = job
                jobs_dedup.append(job)

        _guardar_json("results_jobs.json", jobs_dedup[:1000])  # Máximo 1000

        _set_agent("busqueda", status="done", mensaje=f"{len(jobs)} ofertas nuevas ({len(jobs_dedup)} total)", total=len(jobs))
        return jobs
    except Exception as e:
        _set_agent("busqueda", status="error", mensaje=str(e))
        return []
    finally:
        sys.stdout = orig


def _run_extractor(jobs: list) -> list:
    orig, sys.stdout = sys.stdout, _LogCapture("extractor", sys.stdout)
    try:
        _set_agent("extractor", status="running", mensaje="Buscando correos...", total=len(jobs), con_email=0, logs=[])
        from agents.email_scraper_agent import extract_emails
        results = extract_emails(jobs)
        results = _ensure_ids(results)

        # Cargar resultados anteriores y consolidar
        resultados_anteriores = _leer_json("results_emails.json")
        todos_results = results + resultados_anteriores

        # Deduplicar por email + empresa (mantener el primero)
        vistos = {}
        results_dedup = []
        for r in todos_results:
            clave = (r.get("email", "").lower().strip(), r.get("company", "").lower().strip())
            if clave not in vistos:
                vistos[clave] = r
                results_dedup.append(r)

        _guardar_json("results_emails.json", results_dedup[:1000])  # Máximo 1000

        con_email = sum(1 for j in results if j.get("email"))
        _set_agent("extractor", status="done",
                   mensaje=f"{con_email} correos nuevos ({len(results_dedup)} total)",
                   total=len(results_dedup), con_email=con_email)
        return results
    except Exception as e:
        _set_agent("extractor", status="error", mensaje=str(e))
        return []
    finally:
        sys.stdout = orig


def _run_enviador(jobs_con_email: list) -> None:
    orig, sys.stdout = sys.stdout, _LogCapture("enviador", sys.stdout)
    try:
        _set_agent("enviador", status="running", mensaje="Enviando correos...", enviados=0, logs=[])
        from agents.email_sender_agent import send_emails
        send_emails(jobs_con_email)
        
        # Guardar el estado actualizado de los jobs en results_emails.json
        emails = _leer_json("results_emails.json")
        enviados_map = {j["_id"]: j for j in jobs_con_email if "_id" in j}
        for job in emails:
            jid = job.get("_id")
            if jid in enviados_map:
                job.update(enviados_map[jid])
        _guardar_json("results_emails.json", emails)
        
        enviados = sum(1 for j in jobs_con_email if j.get("sent"))
        _set_agent("enviador", status="done", mensaje=f"{enviados} correos enviados", enviados=enviados)
    except Exception as e:
        _set_agent("enviador", status="error", mensaje=str(e))
    finally:
        sys.stdout = orig


def _run_imap() -> int:
    orig, sys.stdout = sys.stdout, _LogCapture("extractor", sys.stdout)
    try:
        from agents.imap_reader_agent import check_replies
        n = check_replies()
        if n > 0:
            bus.publish({
                "type":   "results",
                "jobs":   _leer_json("results_jobs.json"),
                "emails": _leer_json("results_emails.json"),
            })
            _notify_telegram(f"📬 {n} respuesta(s) nueva(s) detectada(s) en tu bandeja de entrada.")
        return n
    except Exception as e:
        print(f"[IMAP] Error: {e}")
        return 0
    finally:
        sys.stdout = orig


def _run_followup() -> None:
    orig, sys.stdout = sys.stdout, _LogCapture("enviador", sys.stdout)
    try:
        from agents.email_sender_agent import send_followups
        emails = _leer_json("results_emails.json")
        send_followups(emails)
        _guardar_json("results_emails.json", emails)
        bus.publish({
            "type":   "results",
            "jobs":   _leer_json("results_jobs.json"),
            "emails": _leer_json("results_emails.json"),
        })
    except Exception as e:
        print(f"[Follow-up] Error: {e}")
    finally:
        sys.stdout = orig


def _run_pipeline(enviar: bool = False, dry_run: bool = False) -> None:
    config.DRY_RUN = dry_run
    with _lock:
        for ag in _agents:
            _agents[ag].update({"status": "idle", "mensaje": "", "logs": []})
    bus.publish({"type": "snapshot", "agents": {k: dict(v) for k, v in _agents.items()}})

    jobs = _run_busqueda()
    if not jobs:
        return
    results = _run_extractor(jobs)
    if enviar and results:
        con_email = [j for j in results if j.get("email")]
        if con_email:
            _run_enviador(con_email)

    bus.publish({
        "type":   "results",
        "jobs":   _leer_json("results_jobs.json"),
        "emails": _leer_json("results_emails.json"),
    })

    # Notificación Telegram al finalizar
    jobs_count  = len(_leer_json("results_jobs.json"))
    emails_data = _leer_json("results_emails.json")
    mail_count  = sum(1 for j in emails_data if j.get("email"))
    sent_count  = sum(1 for j in emails_data if j.get("sent"))
    _notify_telegram(
        f"✅ Pipeline completado:\n"
        f"• {jobs_count} ofertas encontradas\n"
        f"• {mail_count} correos extraídos\n"
        f"• {sent_count} CVs enviados"
    )


# ── Endpoints REST ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def api_health():
    return {"ok": True, "agents": {k: v["status"] for k, v in _agents.items()}}


@app.get("/api/state")
def api_state():
    import re
    config.load_settings()
    jobs = _leer_json("results_jobs.json")
    emails = _leer_json("results_emails.json")

    # Filtrar por palabras clave actuales si están configuradas
    current_keywords = (config.JOB_KEYWORDS or "").strip()
    if current_keywords:
        # Dividir por comas primero (frases exactas), luego por espacios
        frases = [f.strip().lower() for f in current_keywords.split(",") if f.strip()]
        if not frases:
            frases = [current_keywords.lower()]

        jobs_filtered = []
        for job in jobs:
            title = (job.get("job_title", "") or "").lower()

            # Verificar si el título coincide con AL MENOS una frase/palabra clave
            has_match = False
            for frase in frases:
                palabras = frase.split()
                if len(palabras) > 1:
                    # Es una frase: buscar coincidencia exacta
                    if frase in title:
                        has_match = True
                        break
                else:
                    # Es una palabra: buscar con límites de palabra
                    palabra = palabras[0]
                    if len(palabra) > 2:
                        if re.search(r'\b' + re.escape(palabra) + r'\b', title):
                            has_match = True
                            break

            if has_match:
                jobs_filtered.append(job)

        jobs = jobs_filtered

        # Filtrar emails correspondientes a los jobs filtrados
        job_urls = {j.get("apply_url") for j in jobs}
        emails = [e for e in emails if e.get("apply_url") in job_urls]

    return {
        "jobs":   jobs,
        "emails": emails,
    }


@app.get("/api/settings")
def api_get_settings():
    config.load_settings()
    return {
        "JOB_KEYWORDS":         config.JOB_KEYWORDS,
        "JOB_LOCATION":         config.JOB_LOCATION,
        "JOB_MAX_RESULTS":      config.JOB_MAX_RESULTS,
        "JOB_SOLO_HOY":         config.JOB_SOLO_HOY,
        "EMAIL_ADDRESS":        config.EMAIL_ADDRESS,
        "EMAIL_PASSWORD":       config.EMAIL_PASSWORD,
        "CV_FILE_PATH":         config.CV_FILE_PATH,
        "EMAIL_SUBJECT":        config.EMAIL_SUBJECT,
        "EMAIL_BODY":           config.EMAIL_BODY,
        "GEMINI_API_KEY":       config.GEMINI_API_KEY,
        "PUBLIC_URL":           config.PUBLIC_URL,
        "SCHEDULER_ENABLED":    config.SCHEDULER_ENABLED,
        "SCHEDULER_TIME":       config.SCHEDULER_TIME,
        "EXCLUDE_KEYWORDS":     config.EXCLUDE_KEYWORDS,
        "BLACKLIST_COMPANIES":  config.BLACKLIST_COMPANIES,
        "JOB_MODALITY":         config.JOB_MODALITY,
        "EMAIL_BATCH_SIZE":     config.EMAIL_BATCH_SIZE,
        "EMAIL_BATCH_PAUSE":    config.EMAIL_BATCH_PAUSE,
        "EMAIL_BUSINESS_HOURS": config.EMAIL_BUSINESS_HOURS,
        "EMAIL_BH_START":       config.EMAIL_BH_START,
        "EMAIL_BH_END":         config.EMAIL_BH_END,
        "DRY_RUN":              config.DRY_RUN,
        "TELEGRAM_TOKEN":       config.TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID":     config.TELEGRAM_CHAT_ID,
    }


@app.post("/api/settings")
async def api_save_settings(request: Request):
    data = await request.json()
    settings_path = ROOT / "settings.json"
    try:
        existing = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        existing = {}
    existing.update(data)
    settings_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    config.load_settings()
    return {"ok": True}


@app.post("/api/pipeline/start")
async def api_pipeline_start(enviar: bool = False, dry_run: bool = False):
    threading.Thread(target=_run_pipeline, args=(enviar, dry_run), daemon=True).start()
    return {"ok": True}


@app.post("/api/pipeline/imap")
async def api_pipeline_imap():
    threading.Thread(target=_run_imap, daemon=True).start()
    return {"ok": True}


@app.post("/api/pipeline/followup")
async def api_pipeline_followup():
    threading.Thread(target=_run_followup, daemon=True).start()
    return {"ok": True}


@app.post("/api/agents/{agent}/start")
async def api_agent_start(agent: str):
    if agent == "busqueda":
        threading.Thread(target=_run_busqueda, daemon=True).start()
    elif agent == "extractor":
        jobs = _leer_json("results_jobs.json")
        if not jobs:
            return JSONResponse({"ok": False, "error": "Ejecutá búsqueda primero"}, status_code=400)
        threading.Thread(target=_run_extractor, args=(jobs,), daemon=True).start()
    elif agent == "enviador":
        emails = _leer_json("results_emails.json")
        con_email = [j for j in emails if j.get("email")]
        if not con_email:
            return JSONResponse({"ok": False, "error": "No hay correos para enviar"}, status_code=400)
        threading.Thread(target=_run_enviador, args=(con_email,), daemon=True).start()
    else:
        return JSONResponse({"ok": False, "error": f"Agente desconocido: {agent}"}, status_code=404)
    return {"ok": True}


@app.post("/api/agents/{agent}/stop")
async def api_agent_stop(agent: str):
    if agent in _agents:
        _set_agent(agent, status="idle", mensaje="Detenido por el usuario")
    return {"ok": True}


@app.post("/api/agents/{agent}/chat")
async def api_agent_chat(agent: str, request: Request):
    data = await request.json()
    message = data.get("message", "")
    with _lock:
        ag = dict(_agents.get(agent, {}))
    reply = f"Estado actual: **{ag.get('status', 'idle')}**. {ag.get('mensaje', 'Esperando...')}"
    return {"reply": reply}


@app.post("/api/chat")
async def api_chat(request: Request):
    data = await request.json()
    raw_msg = data.get("message", "")
    msg  = raw_msg.lower().strip()

    with _lock:
        snap = {k: dict(v) for k, v in _agents.items()}

    replies = []

    # 1. Cancelar o salir del flujo
    if _chat_flow["state"] != "idle" and any(w in msg for w in ["cancelar", "salir", "detener"]):
        _chat_flow["state"] = "idle"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": "Configuración cancelada. Volví al estado normal.",
        })
        return {"replies": replies}

    # 2. Procesar flujo interactivo según el estado actual
    if _chat_flow["state"] == "waiting_keywords":
        _chat_flow["keywords"] = raw_msg.strip()
        _chat_flow["state"] = "waiting_location"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": f"Perfecto, buscaré **{raw_msg.strip()}**.\n\n¿En qué ciudad o país? (ej: *Buenos Aires*, *Córdoba*, *Argentina*)",
            "chips": ["Buenos Aires, Argentina", "Remoto", "Cancelar"]
        })
        return {"replies": replies}

    elif _chat_flow["state"] == "waiting_location":
        _chat_flow["location"] = raw_msg.strip()
        _chat_flow["state"] = "waiting_limit"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": f"Buscaré en **{raw_msg.strip()}**.\n\n¿Cuántas ofertas querés ver? (ej: *20*, *50*) — o escribí *saltear* para usar el valor por defecto (30).",
            "chips": ["20", "50", "Saltear", "Cancelar"]
        })
        return {"replies": replies}

    elif _chat_flow["state"] == "waiting_limit":
        limit = 30
        if "saltear" not in msg:
            try:
                import re
                nums = re.findall(r'\d+', msg)
                if nums:
                    limit = int(nums[0])
            except ValueError:
                pass
        _chat_flow["limit"] = limit
        _chat_flow["state"] = "waiting_days"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": "¿Querés buscar ofertas solo de hoy o de los últimos 15 días? (ej: *hoy*, *15 días*, *saltear* para defecto)",
            "chips": ["Hoy", "15 días", "Saltear", "Cancelar"]
        })
        return {"replies": replies}

    elif _chat_flow["state"] == "waiting_days":
        solo_hoy = False
        days_str = "últimos 30 días"
        
        if "hoy" in msg:
            solo_hoy = True
            days_str = "solo de hoy"
        elif "15" in msg:
            solo_hoy = False
            days_str = "últimos 15 días"
        elif "saltear" in msg:
            solo_hoy = False
            days_str = "últimos 30 días"

        _chat_flow["days"] = days_str

        # Guardar en settings.json
        settings_path = ROOT / "settings.json"
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
        existing.update({
            "JOB_KEYWORDS": _chat_flow["keywords"],
            "JOB_LOCATION": _chat_flow["location"],
            "JOB_MAX_RESULTS": _chat_flow["limit"],
            "JOB_SOLO_HOY": solo_hoy
        })
        settings_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        config.load_settings()

        _chat_flow["state"] = "waiting_confirm"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": (
                f"Listo, esto es lo que voy a buscar:\n\n"
                f"🔎 Qué: {_chat_flow['keywords']}\n"
                f"📍 Dónde: {_chat_flow['location']}\n"
                f"📊 Máximo: {_chat_flow['limit']} ofertas\n"
                f"📅 Cuándo: {days_str}\n\n"
                f"¿Arrancamos? (*sí / no*)"
            ),
            "chips": ["Sí", "No", "Cancelar"]
        })
        return {"replies": replies}

    elif _chat_flow["state"] == "waiting_confirm":
        _chat_flow["state"] = "idle"
        if msg.startswith("si") or msg.startswith("sí") or msg.startswith("arranca") or msg.startswith("dale"):
            threading.Thread(target=_run_pipeline, args=(True, False), daemon=True).start()
            replies.append({
                "speaker": "sistema", "name": "Sistema", "emoji": "⚙️", "color": "#8b949e",
                "text": "🚀 ¡Iniciando pipeline completo! El Buscador empezará a rastrear ofertas.",
            })
        else:
            replies.append({
                "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
                "text": "Búsqueda guardada pero no iniciada. Podés arrancar cuando quieras usando el panel.",
            })
        return {"replies": replies}

    # 3. Flujo normal de comandos
    if any(w in msg for w in ["hola", "hello", "hi", "buenos días", "buenos dias", "buenas tardes", "buenas noches"]):
        replies = [
            {
                "speaker": "sistema", "name": "Sistema", "emoji": "⚙️", "color": "#8b949e",
                "text": "👋 ¡Hola! Soy el centro de control. Puedo coordinar a los 3 agentes:",
            },
            {
                "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
                "text": "¡Hola! Yo busco ofertas de trabajo en la web.",
            },
            {
                "speaker": "extractor", "name": "Detective", "emoji": "🕵️", "color": "#ff9900",
                "text": "Yo investigo los sitios para encontrar correos de contacto.",
            },
            {
                "speaker": "enviador", "name": "Cartero", "emoji": "📬", "color": "#00cc00",
                "text": "¡Y yo envío tu CV personalizado a cada empresa!",
            },
            {
                "speaker": "sistema", "name": "Sistema", "emoji": "⚙️", "color": "#8b949e",
                "text": "Escribí **ayuda** para ver los comandos disponibles, o **iniciá búsqueda** para empezar.",
            }
        ]
    elif any(w in msg for w in ["buscar", "búsqueda", "iniciar", "empezar", "empecemos", "start", "empeza", "comenza busqueda", "comenza búsqueda"]):
        _chat_flow["state"] = "waiting_keywords"
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": "¡Genial! Vamos a configurar la búsqueda.\n\n¿Qué tipo de trabajo buscás? (ej: *desarrollador Python*, *diseñador gráfico*, *abogado*)",
            "chips": ["Soporte Técnico", "Desarrollador Python", "Cancelar"]
        })
    elif any(w in msg for w in ["correo", "email", "extractor", "detective"]):
        n = snap["extractor"].get("con_email", 0)
        replies.append({
            "speaker": "extractor", "name": "Detective", "emoji": "🕵️", "color": "#ff9900",
            "text": f"Tengo **{n}** correos encontrados. Para extraer más, primero hay que buscar ofertas.",
        })
    elif any(w in msg for w in ["enviar", "cartero", "postular", "cv"]):
        n = snap["enviador"].get("enviados", 0)
        replies.append({
            "speaker": "enviador", "name": "Cartero", "emoji": "📬", "color": "#00cc00",
            "text": f"Listo para enviar tu CV. Llevo **{n}** correos enviados hasta ahora.",
        })
    elif any(w in msg for w in ["estado", "status", "cómo", "como", "agentes"]):
        for ag_id, meta in [
            ("busqueda",  ("Buscador",  "🔎", "#00ccff")),
            ("extractor", ("Detective", "🕵️", "#ff9900")),
            ("enviador",  ("Cartero",   "📬", "#00cc00")),
        ]:
            st = snap[ag_id]
            replies.append({
                "speaker": ag_id, "name": meta[0], "emoji": meta[1], "color": meta[2],
                "text": f"Estado: **{st['status']}**. {st.get('mensaje', 'Esperando...')}",
            })
    elif any(w in msg for w in ["ayuda", "help", "qué", "que"]):
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": (
                "Puedo ayudarte con:\n"
                "- **Buscar** o **Comenza búsqueda** → Asistente interactivo para configurar\n"
                "- **Estado** → Ver estado de los agentes\n"
                "- **Correos** o **Envíos** → Info sobre estos agentes"
            ),
        })
    else:
        replies.append({
            "speaker": "busqueda", "name": "Buscador", "emoji": "🔎", "color": "#00ccff",
            "text": f'Recibí: "{data.get("message", "")}". Escribí **buscar** para configurar una nueva búsqueda o **ayuda** para ver los comandos.',
        })

    return {"replies": replies}


@app.post("/api/results/{job_id}/status")
async def api_update_status(job_id: str, request: Request):
    data = await request.json()
    new_status = data.get("status", "")
    emails = _leer_json("results_emails.json")
    updated = False
    for job in emails:
        if job.get("_id") == job_id:
            job["status"] = new_status
            updated = True
            break
    if updated:
        _guardar_json("results_emails.json", emails)
        bus.publish({"type": "results", "jobs": _leer_json("results_jobs.json"), "emails": emails})
    return {"ok": updated}


@app.get("/api/results/stats")
def api_stats():
    emails     = _leer_json("results_emails.json")
    jobs       = _leer_json("results_jobs.json")
    today      = time.strftime("%Y-%m-%d")
    daily_sent = 0
    try:
        history    = json.loads((ROOT / "sent_history.json").read_text(encoding="utf-8"))
        daily_sent = history.get("_daily", {}).get(today, 0)
    except Exception:
        pass
    return {
        "total_jobs":       len(jobs),
        "total_with_email": sum(1 for j in emails if j.get("email")),
        "total_sent":       sum(1 for j in emails if j.get("sent")),
        "total_opened":     sum(1 for j in emails if j.get("opened")),
        "total_failed":     sum(1 for j in emails if j.get("sent") is False and j.get("sent_error")),
        "daily_sent_today": daily_sent,
        "daily_limit":      450,
        "daily_remaining":  max(0, 450 - daily_sent),
    }


@app.delete("/api/cache/seen")
async def api_clear_seen():
    try:
        path = ROOT / "seen_jobs.json"
        path.write_text("[]", encoding="utf-8")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    return {"ok": True}


@app.delete("/api/cache/websites")
async def api_clear_websites():
    try:
        path = ROOT / "website_cache.json"
        path.write_text("{}", encoding="utf-8")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    return {"ok": True}


@app.delete("/api/results")
async def api_delete_results():
    try:
        _guardar_json("results_jobs.json", [])
        _guardar_json("results_emails.json", [])
        bus.publish({"type": "results", "jobs": [], "emails": []})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    return {"ok": True}


@app.get("/api/track/{job_id}")
async def api_track(job_id: str):
    try:
        emails = _leer_json("results_emails.json")
        for job in emails:
            if job.get("_id") == job_id and not job.get("opened"):
                job["opened"]    = True
                job["opened_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        _guardar_json("results_emails.json", emails)
        bus.publish({"type": "results", "jobs": _leer_json("results_jobs.json"), "emails": emails})
        _notify_telegram(f"👁 Alguien abrió tu correo (job_id: {job_id})")
    except Exception:
        pass
    pixel = bytes([
        137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82,
        0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0, 31, 21, 196, 137, 0, 0,
        0, 11, 73, 68, 65, 84, 8, 215, 99, 96, 0, 0, 0, 2, 0, 1, 232,
        221, 216, 193, 0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130,
    ])
    return Response(content=pixel, media_type="image/png")


@app.get("/dashboard")
async def dashboard():
    dash = ROOT / "dashboard" / "index.html"
    if dash.exists():
        return FileResponse(str(dash))
    return {"message": "Dashboard HTML no disponible"}


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = await bus.subscribe()

    with _lock:
        snap = {k: dict(v) for k, v in _agents.items()}
    await websocket.send_text(json.dumps({"type": "snapshot", "agents": snap}))
    await websocket.send_text(json.dumps({
        "type":   "results",
        "jobs":   _leer_json("results_jobs.json"),
        "emails": _leer_json("results_emails.json"),
    }))

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_text(json.dumps(event))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping"}))
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        bus.unsubscribe(queue)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
