"""
Aplicación FastAPI configurada para BBVA Seguros
Incluye: Leads, Cotizaciones, Conversaciones, WebHooks
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.models import crear_tablas
from backend.routers import leads_router, cotizaciones_router, conversaciones_router, stats_router, webhook_router

# Crear tablas en la BD al iniciar
crear_tablas()

app = FastAPI(
    title="BBVA Seguros API",
    description="API para gestión de leads y cotizaciones de seguros auto",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

app.include_router(leads_router)
app.include_router(cotizaciones_router)
app.include_router(conversaciones_router)
app.include_router(stats_router)
app.include_router(webhook_router)

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health_check():
    """Health check del servidor"""
    return {"ok": True, "status": "BBVA Seguros API running"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "app": "BBVA Seguros API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ═══════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
