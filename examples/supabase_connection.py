# ═════════════════════════════════════════════════════════════════════════
# Ejemplo: Conectar a Supabase desde la app
# ═════════════════════════════════════════════════════════════════════════
# Nota: Este es solo un ejemplo. La app ya usa SQLAlchemy + psycopg2

import os
from supabase import create_client, Client

# Obtener credenciales desde .env
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

# ═════════════════════════════════════════════════════════════════════════
# Opción 1: Cliente Admin (desde Backend)
# ═════════════════════════════════════════════════════════════════════════

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def crear_lead(username: str, comment: str) -> dict:
    """Crear un nuevo lead"""
    response = supabase.table("leads").insert({
        "username": username,
        "comment": comment,
        "status": "nuevo"
    }).execute()
    return response.data[0] if response.data else None


def obtener_leads(status: str = None) -> list:
    """Obtener leads, opcionalmente filtrados por estado"""
    query = supabase.table("leads").select("*")

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", desc=True).execute()
    return response.data


def actualizar_lead(lead_id: int, status: str) -> dict:
    """Actualizar estado de un lead"""
    response = supabase.table("leads").update({
        "status": status
    }).eq("id", lead_id).execute()
    return response.data[0] if response.data else None


def eliminar_lead(lead_id: int) -> bool:
    """Eliminar un lead"""
    response = supabase.table("leads").delete().eq("id", lead_id).execute()
    return len(response.data) > 0


# ═════════════════════════════════════════════════════════════════════════
# Opción 2: Realtime (Escuchar cambios en tiempo real)
# ═════════════════════════════════════════════════════════════════════════

def on_new_lead(payload):
    """Callback cuando se crea un nuevo lead"""
    print(f"✨ Nuevo lead: {payload['new']}")


def escuchar_nuevos_leads():
    """Configurar listener para nuevos leads"""
    supabase.realtime.on(
        'postgres_changes',
        {
            'event': 'INSERT',
            'schema': 'public',
            'table': 'leads'
        },
        callback=on_new_lead
    ).subscribe()

    # Mantener conexión abierta
    import time
    while True:
        time.sleep(1)


# ═════════════════════════════════════════════════════════════════════════
# Opción 3: Auth (Autenticación)
# ═════════════════════════════════════════════════════════════════════════

def signup(email: str, password: str) -> dict:
    """Registrar nuevo usuario"""
    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    return response.user if response.user else None


def signin(email: str, password: str) -> dict:
    """Login de usuario"""
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return response.session if response.session else None


def logout():
    """Logout"""
    supabase.auth.sign_out()


# ═════════════════════════════════════════════════════════════════════════
# Opción 4: Storage (Guardar archivos)
# ═════════════════════════════════════════════════════════════════════════

def subir_archivo(bucket: str, path: str, file_path: str) -> str:
    """Subir archivo a Supabase Storage"""
    with open(file_path, 'rb') as file:
        supabase.storage.from_(bucket).upload(path, file)

    # Obtener URL pública
    return supabase.storage.from_(bucket).get_public_url(path)


# ═════════════════════════════════════════════════════════════════════════
# Ejemplo de uso
# ═════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # Crear lead
    print("➕ Creando lead...")
    lead = crear_lead("@usuario123", "¡Quiero un seguro!")
    print(f"✅ Lead creado: {lead}")

    # Obtener todos los leads
    print("\n📋 Todos los leads:")
    leads = obtener_leads()
    for lead in leads:
        print(f"  - {lead['username']}: {lead['status']}")

    # Actualizar estado
    if lead:
        print(f"\n✏️  Actualizando lead {lead['id']}...")
        updated = actualizar_lead(lead['id'], "interesado")
        print(f"✅ Estado: {updated['status']}")

    # Obtener solo nuevos
    print("\n🆕 Leads nuevos:")
    new_leads = obtener_leads(status="nuevo")
    print(f"Total: {len(new_leads)}")
