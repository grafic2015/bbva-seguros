#!/bin/bash

# 🚀 Script de Deploy en Oracle Cloud
# Uso: ./deploy.sh

set -e

echo "🚀 BBVA Seguros - Deploy Script"
echo "================================"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paso 1: Actualizar repo
echo -e "${BLUE}📥 Actualizando repositorio...${NC}"
git pull origin main

# Paso 2: Construir imagen
echo -e "${BLUE}🔨 Construyendo Docker image...${NC}"
docker-compose build

# Paso 3: Detener contenedores anteriores
echo -e "${BLUE}⏹️  Deteniendo contenedores antiguos...${NC}"
docker-compose down

# Paso 4: Levantar nuevamente
echo -e "${BLUE}🚀 Levantando contenedores...${NC}"
docker-compose up -d

# Paso 5: Esperar a que PostgreSQL esté listo
echo -e "${YELLOW}⏳ Esperando a PostgreSQL...${NC}"
sleep 10

# Paso 6: Verificar salud
echo -e "${BLUE}🔍 Verificando salud del backend...${NC}"
for i in {1..10}; do
  if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Backend listo!${NC}"
    break
  fi
  echo "Intento $i/10..."
  sleep 2
done

# Paso 7: Ver logs
echo -e "${BLUE}📊 Mostrando logs...${NC}"
docker-compose logs backend

echo ""
echo -e "${GREEN}✅ Deploy completado!${NC}"
echo ""
echo "🌍 URL del backend: http://$(hostname -I | awk '{print $1}'):8000"
echo "📊 PostgreSQL: postgres:5432"
echo ""
echo "Siguiente: Actualiza tu frontend para apuntar a esta URL 🎯"
