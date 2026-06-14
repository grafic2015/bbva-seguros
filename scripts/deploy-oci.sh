#!/bin/bash

# ═════════════════════════════════════════════════════════════════════════
# 🚀 Deploy a Oracle Cloud Container Instance
# ═════════════════════════════════════════════════════════════════════════
# Requisitos: oci-cli, jq, .env configurado
# Uso: ./scripts/deploy-oci.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Cargar .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env no encontrado${NC}"
    exit 1
fi
source .env

# Variables
CONTAINER_DISPLAY_NAME="bbva-seguros-backend"
IMAGE_URL="${OCIR_REGION}.ocir.io/${OCIR_NAMESPACE}/${OCIR_REPO}:latest"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BBVA Seguros - Deploy a Oracle Cloud Container Instance  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────
# PASO 1: Validar requisitos
# ─────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Validando requisitos...${NC}"

if ! command -v oci &> /dev/null; then
    echo -e "${RED}❌ OCI CLI no instalado${NC}"
    echo "Instala desde: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq no instalado${NC}"
    echo "Instala: apt-get install jq (Linux) o brew install jq (Mac)"
    exit 1
fi

# Validar configuración OCI
if ! oci os ns get --query data.namespace-name --raw-output &> /dev/null; then
    echo -e "${RED}❌ OCI CLI no configurado correctamente${NC}"
    echo "Ejecuta: oci setup config"
    exit 1
fi

echo -e "${GREEN}✓ Requisitos OK${NC}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 2: Validar variables de entorno
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/4] Validando variables de Oracle Cloud...${NC}"

REQUIRED_VARS=("OCI_COMPARTMENT_ID" "OCI_VCN_ID" "OCI_SUBNET_ID" "OCIR_REGION" "OCIR_NAMESPACE" "OCIR_REPO")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: Variable $var no configurada en .env${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Variables OK${NC}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 3: Crear Container Instance
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/4] Creando Container Instance en Oracle Cloud...${NC}"

# Crear secret para OCIR (si es privado)
echo -e "${BLUE}Creando referencia de imagen...${NC}"

# Crear Container Instance
CONTAINER_ID=$(oci container-instances container-instance create \
    --compartment-id "$OCI_COMPARTMENT_ID" \
    --availability-domain "$(oci compute availability-domain list --query 'data[0].name' --raw-output)" \
    --display-name "$CONTAINER_DISPLAY_NAME" \
    --containers "[{
        \"displayName\": \"bbva-backend\",
        \"imageUrl\": \"$IMAGE_URL\",
        \"workingDirectory\": \"/app\",
        \"environmentVariables\": {
            \"ENVIRONMENT\": \"$ENVIRONMENT\",
            \"DEBUG\": \"$DEBUG\",
            \"LOG_LEVEL\": \"$LOG_LEVEL\",
            \"OPENAI_API_KEY\": \"$OPENAI_API_KEY\",
            \"INSTAGRAM_EMAIL\": \"$INSTAGRAM_EMAIL\",
            \"INSTAGRAM_PASSWORD\": \"$INSTAGRAM_PASSWORD\",
            \"DATABASE_URL\": \"$DATABASE_URL\",
            \"SECRET_KEY\": \"$SECRET_KEY\",
            \"CORS_ORIGINS\": \"$CORS_ORIGINS\"
        },
        \"portMappings\": [{
            \"containerPort\": 8000,
            \"protocol\": \"TCP\"
        }]
    }]" \
    --vnics "[{
        \"subnetId\": \"$OCI_SUBNET_ID\",
        \"isPublicIpAssigned\": true
    }]" \
    --wait-for-state SUCCEEDED \
    --query 'data.id' \
    --raw-output)

if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}❌ Error creando Container Instance${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Container Instance creado: $CONTAINER_ID${NC}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 4: Obtener información de acceso
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[4/4] Obteniendo información de acceso...${NC}"

# Obtener IP pública
PUBLIC_IP=$(oci container-instances container-instance get \
    --container-instance-id "$CONTAINER_ID" \
    --query 'data.containers[0].vnics[0]["\""publicIp"\""]' \
    --raw-output 2>/dev/null || echo "En espera de asignación...")

# Esperar a que se asigne IP
RETRIES=0
while [ "$PUBLIC_IP" == "null" ] || [ -z "$PUBLIC_IP" ] && [ $RETRIES -lt 30 ]; do
    echo "Esperando asignación de IP pública..."
    sleep 5
    PUBLIC_IP=$(oci container-instances container-instance get \
        --container-instance-id "$CONTAINER_ID" \
        --query 'data.containers[0].vnics[0]["\""publicIp"\""]' \
        --raw-output 2>/dev/null || echo "")
    ((RETRIES++))
done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Deploy completado exitosamente!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Información de la instancia:${NC}"
echo "  Container ID:   $CONTAINER_ID"
echo "  Nombre:         $CONTAINER_DISPLAY_NAME"
echo "  Imagen:         $IMAGE_URL"
if [ "$PUBLIC_IP" != "null" ] && [ -n "$PUBLIC_IP" ]; then
    echo "  IP Pública:     $PUBLIC_IP"
    echo ""
    echo -e "${BLUE}🌐 Acceso:${NC}"
    echo "  API:            http://${PUBLIC_IP}:8000"
    echo "  API Docs:       http://${PUBLIC_IP}:8000/docs"
    echo "  Health Check:   http://${PUBLIC_IP}:8000/api/health"
else
    echo "  IP Pública:     (en espera...)"
fi

echo ""
echo -e "${BLUE}📋 Comandos útiles:${NC}"
echo "  Ver logs:       oci container-instances container instance get --container-instance-id $CONTAINER_ID"
echo "  Actualizar:     ./scripts/deploy-oci.sh (redeploy)"
echo "  Borrar:         oci container-instances container-instance delete --container-instance-id $CONTAINER_ID --force"
echo ""
echo -e "${GREEN}¡Deployment listo! 🎉${NC}"
