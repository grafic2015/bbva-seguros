#!/bin/bash

# ═════════════════════════════════════════════════════════════════════════
# 🚀 Script: Build y Push a Oracle Cloud Container Registry (OCIR)
# ═════════════════════════════════════════════════════════════════════════
# Uso: ./scripts/build-and-push-ocir.sh [version]
# Ejemplo: ./scripts/build-and-push-ocir.sh v1.0.0

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────
# Cargar variables de entorno
# ─────────────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: Archivo .env no encontrado${NC}"
    echo "Copia .env.example a .env y configura tus datos"
    exit 1
fi

source .env

VERSION=${1:-latest}
DATE=$(date +%Y%m%d_%H%M%S)

# Validar variables requeridas
REQUIRED_VARS=("OCIR_REGION" "OCIR_NAMESPACE" "OCIR_REPO" "OPENAI_API_KEY" "INSTAGRAM_EMAIL" "INSTAGRAM_PASSWORD")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: Variable $var no configurada en .env${NC}"
        exit 1
    fi
done

# Construir nombre de imagen
REGISTRY="${OCIR_REGION}.ocir.io"
IMAGE_NAME="${REGISTRY}/${OCIR_NAMESPACE}/${OCIR_REPO}"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
IMAGE_TAG_LATEST="${IMAGE_NAME}:latest"
IMAGE_TAG_DATE="${IMAGE_NAME}:${DATE}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 1: Validar herramientas
# ─────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BBVA Seguros - Build & Push a OCIR                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}[1/5] Validando herramientas...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no instalado${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git no instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Herramientas OK${NC}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 2: Validar conectividad con OCI
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/5] Validando conexión con Oracle Cloud...${NC}"

if ! command -v oci &> /dev/null; then
    echo -e "${YELLOW}⚠️  OCI CLI no instalado - continuando sin validación${NC}"
else
    if ! oci os ns get --query data.namespace-name --raw-output &> /dev/null; then
        echo -e "${RED}❌ No puedo conectar con Oracle Cloud. Verifica OCI CLI configurado${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Conexión OCI OK${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────
# PASO 3: Build imagen
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/5] Compilando imagen Docker...${NC}"
echo "  Tag: $IMAGE_TAG"
echo ""

docker build \
    --tag "$IMAGE_TAG" \
    --tag "$IMAGE_TAG_LATEST" \
    --tag "$IMAGE_TAG_DATE" \
    --label "version=$VERSION" \
    --label "build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --label "git_commit=$(git rev-parse --short HEAD)" \
    .

echo -e "${GREEN}✓ Build completado${NC}"

# ─────────────────────────────────────────────────────────────────────────
# PASO 4: Autenticar con OCIR
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[4/5] Autenticando con Oracle Cloud Container Registry...${NC}"

if command -v oci &> /dev/null; then
    # Usar OCI CLI para obtener token
    AUTH_TOKEN=$(oci os object-meta-storage get-auth-token --max-valid-days 1 --query data --raw-output 2>/dev/null || echo "")

    if [ -n "$AUTH_TOKEN" ]; then
        NAMESPACE=$(oci os ns get --query data.namespace-name --raw-output)
        echo "$AUTH_TOKEN" | docker login -u "${NAMESPACE}" --password-stdin "$REGISTRY"
        echo -e "${GREEN}✓ Autenticación exitosa (vía OCI CLI)${NC}"
    else
        echo -e "${YELLOW}⚠️  No puedo obtener token OCI, intenta manualmente:${NC}"
        echo "docker login $REGISTRY"
        read -p "¿Continuar? (s/n) " -n 1 -r; echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then exit 1; fi
    fi
else
    echo -e "${YELLOW}⚠️  Ingresa credenciales de OCIR manualmente${NC}"
    docker login "$REGISTRY"
fi

# ─────────────────────────────────────────────────────────────────────────
# PASO 5: Push a OCIR
# ─────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[5/5] Subiendo imagen a Oracle Cloud Container Registry...${NC}"

docker push "$IMAGE_TAG"
docker push "$IMAGE_TAG_LATEST"
docker push "$IMAGE_TAG_DATE"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Push completado exitosamente!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Información de la imagen:${NC}"
echo "  Registry:      $REGISTRY"
echo "  Namespace:     $OCIR_NAMESPACE"
echo "  Repositorio:   $OCIR_REPO"
echo "  Version:       $VERSION"
echo "  Full image:    $IMAGE_TAG"
echo ""

echo -e "${BLUE}🚀 Próximos pasos:${NC}"
echo "  1. Ir a Oracle Cloud Console > Container Registries"
echo "  2. Encontrar: ${OCIR_NAMESPACE}/${OCIR_REPO}"
echo "  3. Copiar image URL: $IMAGE_TAG_LATEST"
echo "  4. Crear Container Instance con esta imagen"
echo ""
echo "  O usar Kubernetes:"
echo "  kubectl create deployment bbva-seguros --image=$IMAGE_TAG_LATEST"
echo ""

echo -e "${GREEN}¡Listo para deployar! 🎉${NC}"
