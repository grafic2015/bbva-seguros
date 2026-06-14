# 🚗 Sistema Automatizado de Seguros Auto - BBVA

Sistema de 2 agentes que monitorea comentarios en Instagram, detecta la palabra "quiero" y envía automáticamente un DM con oferta de seguros auto con 35% de descuento.

**Stack:** Python FastAPI (Backend) + React (Frontend) + PostgreSQL (DB) + Oracle Cloud (Producción) + Vercel (Frontend)

## 📋 Estructura

```
Seguros BBVA/
├── agents/
│   ├── instagram_monitor_agent.py    # Agente 1: Monitorea comentarios e envía DM
│   └── leads_manager_agent.py        # Agente 2: Gestiona base de datos de leads
├── config.py                         # Configuración (credenciales, keywords, mensaje)
├── main.py                           # Ejecuta el sistema en CLI
├── server.py                         # Dashboard web (localhost:5000)
├── leads_history.json                # Base de datos de leads
├── .env                              # Credenciales (no compartir)
├── requirements.txt                  # Dependencias Python
└── README.md                         # Este archivo
```

## 🚀 Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Verificar que .env esté configurado correctamente
cat .env

# Debe contener:
# INSTAGRAM_EMAIL=ayudanexos@gmail.com
# INSTAGRAM_PASSWORD=Maranata26@
```

## 📱 Cómo funciona

### Agente 1: Instagram Monitor
- Monitorea los últimos 5 posts
- Busca comentarios con la palabra **"quiero"**
- Envía automáticamente un DM: `"¡Hola! mi nombre es Jose y 🚗 Tenemos seguros de auto con 35% de descuento. ¿Te interesa cotizar? Escríbeme aquí o llama al 1173665439"`
- Guarda los leads en `leads_history.json`

### Agente 2: Leads Manager
- Gestiona la base de datos de leads
- Actualiza estados: nuevo → interesado → convertido
- Genera estadísticas
- Alimenta el dashboard

## ⌨️ Comandos

### 🌐 Opción 1: Dashboard Web (RECOMENDADO)
```bash
python main_server.py
```
✅ Abre automáticamente `http://localhost:5000` en tu navegador
- Panel de control para ejecutar agentes
- Estadísticas en tiempo real
- Tabla de leads
- Auto-refresh cada 10 segundos
- Botones para ejecutar cada agente manualmente

### 📱 Opción 2: Monitoreo en terminal
```bash
python main.py
```
El sistema buscará comentarios cada 5 minutos. Presiona `Ctrl+C` para detener.

### Ver estadísticas en terminal
```bash
python -c "from agents.leads_manager_agent import LeadsManager; LeadsManager().print_dashboard()"
```

### Ver todos los leads en JSON
```bash
python -c "import json; data = json.load(open('leads_history.json')); print(json.dumps(data, indent=2, ensure_ascii=False))"
```

## 📊 Dashboard Web

Accede a `http://localhost:5000` para ver:

### 🎯 Paneles de Agentes
**📱 Instagram Monitor**
- Estado actual (idle, running, done, error)
- Cantidad de leads encontrados
- DMs enviados
- Botón para ejecutar monitoreo manual

**📊 Leads Manager**
- Total de leads en la base de datos
- Botón para actualizar estadísticas
- Mensaje de estado

### 📋 Tabla de Resultados
- Usuario (@username)
- Comentario que escribió
- Estado actual (nuevo, interesado, en_seguimiento, convertido, rechazado)
- Fecha de contacto

### ⚙️ Características
- ✅ **Auto-refresh** - Se actualiza cada 10 segundos (configurable)
- ✅ **Ejecución manual** - Botones para ejecutar cada agente cuando quieras
- ✅ **Estado en tiempo real** - Ve el estado actual de cada agente
- ✅ **Responsive** - Funciona en móvil, tablet y escritorio

## 📝 Estados de un Lead

- 🆕 **nuevo** - Acabamos de enviar DM
- 👍 **interesado** - Respondió favorablemente
- 🔄 **en_seguimiento** - Necesita recordatorio
- ✅ **convertido** - Compró el seguro
- ❌ **rechazado** - No interesado

## 🔒 Seguridad

- Las credenciales están en `.env` (NO COMPARTIR)
- Nunca publiques el `.env` en GitHub
- Usa contraseña de aplicación de Google, no la contraseña real

## 🛠️ Configuración

Edita `config.py` para:
- Cambiar las palabras clave a detectar: `TRIGGER_KEYWORDS`
- Cambiar el mensaje automático: `AUTO_RESPONSE_MESSAGE`
- Cambiar el intervalo de monitoreo: `CHECK_INTERVAL_MINUTES`

## 📞 Contacto

Teléfono/WhatsApp: **1173665439**

---

## 🚀 Deployment a Producción

### Prerequisitos

1. **Oracle Cloud Account** - [crear cuenta](https://www.oracle.com/cloud/free/)
2. **OCI CLI** - [instalar](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
3. **Docker** - [instalar](https://get.docker.com/)
4. **Terraform** (opcional) - [instalar](https://www.terraform.io/downloads.html)

### 🔐 Configuración de Secretos en GitHub

Para CI/CD automatizado, configura estos secrets en GitHub:

```
Settings > Secrets and variables > Actions > New repository secret
```

**Secretos requeridos:**
- `OCI_NAMESPACE` - Tu namespace en OCIR
- `OCI_USERNAME` - Usuario OCIR
- `OCI_AUTH_TOKEN` - Auth token de OCIR
- `OCI_PROVIDER_ID` - Provider ID para OIDC
- `OCI_WORKLOAD_IDENTITY_PROVIDER` - Workload identity provider
- `OCI_CONTAINER_ID` - ID del Container Instance (después de crear)
- `SLACK_WEBHOOK_URL` (opcional) - Para notificaciones

### 1️⃣ Build y Push a Oracle Container Registry

```bash
# Configurar variables en .env
cp .env.example .env
# Edita .env con tus datos reales

# Hacer el build y push a OCIR
./scripts/build-and-push-ocir.sh v1.0.0
```

**Qué sucede:**
1. Valida herramientas (Docker, Git, OCI CLI)
2. Construye imagen Docker optimizada
3. Autentica con Oracle Container Registry
4. Sube 3 tags: `latest`, `v1.0.0`, y timestamp

### 2️⃣ Deploy en Oracle Cloud Container Instance

#### Opción A: Usando script (rápido)

```bash
./scripts/deploy-oci.sh
```

#### Opción B: Usando Terraform (IaC)

```bash
cd deploy/terraform

# Inicializar Terraform
terraform init

# Crear terraform.tfvars
cat > terraform.tfvars << 'EOF'
oci_compartment_id = "ocid1.compartment.oc1..xxxxx"
container_image = "iad.ocir.io/namespace/bbva-seguros:latest"
openai_api_key = "sk-proj-xxxxx"
instagram_email = "tu_email@gmail.com"
instagram_password = "tu_app_password"
database_password = "StrongPassword123!"
secret_key = "your-secret-key-here"
EOF

# Aplicar configuración
terraform plan
terraform apply
```

#### Opción C: Oracle Cloud Console (UI)

1. Ir a **Container Instances**
2. Click en **Create container instance**
3. Seleccionar la imagen: `iad.ocir.io/namespace/bbva-seguros:latest`
4. Configurar variables de entorno desde `.env`
5. Asignar subnet pública con acceso a internet

### 3️⃣ CI/CD Automatizado con GitHub Actions

Cada push a `main` ejecuta automáticamente:

1. ✅ **Build** - Construye imagen Docker
2. ✅ **Test** - Ejecuta pytest en el backend
3. ✅ **Push** - Sube a Oracle Container Registry
4. ✅ **Deploy** - Actualiza Container Instance
5. ✅ **Healthcheck** - Verifica que la app esté sana
6. ✅ **Notificación** - Avisa en Slack

Ver workflow: `.github/workflows/deploy.yml`

### 🗄️ Base de Datos

#### Opción 1: PostgreSQL en Docker (desarrollo)

```bash
docker-compose up -d postgres
```

#### Opción 2: Oracle Autonomous Database (producción recomendado)

```bash
# 1. Crear Autonomous Database en OCI Console
# 2. Descargar wallet (zip con certificados)
# 3. Actualizar CONNECTION_STRING en .env
# 4. Actualizar requirements.txt para usar oracle-client

pip install oracledb
```

### 📊 Monitoreo en Producción

```bash
# Ver logs del container
oci container-instances container-instance get \
  --container-instance-id ocid1.containerinstance.oc1.iad.xxxxx

# Conectar a PostgreSQL desde local (port forward)
oci compute ssh --instance-id <id> \
  -c "ssh -L 5432:postgres:5432 ubuntu@instance"
```

### 🔒 Seguridad

✅ **Implementado:**
- Dockerfile multistage (imagen pequeña)
- Usuario no-root (uid 1000)
- Health checks
- Credenciales en variables de entorno
- CORS configurado
- Secret Key para sesiones

✅ **Recomendado:**
- Usar Oracle Vault para almacenar secretos
- Habilitar network security groups (NSG)
- Certificados SSL/TLS
- WAF (Web Application Firewall)
- Backups automáticos de DB

### ⚠️ Troubleshooting

**Container no inicia:**
```bash
# Ver logs
docker logs bbva_backend

# O en OCI:
oci container-instances container-instance get --container-instance-id <id>
```

**Connection timeout a BD:**
- Verificar security list permite puerto 5432
- Verificar VCN routing
- Usar `psql` para testear: `psql $DATABASE_URL`

**OCIR auth error:**
```bash
# Generar nuevo auth token
oci os object-meta-storage get-auth-token --max-valid-days 30

# Login manual
docker login iad.ocir.io
```

### 📚 Referencias

- [Oracle Cloud Documentation](https://docs.oracle.com/en-us/iaas/)
- [Container Instances](https://docs.oracle.com/en-us/iaas/Content/container-instances/home.htm)
- [OCIR](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryconcepts.htm)
- [Kubernetes (OKE)](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)

---

Hecho con ❤️ para BBVA Seguros Auto
