# 🚀 Guía Completa de Deployment - BBVA Seguros

Instrucciones detalladas para deployar la aplicación a Oracle Cloud.

## 📋 Tabla de Contenidos

1. [Setup Inicial](#setup-inicial)
2. [Configuración Local](#configuración-local)
3. [Build & Push a OCIR](#build--push-a-ocir)
4. [Deploy a Oracle Cloud](#deploy-a-oracle-cloud)
5. [CI/CD con GitHub Actions](#cicd-con-github-actions)
6. [Troubleshooting](#troubleshooting)

---

## Setup Inicial

### 1. Crear Oracle Cloud Account

1. Ir a [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
2. Crear cuenta
3. Verificar email
4. Acceder a [Oracle Cloud Console](https://www.oracle.com/cloud/sign-in/)

### 2. Instalar Herramientas Necesarias

#### Windows

```powershell
# Instalar Docker Desktop
choco install docker-desktop -y

# Instalar OCI CLI
choco install oci-cli -y

# Instalar Git
choco install git -y

# Instalar Terraform (opcional)
choco install terraform -y

# Instalar jq (para parsing JSON)
choco install jq -y
```

#### macOS

```bash
# Instalar Docker Desktop
brew install --cask docker

# Instalar OCI CLI
brew install oracle-cloud-cli

# Instalar Git
brew install git

# Instalar Terraform
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Instalar jq
brew install jq
```

#### Linux (Ubuntu/Debian)

```bash
# Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose -y

# OCI CLI
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash

# Git, Terraform, jq
sudo apt-get install git terraform jq -y
```

### 3. Configurar OCI CLI

```bash
# Iniciar setup
oci setup config

# Responde las preguntas:
# - User OCID: obtener de Profile > User Settings
# - Tenancy OCID: obtener de Profile > Tenancy
# - Region: us-ashburn-1 (o tu región)
# - Generate API Key: yes
```

Verifica que funciona:

```bash
oci os ns get
# Debería mostrar tu namespace
```

---

## Configuración Local

### 1. Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/bbva-seguros.git
cd bbva-seguros
```

### 2. Crear Archivo .env

```bash
cp .env.example .env
```

Edita `.env` con tus datos:

```env
# 🔑 Credenciales sensibles
ENVIRONMENT=production
POSTGRES_PASSWORD=GeneraContrasenaFuerte123!
OPENAI_API_KEY=sk-proj-tu-key-aqui
INSTAGRAM_EMAIL=tu_email@gmail.com
INSTAGRAM_PASSWORD=tu_app_password
SECRET_KEY=tu_secret_key_aqui

# ☁️  Oracle Cloud
OCI_REGION=us-ashburn-1
OCIR_REGION=iad
OCIR_NAMESPACE=tu_namespace_aqui
OCIR_REPO=bbva-seguros
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxx
OCI_VCN_ID=ocid1.vcn.oc1.iad.xxxxx
OCI_SUBNET_ID=ocid1.subnet.oc1.iad.xxxxx
```

### 3. Obtener Valores de Oracle Cloud

#### Obtener Compartment ID

```bash
oci iam compartment list \
  --compartment-id-in-subtree true \
  --query 'data[].{name:name,id:id}' \
  --output table
```

#### Crear VCN (si no existe)

```bash
# Listar VCNs existentes
oci network vcn list --compartment-id <COMPARTMENT_ID>

# O crear una nueva (más adelante con Terraform)
```

#### Obtener Namespace de OCIR

```bash
oci os ns get
# Output: {"data": "mynamespace"}
```

### 4. Generar Auth Token para OCIR

```bash
# En Oracle Cloud Console:
# 1. Click en tu nombre (arriba a la derecha)
# 2. My profile
# 3. Auth tokens
# 4. Generate Token
# 5. Copiar el token

# O vía CLI:
oci os object-meta-storage get-auth-token
```

---

## Build & Push a OCIR

### 1. Hacer Build Local

```bash
# Construir imagen
docker build -t bbva-seguros:latest .

# Probar localmente
docker-compose up -d
docker-compose logs -f backend
```

### 2. Push a Oracle Container Registry

```bash
# Hacer el script ejecutable
chmod +x scripts/build-and-push-ocir.sh

# Ejecutar el script
./scripts/build-and-push-ocir.sh v1.0.0
```

**Qué hace el script:**
- ✅ Valida Git, Docker, OCI CLI
- ✅ Construye imagen optimizada (multistage)
- ✅ Autentica con OCIR
- ✅ Sube 3 tags: `latest`, `v1.0.0`, `timestamp`

### 3. Verificar en OCIR

```bash
# Ver imágenes subidas
oci artifacts container image list \
  --repository-name bbva-seguros \
  --compartment-id <COMPARTMENT_ID>
```

O en **Oracle Cloud Console > Container Registries**

---

## Deploy a Oracle Cloud

### Opción 1: Script Rápido (Recomendado)

```bash
chmod +x scripts/deploy-oci.sh
./scripts/deploy-oci.sh
```

**Output esperado:**
```
✅ Deploy completado exitosamente!

📊 Información de la instancia:
  IP Pública: 123.45.67.89
  API: http://123.45.67.89:8000
  API Docs: http://123.45.67.89:8000/docs
```

### Opción 2: Infrastructure as Code (Terraform)

#### Paso 1: Crear archivo de variables

```bash
cd deploy/terraform

cat > terraform.tfvars << 'EOF'
oci_compartment_id = "ocid1.compartment.oc1..xxxxx"
container_image = "iad.ocir.io/mynamespace/bbva-seguros:latest"
openai_api_key = "sk-proj-xxxxx"
instagram_email = "email@gmail.com"
instagram_password = "app_password"
database_password = "StrongPassword123!"
secret_key = "generate-with-python-secrets"
EOF
```

#### Paso 2: Aplicar Terraform

```bash
# Inicializar
terraform init

# Ver cambios
terraform plan

# Aplicar
terraform apply

# Output muestra:
# - VCN ID
# - Subnet IDs
# - Vault ID
```

### Opción 3: Oracle Cloud Console (UI)

1. **Ir a Container Instances**
   - Oracle Cloud Console > Containers > Container Instances

2. **Click en "Create container instance"**

3. **Configurar:**
   - Name: `bbva-seguros-backend`
   - Compartment: tu compartment
   - Subnet: red pública

4. **Agregar Container:**
   - Image: `iad.ocir.io/namespace/bbva-seguros:latest`
   - Memory: 1 GB
   - CPUs: 1
   - Port: 8000

5. **Environment Variables:**
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `INSTAGRAM_EMAIL`
   - `INSTAGRAM_PASSWORD`
   - `SECRET_KEY`

6. **Create**

---

## CI/CD con GitHub Actions

### 1. Configurar Secrets en GitHub

```
Repo > Settings > Secrets and variables > Actions > New repository secret
```

Agregar estos secrets:

| Secret | Valor | Cómo obtener |
|--------|-------|-------------|
| `OCI_NAMESPACE` | mynamespace | `oci os ns get` |
| `OCI_USERNAME` | tu_username | Profile > Tenancy |
| `OCI_AUTH_TOKEN` | generated_token | Profile > Auth tokens |
| `OCI_PROVIDER_ID` | ocid1.authprovider... | OCI IAM > Identity Providers |
| `OCI_WORKLOAD_IDENTITY_PROVIDER` | ocid1.workload... | OCI IAM > Workload Identity |
| `OCI_CONTAINER_ID` | ocid1.containerinstance... | Después de crear |
| `SLACK_WEBHOOK_URL` | https://hooks.slack.com/... | (opcional) Slack App |

### 2. Hacer Push a main

```bash
git add .
git commit -m "Configura deployment a Oracle Cloud"
git push origin main
```

**GitHub Actions ejecutará automáticamente:**
1. Build Docker image
2. Ejecutar tests
3. Push a OCIR
4. Deploy a Container Instance
5. Healthcheck
6. Notificar en Slack

Ver estado: **GitHub > Actions**

---

## Troubleshooting

### ❌ "Docker not found"

```bash
# Verificar instalación
docker --version

# Si no está instalado:
# Windows/Mac: Instalar Docker Desktop
# Linux: sudo apt-get install docker.io
```

### ❌ "OCI CLI: not authenticated"

```bash
# Verificar credenciales
oci os ns get

# Si falla, reconfigura:
oci setup config
```

### ❌ "OCIR: Unauthorized"

```bash
# Generar nuevo token
oci os object-meta-storage get-auth-token --max-valid-days 30

# Copiar el token y hacer login manual
docker login iad.ocir.io
# Username: <namespace>
# Password: <paste_token>
```

### ❌ "Container Instance no inicia"

```bash
# Ver logs
docker logs bbva_backend

# Si usa OCI CLI:
oci container-instances container-instance get \
  --container-instance-id <ID>
```

### ❌ "Connection refused - Cannot connect to database"

```bash
# Verificar DB está corriendo
docker-compose ps postgres

# Verificar connection string en .env
echo $DATABASE_URL

# Testear conexión
psql $DATABASE_URL
```

### ❌ "Port 8000 already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### ❌ "GitHub Actions - Push failed"

```bash
# Verificar secrets están configurados
# Settings > Secrets > Check all secrets

# Verificar Docker Registry login
docker login iad.ocir.io
```

---

## 🔒 Seguridad - Checklist

- [ ] Cambiar todas las contraseñas en .env
- [ ] Generar SECRET_KEY fuerte: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] No compartir .env en público
- [ ] Usar credenciales de aplicación para Instagram (no contraseña real)
- [ ] Habilitar security groups en OCI
- [ ] Configurar CORS correctamente
- [ ] Usar SSL/TLS en producción
- [ ] Hacer backups de la base de datos
- [ ] Rotar tokens regularmente

---

## 📊 Monitoreo

```bash
# Ver estado de Container Instance
oci container-instances container-instance list \
  --compartment-id <COMPARTMENT_ID>

# Ver logs en tiempo real
docker-compose logs -f backend

# Healthcheck
curl http://<IP>:8000/api/health

# Conectarse a DB
psql $DATABASE_URL
SELECT * FROM leads;
```

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs
2. Consulta [Oracle Cloud Docs](https://docs.oracle.com/en-us/iaas/)
3. Abre un issue en GitHub
4. Contacta: epujalka24@gmail.com

---

¡Listo para deployar! 🚀
