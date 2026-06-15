"""
Autenticación simple por contraseña + token Bearer.

Flujo:
  1. El frontend hace POST /api/login con la contraseña.
  2. Si coincide con ADMIN_PASSWORD, se devuelve un token estable.
  3. El frontend envía ese token en `Authorization: Bearer <token>` en cada
     pedido (y como ?token=<token> en la conexión WebSocket).

El token deriva de la contraseña con SHA-256, así que es estable entre
reinicios sin necesidad de almacenar estado.
"""

import hashlib
import os

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
AUTH_SALT = os.getenv("AUTH_SALT", "bbva-seguros-salt-v1")

# La auth se activa solo si hay una contraseña configurada.
AUTH_ENABLED = bool(ADMIN_PASSWORD)

# Rutas accesibles sin token.
PUBLIC_PATHS = {
    "/",
    "/api/health",
    "/api/login",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/docs/oauth2-redirect",
}


def token_for(password: str) -> str:
    """Token determinístico derivado de la contraseña."""
    return hashlib.sha256(f"{password}::{AUTH_SALT}".encode()).hexdigest()


VALID_TOKEN = token_for(ADMIN_PASSWORD) if AUTH_ENABLED else ""


def check_password(password: str) -> bool:
    return AUTH_ENABLED and password == ADMIN_PASSWORD


def is_valid_token(token: str) -> bool:
    return AUTH_ENABLED and bool(token) and token == VALID_TOKEN
