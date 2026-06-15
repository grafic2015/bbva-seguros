"""
Modelos SQLAlchemy para BBVA Seguros
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import os

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EstadoLead(str, enum.Enum):
    """Estados posibles de un lead"""
    NUEVO = "nuevo"
    INTERESADO = "interesado"
    EN_SEGUIMIENTO = "en_seguimiento"
    CONVERTIDO = "convertido"
    RECHAZADO = "rechazado"


class CalificacionLead(str, enum.Enum):
    """Calificación de interés del lead"""
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


class Lead(Base):
    """Modelo de Lead - Cliente potencial de Seguros"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Información básica
    nombre = Column(String(100), nullable=False)
    usuario_instagram = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)

    # Información del vehículo
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)
    año = Column(Integer, nullable=True)
    tipo_vehiculo = Column(String(50), nullable=True)  # Auto, Moto, etc
    patente = Column(String(20), nullable=True)

    # Ubicación
    localidad = Column(String(100), nullable=True)
    provincia = Column(String(100), nullable=True)

    # Estado
    estado = Column(Enum(EstadoLead), default=EstadoLead.NUEVO, index=True)
    calificacion = Column(Enum(CalificacionLead), default=CalificacionLead.MEDIO)

    # Comentario inicial
    comentario_inicial = Column(Text, nullable=True)

    # Cotización
    cotizacion_generada = Column(Boolean, default=False)
    monto_cotizado = Column(Float, nullable=True)

    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow, index=True)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_conversion = Column(DateTime, nullable=True)

    # Metadata
    fuente = Column(String(50), default="instagram")  # instagram, whatsapp, web, etc

    def __repr__(self):
        return f"<Lead {self.usuario_instagram} - {self.estado}>"


class Conversacion(Base):
    """Modelo de Conversación - Historial de chats con leads"""
    __tablename__ = "conversaciones"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)  # FK a leads.id

    # Mensaje
    mensaje_usuario = Column(Text, nullable=False)
    mensaje_respuesta = Column(Text, nullable=True)

    # Tipo
    tipo = Column(String(50), default="chat")  # chat, comentario_instagram, dm, etc

    # Timestamp
    fecha = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Conversacion lead_id={self.lead_id}>"


class Cotizacion(Base):
    """Modelo de Cotización - Presupuestos generados"""
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)

    # Detalles
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    año = Column(Integer, nullable=False)

    # Coberturas
    responsabilidad_civil = Column(Boolean, default=True)
    robo = Column(Boolean, default=True)
    colision = Column(Boolean, default=True)
    asistencia_24h = Column(Boolean, default=True)

    # Monto
    prima_mensual = Column(Float, nullable=False)
    prima_anual = Column(Float, nullable=False)
    descuento_porcentaje = Column(Float, default=35.0)

    # Estado
    estado = Column(String(50), default="generada")  # generada, enviada, aceptada, rechazada

    # Timestamp
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    fecha_validez = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Cotizacion lead_id={self.lead_id} ${self.prima_mensual}>"


class ComentarioProcesado(Base):
    """Registro de comentarios de Instagram ya respondidos (dedup por comentario)."""
    __tablename__ = "comentarios_procesados"

    id = Column(Integer, primary_key=True, index=True)
    comment_pk = Column(String(64), unique=True, nullable=False, index=True)
    usuario = Column(String(100), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ComentarioProcesado {self.comment_pk} - {self.usuario}>"


def crear_tablas():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


def obtener_db():
    """Dependencia para obtener sesión de BD en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Creando tablas...")
    crear_tablas()
    print("✅ Tablas creadas correctamente")
