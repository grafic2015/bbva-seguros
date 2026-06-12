"""
Modulo de encriptacion para credenciales sensibles.
Usa una clave derivada del hostname de la maquina (determinista pero segura localmente).
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import socket
import hashlib


def _get_encryption_key() -> bytes:
    """
    Genera una clave determinista basada en el hostname de la maquina.
    La misma maquina siempre genera la misma clave.
    """
    hostname = socket.gethostname()
    salt = "bbva-seguros"

    # Crear una clave hash determinista
    combined = f"{hostname}:{salt}"
    hash_obj = hashlib.sha256(combined.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())

    return key


def encrypt(plaintext: str) -> str:
    """Encripta un texto plano."""
    if not plaintext:
        return ""

    key = _get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt(ciphertext: str) -> str:
    """Desencripta un texto encriptado."""
    if not ciphertext:
        return ""

    try:
        key = _get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"[Secrets] Error al desencriptar: {e}")
        return ""


def encrypt_credentials(email: str, password: str) -> dict:
    """Encripta email y password, retorna diccionario con valores encriptados."""
    return {
        "email": encrypt(email),
        "password": encrypt(password),
    }


def decrypt_credentials(encrypted_dict: dict) -> dict:
    """Desencripta credenciales desde un diccionario encriptado."""
    return {
        "email": decrypt(encrypted_dict.get("email", "")),
        "password": decrypt(encrypted_dict.get("password", "")),
    }
