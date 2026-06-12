#!/bin/bash

# 🚀 Script de Deploy Automatizado - Oracle Cloud
# Uso: ./deploy-oracle.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║   BBVA Seguros - Deploy Automatizado Oracle Cloud  ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# PASO 1: Verificar requisitos
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}[1/5] Verificando requisitos...${NC}"

# Verificar Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git no instalado${NC}"
    exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no instalado. Instala desde https://get.docker.com${NC}"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose no encontrado, instalando...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✓ Requisitos OK${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# PASO 2: Preparar repositorio
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}[2/5] Preparando repositorio...${NC}"

# Inicializar Git si no existe
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit - BBVA Seguros"
    echo -e "${YELLOW}⚠️  Repositorio creado localmente. Debes subirlo a GitHub manualmente:${NC}"
    echo "git remote add origin https://github.com/tu_usuario/tu_repo.git"
    echo "git push -u origin main"
else
    git pull origin main || echo "No remote configurado"
fi

echo -e "${GREEN}✓ Repositorio OK${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# PASO 3: Crear variables de entorno
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}[3/5] Configurando variables de entorno...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado. Creando plantilla...${NC}"
    cat > .env << 'EOF'
# OpenAI API Key (obten en https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-tu_key_aqui

# Instagram Business (para webhooks futuros)
INSTAGRAM_EMAIL=tu_email@instagram.com
INSTAGRAM_PASSWORD=tu_password_app

# Database (no cambiar, se configura en docker-compose.yml)
DATABASE_URL=postgresql://bbva_user:bbva_password_123@postgres:5432/bbva_seguros
EOF
    echo -e "${YELLOW}⚠️  Abre .env y actualiza OPENAI_API_KEY${NC}"
else
    echo -e "${GREEN}✓ .env ya existe${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PASO 4: Construir y levantar Docker
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}[4/5] Levantando Docker containers...${NC}"

# Detener contenedores anteriores
sudo docker-compose down || true

# Construir imagen
echo -e "${BLUE}Construyendo imagen...${NC}"
sudo docker-compose build

# Levantar contenedores
echo -e "${BLUE}Levantando contenedores...${NC}"
sudo docker-compose up -d

# Esperar a que PostgreSQL esté listo
echo -e "${BLUE}Esperando a PostgreSQL...${NC}"
sleep 15

# Verificar que está corriendo
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo -e "${GREEN}✓ Backend listo!${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend no responde después de 10 intentos${NC}"
        echo -e "${BLUE}Ver logs:${NC} sudo docker-compose logs backend"
        exit 1
    fi
    echo "Intento $i/10..."
    sleep 2
done

# ═══════════════════════════════════════════════════════════════════════════
# PASO 5: Información de acceso
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}[5/5] Finalizando...${NC}"

# Obtener IP
IP=$(hostname -I | awk '{print $1}')
DOCKER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' bbva_backend || echo "localhost")

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║          ✅ DEPLOY EXITOSO                        ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📊 Información de acceso:${NC}"
echo "  Backend API:    http://$IP:8000"
echo "  API Docs:       http://$IP:8000/docs (Swagger)"
echo "  Health Check:   http://$IP:8000/api/health"
echo ""
echo -e "${BLUE}🗄️  Base de datos:${NC}"
echo "  Host:     postgres (o $DOCKER_IP)"
echo "  Usuario:  bbva_user"
echo "  Contraseña: bbva_password_123"
echo "  Database: bbva_seguros"
echo ""
echo -e "${BLUE}🔍 Comandos útiles:${NC}"
echo "  Ver logs:       sudo docker-compose logs -f backend"
echo "  Reiniciar:      sudo docker-compose restart"
echo "  Parar:          sudo docker-compose down"
echo "  Status:         sudo docker-compose ps"
echo ""
echo -e "${YELLOW}⚠️  PRÓXIMOS PASOS:${NC}"
echo "  1. Abre .env y actualiza OPENAI_API_KEY"
echo "  2. Sube el proyecto a GitHub"
echo "  3. Deploy frontend en Vercel (https://vercel.com)"
echo "  4. En Vercel, configura: /frontend como root"
echo "  5. Actualiza frontend/vite.config.ts con esta IP"
echo ""
echo -e "${GREEN}¡Sistema en producción! 🚀${NC}"
