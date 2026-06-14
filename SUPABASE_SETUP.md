# 🚀 Configurar Supabase para BBVA Seguros

Supabase es PostgreSQL managed + autenticación + storage en la nube. **GRATIS para desarrollo**.

## 📋 ¿Por qué Supabase?

- ✅ PostgreSQL en la nube (sin gestionar servidores)
- ✅ Autenticación built-in (OAuth, Email, Passwords)
- ✅ API REST automática (sin escribir endpoints)
- ✅ Realtime subscriptions (sockets)
- ✅ Storage (para archivos)
- ✅ Free tier generoso (500MB DB, 50MB storage)
- ✅ No necesitas PostgreSQL local

---

## 🔧 Setup (5 minutos)

### 1. Crear Cuenta en Supabase

1. Ir a [app.supabase.com](https://app.supabase.com)
2. Click en **"Sign up"**
3. Usar email o GitHub

### 2. Crear Proyecto

1. Click en **"+ New project"**
2. **Project name:** `bbva-seguros`
3. **Database password:** Generar contraseña fuerte (copiar)
4. **Region:** Elegir la más cercana (ej: `US East (N. Virginia)`)
5. Click **"Create new project"** (esperar 2-3 min)

### 3. Obtener Credenciales

Una vez creado el proyecto:

1. Ir a **Settings > Database** (left sidebar)
2. Copiar **Connection string** bajo "Connection pooling" (Supabase)
   ```
   postgresql://postgres.xxxxxx:[PASSWORD]@aws-0-region.pooler.supabase.com:6543/postgres
   ```
3. Reemplazar `[PASSWORD]` con la contraseña que guardaste

4. Ir a **Settings > API**
5. Copiar:
   - **Project URL** → `SUPABASE_URL`
   - **anon public key** → `SUPABASE_ANON_KEY`
   - **service_role secret** → `SUPABASE_SERVICE_ROLE_KEY`

### 4. Configurar .env

```bash
# Edita .env
nano .env
```

Reemplaza:

```env
# DATABASE_URL de Supabase
DATABASE_URL=postgresql://postgres.xxxxxx:YourPassword@aws-0-region.pooler.supabase.com:6543/postgres

# Supabase API (opcional, para features avanzadas)
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Testear Conexión

```bash
# Instalar psql (si no está)
# Windows: choco install postgresql -y
# Mac:     brew install postgresql@15
# Linux:   apt-get install postgresql-client

# Conectar a Supabase
psql "postgresql://postgres.xxxxxx:YourPassword@aws-0-region.pooler.supabase.com:6543/postgres"

# Si funciona, verás el prompt: postgres=>
# Escribe: \q (para salir)
```

### 6. Crear Tablas en Supabase

#### Opción A: Usar SQL Editor (UI)

1. En Supabase Console, ir a **SQL Editor**
2. Click en **"New Query"**
3. Pegar este código:

```sql
-- Tabla de Leads
CREATE TABLE leads (
  id BIGSERIAL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  comment TEXT NOT NULL,
  status TEXT DEFAULT 'nuevo',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);

-- Habilitar RLS (Row Level Security)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Policy: anyone can read
CREATE POLICY "Enable read access for all users"
  ON leads FOR SELECT
  USING (true);

-- Policy: backend puede insert/update
CREATE POLICY "Enable insert for authenticated users"
  ON leads FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users"
  ON leads FOR UPDATE
  USING (true);
```

4. Click en **"Run"**

#### Opción B: Usar alembic (desde app)

Si tienes migraciones alembic:

```bash
# Local con postgres
docker-compose --profile local up -d

# Aplicar migraciones
docker-compose exec backend alembic upgrade head

# Verificar
docker-compose exec backend psql $DATABASE_URL -c "SELECT * FROM leads;"
```

Luego dump el schema:

```bash
pg_dump $DATABASE_URL --schema-only > schema.sql
```

Y aplicar en Supabase SQL Editor.

---

## 🚀 Usar Supabase en Desarrollo

### Opción 1: Sin PostgreSQL Local (recomendado)

```bash
# Solo levanta backend, usa Supabase
docker-compose up -d backend

# Ver logs
docker-compose logs -f backend

# API disponible en http://localhost:8000
```

### Opción 2: Con PostgreSQL Local (offline mode)

```bash
# Levanta postgres + backend local
docker-compose --profile local up -d

# DATABASE_URL apunta a localhost:5432
# (Cambia en .env para testing local)
```

---

## 🔐 Seguridad en Producción

### 1. Usar Service Role Key solo en backend

```python
from supabase import create_client

supabase = create_client(
    url=os.environ['SUPABASE_URL'],
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']  # NUNCA enviar al cliente
)
```

### 2. Habilitar RLS (Row Level Security)

```sql
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Solo el backend puede acceder
CREATE POLICY "backend_access"
  ON leads
  USING (current_setting('app.jwt_claims'->>'role') = 'service_role');
```

### 3. Conexión Pool (para producción)

Supabase incluye **PgBouncer** para pooling automático. El connection string ya lo usa:

```
postgresql://postgres.xxxx:pass@aws-0-region.pooler.supabase.com:6543/postgres
                                    ^^^^^^^^^^^^^^ Este es el pooler
```

### 4. Backups Automáticos

Supabase hace backups diarios. Accede en:
- **Settings > Backups**

---

## 🛠️ Funcionalidades Supabase (Bonus)

### Auth (Autenticación)

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Sign up
user = supabase.auth.sign_up(
    email="user@example.com",
    password="password123"
)

# Sign in
session = supabase.auth.sign_in_with_password(
    email="user@example.com",
    password="password123"
)
```

### Realtime (Sockets)

```python
# Escuchar cambios en tabla leads
supabase.realtime.on(
    'postgres_changes',
    {'event': 'INSERT', 'schema': 'public', 'table': 'leads'},
    callback=on_new_lead
).subscribe()
```

### Storage (Archivos)

```python
# Subir archivo
supabase.storage.from_('avatars').upload(
    path='public/avatar1.png',
    file=open('avatar.png', 'rb')
)
```

### Vectores (AI Embeddings)

```sql
-- Crear tabla con embeddings
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  embedding vector(1536)
);

-- Buscar por similitud
SELECT * FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

---

## 🐛 Troubleshooting

### ❌ "Password authentication failed"

```bash
# Verificar credenciales
# 1. Ir a Supabase > Settings > Database
# 2. Copiar password nuevamente (nunca se muestra de nuevo)
# 3. Reset password si es necesario
```

### ❌ "Connection timeout"

```bash
# Supabase está lento en algunos países
# Solución: Usar connection pooling (ya incluido)
# O cambiar region en Settings > Project Settings
```

### ❌ "psql: FATAL: too many connections"

```sql
-- Ver conexiones
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

-- El plan Free permite max 100 conexiones
-- Usa connection pooling (default)
```

### ❌ "Role 'postgres' does not exist"

Esto NO debería pasar en Supabase. Si pasa:
1. Resetea la password en Settings > Database
2. Genera nuevamente el connection string

---

## 📊 Monitoreo

### Ver Estadísticas

En Supabase Console:
- **Settings > Database** - Estadísticas de conexión
- **Settings > Billing** - Uso actual

### Ver Logs

```bash
# En Supabase > Logs
# Puedes ver: queries, auth events, storage, realtime
```

### Performance

```sql
-- Ver queries lentas
SELECT mean_exec_time, calls, query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 💰 Pricing

**Free Tier (perfecto para desarrollo):**
- 500 MB Database
- 1 GB Bandwidth
- Email auth
- 50 MB Storage
- 10MB Realtime messages

**Pro Tier ($25/mes):**
- 8 GB Database
- 250 GB Bandwidth
- Unlimited auth methods
- 100 GB Storage
- Unlimited Realtime

---

## 🚀 Deployment a Producción

Una vez configurado, el deploy sigue siendo igual:

```bash
# 1. Build imagen Docker
docker build -t bbva-seguros:latest .

# 2. Push a OCIR
./scripts/build-and-push-ocir.sh v1.0.0

# 3. Deploy a Oracle Cloud
./scripts/deploy-oci.sh

# Backend automáticamente usa DATABASE_URL de Supabase
# ✅ No necesitas gestionar PostgreSQL en OCI
```

---

## 📚 Recursos

- [Supabase Docs](https://supabase.com/docs)
- [SQL Reference](https://supabase.com/docs/guides/database/overview)
- [Python Client](https://supabase.com/docs/reference/python/introduction)
- [Realtime](https://supabase.com/docs/guides/realtime)

---

¡Listo para usar Supabase! 🎉
