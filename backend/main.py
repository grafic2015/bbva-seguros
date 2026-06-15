"""
Backend FastAPI unificado — puerto 8000
BBVA Seguros: REST + WebSockets en tiempo real.

Fuente de verdad ÚNICA: la base de datos (Supabase).
Sirve tanto el panel 3D (WebSocket + agentes) como la gestión de
leads / cotizaciones / conversaciones / estadísticas.
"""

import asyncio
import json
import os
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
from backend.models import crear_tablas
from backend.routers import (
    leads_router,
    cotizaciones_router,
    conversaciones_router,
    stats_router,
    webhook_router,
)

ROOT = Path(__file__).resolve().parent.parent

# Estado en memoria de los agentes (para el panel 3D)
_AGENTS: dict = {
    "instagram": {"status": "idle", "mensaje": "Esperando inicio...", "leads_encontrados": 0, "logs": []},
    "leads":     {"status": "idle", "mensaje": "Esperando inicio...", "total_leads": 0,      "logs": []},
}
_AGENT_TASKS: dict[str, Optional[asyncio.Task]] = {"instagram": None, "leads": None}

# Monitoreo automático del agente de Instagram (sin disparo manual)
IG_MONITOR_ENABLED  = os.getenv("IG_MONITOR_ENABLED", "true").lower() in ("1", "true", "yes")
IG_MONITOR_INTERVAL = int(os.getenv("IG_MONITOR_INTERVAL", "600"))  # segundos (default 10 min)


async def _scheduler_loop():
    """Ejecuta el ciclo del agente de Instagram periódicamente, en segundo plano."""
    await asyncio.sleep(30)  # esperar a que el server termine de arrancar
    while True:
        try:
            if _AGENTS["instagram"]["status"] != "running":
                await _run_instagram_agent()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Scheduler] Error en ciclo automático: {e}")
        await asyncio.sleep(IG_MONITOR_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegurar que las tablas existan en la base de datos
    try:
        crear_tablas()
    except Exception as e:
        print(f"[Startup] No se pudieron crear/verificar tablas: {e}")
    bus.set_loop(asyncio.get_event_loop())

    scheduler_task = None
    if IG_MONITOR_ENABLED:
        scheduler_task = asyncio.create_task(_scheduler_loop())
        print(f"[Scheduler] Monitoreo automático de Instagram activado (cada {IG_MONITOR_INTERVAL}s)")

    yield

    if scheduler_task:
        scheduler_task.cancel()


app = FastAPI(title="BBVA Seguros API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers de la base de datos ──────────────────────────────────────────────────
app.include_router(leads_router)
app.include_router(cotizaciones_router)
app.include_router(conversaciones_router)
app.include_router(stats_router)
app.include_router(webhook_router)


# ── Endpoints básicos ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"app": "BBVA Seguros API", "docs": "/docs", "redoc": "/redoc"}


@app.get("/api/health")
def api_health():
    return {"ok": True, "status": "healthy"}


@app.get("/api/settings")
def api_get_settings():
    config.load_settings()
    return {
        "EMAIL_ADDRESS": config.EMAIL_ADDRESS if hasattr(config, "EMAIL_ADDRESS") else "",
        "INSTAGRAM_ACCOUNTS": config.INSTAGRAM_ACCOUNTS,
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


# ── Actualización de estado por usuario (consumido por el panel 3D) ──────────────

@app.post("/api/leads/{username}/status")
async def api_update_lead_status(username: str, request: Request):
    """Actualiza el estado de un lead identificándolo por usuario de Instagram."""
    try:
        data = await request.json()
        new_status = data.get("estado") or data.get("status")
        from agents.leads_manager_agent import update_lead_status
        success = update_lead_status(username, new_status)
        if success:
            # Notificar a los clientes conectados con la lista actualizada
            from agents.leads_manager_agent import get_all_leads
            bus.publish({"type": "results", "leads": get_all_leads()})
        return {"ok": success}
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
            try:
                event = await asyncio.wait_for(q.get(), timeout=30)
                await ws.send_text(json.dumps(event))
            except asyncio.TimeoutError:
                # Mantener viva la conexión con un ping
                await ws.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        bus.unsubscribe(q)


# ── /api/status: snapshot inicial para el panel 3D ───────────────────────────────

@app.get("/api/status")
async def api_status():
    """Snapshot de leads (desde la DB) + estado de agentes para la carga inicial."""
    try:
        from agents.leads_manager_agent import get_all_leads
        leads = get_all_leads()
    except Exception:
        leads = []
    return {"ok": True, "status": "running", "leads": leads, "agents": _AGENTS}


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
        _agent_log("leads", f"📊 Resumen: {total} leads | Convertidos: {summary['by_status'].get('convertido', 0)} | Tasa: {summary.get('conversion_rate', 0)}%")
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
