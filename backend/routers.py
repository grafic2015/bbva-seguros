"""
Routers de FastAPI para Leads y Cotizaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.models import obtener_db
from backend.schemas import (
    LeadCreate, LeadUpdate, LeadResponse,
    ConversacionCreate, ConversacionResponse,
    CotizacionCreate, CotizacionResponse,
    StatsResponse, MessageResponse
)
from backend import crud

# ═══════════════════════════════════════════════════════════════════════════
# ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

leads_router = APIRouter(prefix="/api/leads", tags=["Leads"])
cotizaciones_router = APIRouter(prefix="/api/cotizaciones", tags=["Cotizaciones"])
conversaciones_router = APIRouter(prefix="/api/conversaciones", tags=["Conversaciones"])
stats_router = APIRouter(prefix="/api/stats", tags=["Estadísticas"])


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - LEADS
# ═══════════════════════════════════════════════════════════════════════════

@leads_router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def crear_lead(lead: LeadCreate, db: Session = Depends(obtener_db)):
    """Crear un nuevo lead"""
    nuevo_lead = crud.crear_lead(db, lead)
    return nuevo_lead


@leads_router.get("/", response_model=List[LeadResponse])
def obtener_leads(skip: int = 0, limit: int = 100, db: Session = Depends(obtener_db)):
    """Obtener todos los leads con paginación"""
    leads = crud.obtener_todos_los_leads(db, skip=skip, limit=limit)
    return leads


@leads_router.get("/estado/{estado}", response_model=List[LeadResponse])
def obtener_leads_por_estado(estado: str, db: Session = Depends(obtener_db)):
    """Obtener leads filtrados por estado"""
    if estado not in ["nuevo", "interesado", "en_seguimiento", "convertido", "rechazado"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    leads = crud.obtener_leads_por_estado(db, estado)
    return leads


@leads_router.get("/recientes/{dias}", response_model=List[LeadResponse])
def obtener_leads_recientes(dias: int = 7, db: Session = Depends(obtener_db)):
    """Obtener leads de los últimos N días"""
    leads = crud.obtener_leads_recientes(db, dias=dias)
    return leads


@leads_router.get("/{lead_id}", response_model=LeadResponse)
def obtener_lead(lead_id: int, db: Session = Depends(obtener_db)):
    """Obtener un lead por ID"""
    lead = crud.obtener_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@leads_router.get("/usuario/{usuario_instagram}", response_model=LeadResponse)
def obtener_lead_por_usuario(usuario_instagram: str, db: Session = Depends(obtener_db)):
    """Obtener un lead por usuario de Instagram"""
    lead = crud.obtener_lead_por_usuario(db, usuario_instagram)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@leads_router.put("/{lead_id}", response_model=LeadResponse)
def actualizar_lead(lead_id: int, lead_update: LeadUpdate, db: Session = Depends(obtener_db)):
    """Actualizar un lead"""
    lead = crud.actualizar_lead(db, lead_id, lead_update)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@leads_router.patch("/{lead_id}/estado/{nuevo_estado}", response_model=LeadResponse)
def cambiar_estado_lead(lead_id: int, nuevo_estado: str, db: Session = Depends(obtener_db)):
    """Cambiar el estado de un lead"""
    estados_validos = ["nuevo", "interesado", "en_seguimiento", "convertido", "rechazado"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado inválido")

    lead = crud.cambiar_estado_lead(db, lead_id, nuevo_estado)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@leads_router.delete("/{lead_id}", response_model=MessageResponse)
def eliminar_lead(lead_id: int, db: Session = Depends(obtener_db)):
    """Eliminar un lead"""
    success = crud.eliminar_lead(db, lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return {"ok": True, "mensaje": "Lead eliminado correctamente"}


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - CONVERSACIONES
# ═══════════════════════════════════════════════════════════════════════════

@conversaciones_router.post("/", response_model=ConversacionResponse, status_code=status.HTTP_201_CREATED)
def crear_conversacion(conversacion: ConversacionCreate, db: Session = Depends(obtener_db)):
    """Crear una nueva conversación"""
    # Verificar que el lead exista
    lead = crud.obtener_lead(db, conversacion.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    nueva_conv = crud.crear_conversacion(db, conversacion)
    return nueva_conv


@conversaciones_router.get("/lead/{lead_id}", response_model=List[ConversacionResponse])
def obtener_conversaciones_lead(lead_id: int, db: Session = Depends(obtener_db)):
    """Obtener todas las conversaciones de un lead"""
    conversaciones = crud.obtener_conversaciones_lead(db, lead_id)
    return conversaciones


@conversaciones_router.get("/lead/{lead_id}/ultima", response_model=ConversacionResponse)
def obtener_ultima_conversacion(lead_id: int, db: Session = Depends(obtener_db)):
    """Obtener la última conversación de un lead"""
    conversacion = crud.obtener_ultima_conversacion(db, lead_id)
    if not conversacion:
        raise HTTPException(status_code=404, detail="No hay conversaciones")
    return conversacion


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - COTIZACIONES
# ═══════════════════════════════════════════════════════════════════════════

@cotizaciones_router.post("/", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED)
def crear_cotizacion(cotizacion: CotizacionCreate, db: Session = Depends(obtener_db)):
    """Crear una nueva cotización"""
    # Verificar que el lead exista
    lead = crud.obtener_lead(db, cotizacion.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    nueva_cot = crud.crear_cotizacion(db, cotizacion)
    return nueva_cot


@cotizaciones_router.get("/lead/{lead_id}", response_model=List[CotizacionResponse])
def obtener_cotizaciones_lead(lead_id: int, db: Session = Depends(obtener_db)):
    """Obtener todas las cotizaciones de un lead"""
    cotizaciones = crud.obtener_cotizaciones_lead(db, lead_id)
    return cotizaciones


@cotizaciones_router.get("/{cotizacion_id}", response_model=CotizacionResponse)
def obtener_cotizacion(cotizacion_id: int, db: Session = Depends(obtener_db)):
    """Obtener una cotización por ID"""
    cotizacion = crud.obtener_cotizacion(db, cotizacion_id)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return cotizacion


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════════════════

@stats_router.get("/", response_model=StatsResponse)
def obtener_estadisticas(db: Session = Depends(obtener_db)):
    """Obtener estadísticas generales del sistema"""
    stats = crud.obtener_estadisticas(db)
    return stats


# ═══════════════════════════════════════════════════════════════════════════
# WEBHOOK DE INSTAGRAM/META
# ═══════════════════════════════════════════════════════════════════════════

webhook_router = APIRouter(prefix="/api/webhook", tags=["Webhooks"])


@webhook_router.get("/instagram")
def webhook_verify(
    hub_mode: str = None, 
    hub_challenge: str = None, 
    hub_verify_token: str = None
):
    """Verificar webhook de Meta"""
    print(f"Mode: {hub_mode}, Token: {hub_verify_token}, Challenge: {hub_challenge}")
    
    VERIFY_TOKEN = "bbva_token_123"
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN and hub_challenge:
        return int(hub_challenge)
    
    return {"error": "Invalid request"}

@webhook_router.post("/instagram/comment")
def webhook_instagram_comment(event: dict, db: Session = Depends(obtener_db)):
    """Webhook para recibir comentarios de Instagram"""
    try:
        username = event.get("username")
        comment_text = event.get("comment_text")

        if not username or not comment_text:
            raise HTTPException(status_code=400, detail="Datos incompletos")

        # Obtener o crear lead
        lead = crud.obtener_lead_por_usuario(db, username)
        if not lead:
            lead = crud.crear_lead(db, LeadCreate(
                nombre=username,
                usuario_instagram=username,
                comentario_inicial=comment_text
            ))

        # Guardar conversación
        crud.crear_conversacion(db, ConversacionCreate(
            lead_id=lead.id,
            mensaje_usuario=comment_text,
            tipo="comentario_instagram"
        ))

        return {"ok": True, "lead_id": lead.id, "mensaje": "Comentario procesado"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@webhook_router.post("/instagram/dm")
def webhook_instagram_dm(event: dict, db: Session = Depends(obtener_db)):
    """Webhook para recibir DMs de Instagram"""
    try:
        username = event.get("sender_username")
        message = event.get("message")

        if not username or not message:
            raise HTTPException(status_code=400, detail="Datos incompletos")

        # Obtener o crear lead
        lead = crud.obtener_lead_por_usuario(db, username)
        if not lead:
            lead = crud.crear_lead(db, LeadCreate(
                nombre=username,
                usuario_instagram=username
            ))

        # Guardar conversación
        crud.crear_conversacion(db, ConversacionCreate(
            lead_id=lead.id,
            mensaje_usuario=message,
            tipo="dm_instagram"
        ))

        return {"ok": True, "lead_id": lead.id, "mensaje": "DM procesado"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
