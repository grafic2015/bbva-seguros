"""
Backend FastAPI — puerto 8000
BBVA Seguros: REST + WebSockets en tiempo real para la escena 3D.
"""

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from backend.events import bus

ROOT = Path(__file__).resolve().parent.parent

# Estado en memoria de los agentes (para el panel 3D)
_AGENTS: dict = {
    "instagram": {"status": "idle", "mensaje": "Esperando inicio...", "leads_encontrados": 0, "logs": []},
    "leads":     {"status": "idle", "mensaje": "Esperando inicio...", "total_leads": 0,      "logs": []},
}
_AGENT_TASKS: dict[str, Optional[asyncio.Task]] = {"instagram": None, "leads": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    bus.set_loop(asyncio.get_event_loop())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints REST ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def api_health():
    return {"ok": True, "status": "healthy"}


@app.get("/api/settings")
def api_get_settings():
    config.load_settings()
    return {
        "EMAIL_ADDRESS": config.EMAIL_ADDRESS,
        "CV_FILE_PATH":  config.CV_FILE_PATH,
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


@app.post("/api/instagram/monitor")
async def api_instagram_monitor():
    try:
        from agents.instagram_monitor_agent import monitor_instagram
        n = monitor_instagram()
        return {"ok": True, "new_leads": n}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/instagram/leads")
async def api_instagram_leads():
    try:
        from agents.instagram_monitor_agent import get_leads_summary
        summary = get_leads_summary()
        return summary
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/leads/summary")
async def api_leads_summary():
    try:
        from agents.leads_manager_agent import get_leads_summary
        summary = get_leads_summary()
        return summary
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/leads/all")
async def api_leads_all():
    try:
        from agents.leads_manager_agent import get_all_leads
        leads = get_all_leads()
        return {"leads": leads}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/leads/hot")
async def api_leads_hot():
    try:
        from agents.leads_manager_agent import get_hot_leads
        leads = get_hot_leads()
        return {"hot_leads": leads}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/leads/{username}/status")
async def api_update_lead_status(username: str, request: Request):
    try:
        data = await request.json()
        new_status = data.get("status")
        from agents.leads_manager_agent import update_lead_status
        success = update_lead_status(username, new_status)
        return {"ok": success}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/leads/{username}/note")
async def api_add_note_to_lead(username: str, request: Request):
    try:
        data = await request.json()
        note = data.get("note")
        from agents.leads_manager_agent import add_note_to_lead
        success = add_note_to_lead(username, note)
        return {"ok": success}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/leads/export/csv")
async def api_export_leads_csv():
    try:
        from agents.leads_manager_agent import export_leads_csv
        csv_content = export_leads_csv()
        return {"ok": True, "csv": csv_content}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    # Enviar snapshot inicial del estado de los agentes
    await ws.send_text(json.dumps({"type": "snapshot", "agents": _AGENTS}))
    q = await bus.subscribe()
    try:
        while True:
            event = await asyncio.wait_for(q.get(), timeout=30)
            await ws.send_text(json.dumps(event))
    except asyncio.TimeoutError:
        # Mantener viva la conexión con un ping
        try:
            await ws.send_text(json.dumps({"type": "ping"}))
        except Exception:
            pass
    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(q)


# ── /api/status ─────────────────────────────────────────────────────────────────

@app.get("/api/status")
async def api_status():
    """Snapshot de leads + estado de agentes para la carga inicial del frontend."""
    try:
        from agents.leads_manager_agent import get_all_leads
        leads = get_all_leads()
    except Exception:
        leads = []
    return {"leads": leads, "agents": _AGENTS}


# ── Control de Agentes ──────────────────────────────────────────────────────────

def _agent_log(agent_id: str, line: str):
    """Agrega una línea de log al agente y lo publica al bus."""
    state = _AGENTS[agent_id]
    state["logs"] = (state["logs"] + [line])[-50:]  # máximo 50 líneas
    bus.publish({"type": "agent_log",  "agent": agent_id, "line": line})
    bus.publish({"type": "agent_state", "agent": agent_id, "state": dict(state)})


async def _run_instagram_agent():
    """Tarea asíncrona que ejecuta el agente de Instagram."""
    _AGENTS["instagram"]["status"] = "running"
    _AGENTS["instagram"]["mensaje"] = "Monitoreando Instagram..."
    bus.publish({"type": "agent_state", "agent": "instagram", "state": dict(_AGENTS["instagram"])})
    try:
        _agent_log("instagram", "🚀 Iniciando monitoreo de comentarios en Instagram")
        from agents.instagram_monitor_agent import monitor_instagram
        nuevos = await asyncio.get_event_loop().run_in_executor(None, monitor_instagram)
        _AGENTS["instagram"]["leads_encontrados"] = _AGENTS["instagram"].get("leads_encontrados", 0) + nuevos
        _AGENTS["instagram"]["status"]  = "done"
        _AGENTS["instagram"]["mensaje"] = f"✅ Ciclo completado. {nuevos} leads nuevos."
        _agent_log("instagram", f"✅ Monitoreo completado — {nuevos} nuevos leads encontrados")
        # Publicar lista actualizada de leads
        from agents.leads_manager_agent import get_all_leads
        bus.publish({"type": "results", "leads": get_all_leads()})
    except Exception as e:
        _AGENTS["instagram"]["status"]  = "error"
        _AGENTS["instagram"]["mensaje"] = f"❌ Error: {e}"
        _agent_log("instagram", f"❌ Error: {e}")
    finally:
        bus.publish({"type": "agent_state", "agent": "instagram", "state": dict(_AGENTS["instagram"])})


async def _run_leads_agent():
    """Tarea asíncrona que ejecuta el agente de Leads."""
    _AGENTS["leads"]["status"]  = "running"
    _AGENTS["leads"]["mensaje"] = "Analizando y clasificando leads..."
    bus.publish({"type": "agent_state", "agent": "leads", "state": dict(_AGENTS["leads"])})
    try:
        _agent_log("leads", "🚀 Iniciando gestión y análisis de leads")
        from agents.leads_manager_agent import get_leads_summary, get_all_leads
        summary = await asyncio.get_event_loop().run_in_executor(None, get_leads_summary)
        total = summary.get("total_leads", 0)
        _AGENTS["leads"]["total_leads"] = total
        _AGENTS["leads"]["status"]  = "done"
        _AGENTS["leads"]["mensaje"] = f"✅ {total} leads gestionados. Conversión: {summary.get('conversion_rate', 0)}%"
        _agent_log("leads", f"📊 Resumen: {total} leads | Convertidos: {summary['by_status'].get('converted', 0)} | Tasa: {summary.get('conversion_rate', 0)}%")
        bus.publish({"type": "results", "leads": get_all_leads()})
    except Exception as e:
        _AGENTS["leads"]["status"]  = "error"
        _AGENTS["leads"]["mensaje"] = f"❌ Error: {e}"
        _agent_log("leads", f"❌ Error: {e}")
    finally:
        bus.publish({"type": "agent_state", "agent": "leads", "state": dict(_AGENTS["leads"])})


@app.post("/api/agents/{agent_id}/start")
async def api_agent_start(agent_id: str):
    """Inicia un agente de forma asíncrona."""
    if agent_id not in _AGENTS:
        return JSONResponse({"ok": False, "error": "Agente desconocido"}, status_code=404)
    if _AGENTS[agent_id]["status"] == "running":
        return {"ok": False, "error": "El agente ya está corriendo"}

    if agent_id == "instagram":
        _AGENT_TASKS["instagram"] = asyncio.create_task(_run_instagram_agent())
    elif agent_id == "leads":
        _AGENT_TASKS["leads"] = asyncio.create_task(_run_leads_agent())

    return {"ok": True, "message": f"Agente '{agent_id}' iniciado"}


@app.post("/api/agents/{agent_id}/stop")
async def api_agent_stop(agent_id: str):
    """Cancela la tarea del agente si está corriendo."""
    if agent_id not in _AGENTS:
        return JSONResponse({"ok": False, "error": "Agente desconocido"}, status_code=404)
    task = _AGENT_TASKS.get(agent_id)
    if task and not task.done():
        task.cancel()
    _AGENTS[agent_id]["status"]  = "idle"
    _AGENTS[agent_id]["mensaje"] = "Detenido manualmente."
    bus.publish({"type": "agent_state", "agent": agent_id, "state": dict(_AGENTS[agent_id])})
    return {"ok": True}


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
