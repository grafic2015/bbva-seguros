"""
Esquemas Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class EstadoLeadSchema(str, Enum):
    NUEVO = "nuevo"
    INTERESADO = "interesado"
    EN_SEGUIMIENTO = "en_seguimiento"
    CONVERTIDO = "convertido"
    RECHAZADO = "rechazado"


class CalificacionLeadSchema(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


# ═══════════════════════════════════════════════════════════════════════════
# LEADS
# ═══════════════════════════════════════════════════════════════════════════

class LeadCreate(BaseModel):
    """Schema para crear un nuevo lead"""
    nombre: str
    usuario_instagram: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    localidad: Optional[str] = None
    comentario_inicial: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema para actualizar un lead"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    localidad: Optional[str] = None
    estado: Optional[EstadoLeadSchema] = None
    calificacion: Optional[CalificacionLeadSchema] = None


class LeadResponse(BaseModel):
    """Schema para responder con datos de lead"""
    id: int
    nombre: str
    usuario_instagram: str
    email: Optional[str]
    telefono: Optional[str]
    marca: Optional[str]
    modelo: Optional[str]
    año: Optional[int]
    localidad: Optional[str]
    estado: EstadoLeadSchema
    calificacion: CalificacionLeadSchema
    cotizacion_generada: bool
    monto_cotizado: Optional[float]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# CONVERSACIONES
# ═══════════════════════════════════════════════════════════════════════════

class ConversacionCreate(BaseModel):
    """Schema para crear una conversación"""
    lead_id: int
    mensaje_usuario: str
    mensaje_respuesta: Optional[str] = None
    tipo: str = "chat"


class ConversacionResponse(BaseModel):
    """Schema para responder con datos de conversación"""
    id: int
    lead_id: int
    mensaje_usuario: str
    mensaje_respuesta: Optional[str]
    tipo: str
    fecha: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# COTIZACIONES
# ═══════════════════════════════════════════════════════════════════════════

class CotizacionCreate(BaseModel):
    """Schema para crear una cotización"""
    lead_id: int
    marca: str
    modelo: str
    año: int
    responsabilidad_civil: bool = True
    robo: bool = True
    colision: bool = True
    asistencia_24h: bool = True
    prima_mensual: float
    descuento_porcentaje: float = 35.0


class CotizacionResponse(BaseModel):
    """Schema para responder con datos de cotización"""
    id: int
    lead_id: int
    marca: str
    modelo: str
    año: int
    prima_mensual: float
    prima_anual: float
    descuento_porcentaje: float
    estado: str
    fecha_generacion: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# WEBHOOK DE INSTAGRAM/META
# ═══════════════════════════════════════════════════════════════════════════

class InstagramCommentEvent(BaseModel):
    """Schema para evento de comentario en Instagram"""
    username: str
    comment_text: str
    post_id: str


class InstagramDMEvent(BaseModel):
    """Schema para evento de DM en Instagram"""
    sender_username: str
    message: str
    message_id: str


# ═══════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════════════════

class StatsResponse(BaseModel):
    """Schema para estadísticas del sistema"""
    total_leads: int
    leads_nuevos: int
    leads_interesados: int
    leads_en_seguimiento: int
    leads_convertidos: int
    leads_rechazados: int
    cotizaciones_generadas: int
    cotizaciones_aceptadas: int
    inversion_total: float
    tasa_conversion: float


# ═══════════════════════════════════════════════════════════════════════════
# RESPUESTAS GENÉRICAS
# ═══════════════════════════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    """Schema genérico para respuestas con mensaje"""
    ok: bool
    mensaje: str
    data: Optional[dict] = None
