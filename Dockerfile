# ═════════════════════════════════════════════════════════════════════════
# STAGE 1: BUILDER - Instalar dependencias
# ═════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y compilar wheels
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ═════════════════════════════════════════════════════════════════════════
# STAGE 2: RUNTIME - Imagen final pequeña
# ═════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

# Información de la imagen
LABEL maintainer="BBVA Seguros"
LABEL description="BBVA Seguros Auto - Backend API"
LABEL version="1.0.0"

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar Python packages del builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Actualizar PATH
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Ejecutar aplicación con Uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
