# 🚀 Deploy en Oracle Cloud con Docker

## 📋 Requisitos

- Cuenta Oracle Cloud (gratis)
- Docker instalado en tu servidor
- Git en tu servidor

---

## 🔧 Paso 1: Conectarse al servidor Oracle

```bash
# Desde tu PC
ssh -i tu_clave.key ubuntu@tu_ip_oracle
```

---

## 📥 Paso 2: Clonar el repositorio

```bash
cd /home/ubuntu
git clone https://github.com/tu_usuario/Proyectos-Seguros-BBVA.git
cd Proyectos-Seguros-BBVA
```

---

## ⚙️ Paso 3: Configurar variables de entorno

Crear archivo `.env` en la raíz:

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-tu_key_aqui
INSTAGRAM_EMAIL=tu_email@instagram.com
INSTAGRAM_PASSWORD=tu_password
EOF
```

---

## 🐳 Paso 4: Levantar Docker Compose

```bash
# Construir y levantar
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ver contenedores
docker-compose ps
```

---

## ✅ Paso 5: Verificar que funciona

```bash
# Test del backend
curl http://localhost:8000/api/health

# Debería responder:
# {"ok":true,"agents":{...}}
```

---

## 🌍 Paso 6: Configurar firewall en Oracle Cloud

1. Ve a **Networking** → **Virtual Cloud Networks**
2. Abre puerto **8000** (TCP)
3. Tu URL será: `http://tu_ip_oracle:8000`

---

## 🔗 Paso 7: Conectar Frontend (Vercel)

En `frontend/vite.config.ts`:

```typescript
proxy: {
  "/api": "http://tu_ip_oracle:8000",
  "/ws": {
    target: "ws://tu_ip_oracle:8000",
    ws: true
  }
}
```

Deploy en Vercel y listo ✅

---

## 📊 Base de datos

PostgreSQL está corriendo en el contenedor:

```
Host: postgres
Puerto: 5432
Usuario: bbva_user
Contraseña: bbva_password_123
DB: bbva_seguros
```

Para conectarse desde tu PC:

```bash
psql -h tu_ip_oracle -U bbva_user -d bbva_seguros
```

---

## 🛠️ Comandos útiles

```bash
# Detener todo
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Entrar al contenedor
docker-compose exec backend bash

# Ejecutar migraciones (cuando tengas)
docker-compose exec backend python -m alembic upgrade head
```

---

## 💾 Backup de datos

```bash
# Respaldar PostgreSQL
docker-compose exec postgres pg_dump -U bbva_user bbva_seguros > backup.sql

# Restaurar
cat backup.sql | docker-compose exec -T postgres psql -U bbva_user -d bbva_seguros
```

---

## 🚨 Solución de problemas

### Backend no se levanta
```bash
docker-compose logs backend
```

### PostgreSQL no conecta
```bash
docker-compose logs postgres
```

### Puerto 8000 en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por otro
```

---

## 📱 Acceso remoto

Frontend → Vercel (gratis, tu dominio)
Backend → Oracle Cloud (gratis, IP pública)
DB → Oracle Cloud (gratis, interna)

**Total: $0** 🎉

¿Necesitas ayuda? 🚀
