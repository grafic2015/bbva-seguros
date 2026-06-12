#!/usr/bin/env python3
"""
Herramienta para encriptar credenciales de Instagram.

Uso:
  python encrypt_credentials.py

Ingresa tus credenciales y el script te dara los valores encriptados
para copiar en el archivo .env
"""

from secrets import encrypt


def main():
    print("=" * 60)
    print("ENCRIPTADOR DE CREDENCIALES - BBVA SEGUROS")
    print("=" * 60)
    print()
    print("Este script encripta tus credenciales de Instagram.")
    print("Los valores encriptados son seguros para guardar en .env")
    print()

    email = input("Email de Instagram: ").strip()
    password = input("Contraseña de Instagram: ").strip()

    if not email or not password:
        print("\n[Error] Email y contraseña son requeridos.")
        return

    encrypted_email = encrypt(email)
    encrypted_password = encrypt(password)

    print("\n" + "=" * 60)
    print("CREDENCIALES ENCRIPTADAS")
    print("=" * 60)
    print()
    print("Copia estas lineas en tu archivo .env:")
    print()
    print(f'INSTAGRAM_EMAIL={encrypted_email}')
    print(f'INSTAGRAM_PASSWORD={encrypted_password}')
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
