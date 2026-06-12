"""
Backend FastAPI — puerto 8000
El frontend React (Vite :5173) hace proxy de /api hacia aquí.
"""

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config

ROOT = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
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


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
