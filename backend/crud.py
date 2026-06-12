"""
Operaciones CRUD para la base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from backend.models import Lead, Conversacion, Cotizacion, EstadoLead, CalificacionLead
from backend.schemas import LeadCreate, LeadUpdate, ConversacionCreate, CotizacionCreate


# ═══════════════════════════════════════════════════════════════════════════
# LEADS
# ═══════════════════════════════════════════════════════════════════════════

def crear_lead(db: Session, lead: LeadCreate) -> Lead:
    """Crear un nuevo lead"""
    # Verificar si ya existe
    existente = db.query(Lead).filter(
        Lead.usuario_instagram == lead.usuario_instagram
    ).first()

    if existente:
        return existente

    nuevo_lead = Lead(**lead.dict())
    db.add(nuevo_lead)
    db.commit()
    db.refresh(nuevo_lead)
    return nuevo_lead


def obtener_lead(db: Session, lead_id: int) -> Lead:
    """Obtener un lead por ID"""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def obtener_lead_por_usuario(db: Session, usuario_instagram: str) -> Lead:
    """Obtener un lead por usuario de Instagram"""
    return db.query(Lead).filter(
        Lead.usuario_instagram == usuario_instagram
    ).first()


def obtener_todos_los_leads(db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
    """Obtener todos los leads con paginación"""
    return db.query(Lead).offset(skip).limit(limit).all()


def obtener_leads_por_estado(db: Session, estado: str, limit: int = 100) -> list[Lead]:
    """Obtener leads filtrados por estado"""
    return db.query(Lead).filter(
        Lead.estado == estado
    ).order_by(desc(Lead.fecha_creacion)).limit(limit).all()


def obtener_leads_recientes(db: Session, dias: int = 7) -> list[Lead]:
    """Obtener leads de los últimos N días"""
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    return db.query(Lead).filter(
        Lead.fecha_creacion >= fecha_limite
    ).order_by(desc(Lead.fecha_creacion)).all()


def actualizar_lead(db: Session, lead_id: int, lead_update: LeadUpdate) -> Lead:
    """Actualizar un lead"""
    db_lead = obtener_lead(db, lead_id)
    if not db_lead:
        return None

    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)

    db_lead.fecha_actualizacion = datetime.utcnow()
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def eliminar_lead(db: Session, lead_id: int) -> bool:
    """Eliminar un lead"""
    db_lead = obtener_lead(db, lead_id)
    if not db_lead:
        return False

    db.delete(db_lead)
    db.commit()
    return True


def cambiar_estado_lead(db: Session, lead_id: int, nuevo_estado: str) -> Lead:
    """Cambiar el estado de un lead"""
    db_lead = obtener_lead(db, lead_id)
    if not db_lead:
        return None

    db_lead.estado = nuevo_estado
    db_lead.fecha_actualizacion = datetime.utcnow()

    if nuevo_estado == EstadoLead.CONVERTIDO:
        db_lead.fecha_conversion = datetime.utcnow()

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


# ═══════════════════════════════════════════════════════════════════════════
# CONVERSACIONES
# ═══════════════════════════════════════════════════════════════════════════

def crear_conversacion(db: Session, conversacion: ConversacionCreate) -> Conversacion:
    """Crear una nueva conversación"""
    nueva_conv = Conversacion(**conversacion.dict())
    db.add(nueva_conv)
    db.commit()
    db.refresh(nueva_conv)
    return nueva_conv


def obtener_conversaciones_lead(db: Session, lead_id: int, limit: int = 50) -> list[Conversacion]:
    """Obtener todas las conversaciones de un lead"""
    return db.query(Conversacion).filter(
        Conversacion.lead_id == lead_id
    ).order_by(desc(Conversacion.fecha)).limit(limit).all()


def obtener_ultima_conversacion(db: Session, lead_id: int) -> Conversacion:
    """Obtener la última conversación de un lead"""
    return db.query(Conversacion).filter(
        Conversacion.lead_id == lead_id
    ).order_by(desc(Conversacion.fecha)).first()


# ═══════════════════════════════════════════════════════════════════════════
# COTIZACIONES
# ═══════════════════════════════════════════════════════════════════════════

def crear_cotizacion(db: Session, cotizacion: CotizacionCreate) -> Cotizacion:
    """Crear una nueva cotización"""
    nueva_cot = Cotizacion(**cotizacion.dict())

    # Calcular prima anual
    nueva_cot.prima_anual = nueva_cot.prima_mensual * 12

    db.add(nueva_cot)

    # Actualizar lead
    db_lead = obtener_lead(db, cotizacion.lead_id)
    if db_lead:
        db_lead.cotizacion_generada = True
        db_lead.monto_cotizado = nueva_cot.prima_mensual
        db.add(db_lead)

    db.commit()
    db.refresh(nueva_cot)
    return nueva_cot


def obtener_cotizaciones_lead(db: Session, lead_id: int) -> list[Cotizacion]:
    """Obtener todas las cotizaciones de un lead"""
    return db.query(Cotizacion).filter(
        Cotizacion.lead_id == lead_id
    ).order_by(desc(Cotizacion.fecha_generacion)).all()


def obtener_cotizacion(db: Session, cotizacion_id: int) -> Cotizacion:
    """Obtener una cotización por ID"""
    return db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()


# ═══════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════════════════

def obtener_estadisticas(db: Session) -> dict:
    """Obtener estadísticas generales del sistema"""
    total_leads = db.query(Lead).count()
    leads_nuevos = db.query(Lead).filter(Lead.estado == EstadoLead.NUEVO).count()
    leads_interesados = db.query(Lead).filter(Lead.estado == EstadoLead.INTERESADO).count()
    leads_en_seguimiento = db.query(Lead).filter(Lead.estado == EstadoLead.EN_SEGUIMIENTO).count()
    leads_convertidos = db.query(Lead).filter(Lead.estado == EstadoLead.CONVERTIDO).count()
    leads_rechazados = db.query(Lead).filter(Lead.estado == EstadoLead.RECHAZADO).count()

    cotizaciones = db.query(Cotizacion).all()
    cotizaciones_generadas = len(cotizaciones)
    cotizaciones_aceptadas = len([c for c in cotizaciones if c.estado == "aceptada"])
    inversion_total = sum([c.prima_anual for c in cotizaciones if c.estado == "aceptada"])

    tasa_conversion = (leads_convertidos / total_leads * 100) if total_leads > 0 else 0

    return {
        "total_leads": total_leads,
        "leads_nuevos": leads_nuevos,
        "leads_interesados": leads_interesados,
        "leads_en_seguimiento": leads_en_seguimiento,
        "leads_convertidos": leads_convertidos,
        "leads_rechazados": leads_rechazados,
        "cotizaciones_generadas": cotizaciones_generadas,
        "cotizaciones_aceptadas": cotizaciones_aceptadas,
        "inversion_total": inversion_total,
        "tasa_conversion": round(tasa_conversion, 2)
    }
