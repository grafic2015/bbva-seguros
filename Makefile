# ═════════════════════════════════════════════════════════════════════════
# Makefile - BBVA Seguros
# Comandos útiles para desarrollo y deployment
# ═════════════════════════════════════════════════════════════════════════

.PHONY: help install dev test build push deploy clean

# Default target
help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  BBVA Seguros - Makefile                                  ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 Instalación:"
	@echo "  make install          - Instalar dependencias"
	@echo "  make install-dev      - Instalar con dependencias de desarrollo"
	@echo ""
	@echo "🚀 Desarrollo:"
	@echo "  make dev              - Levantar stack local (Docker Compose)"
	@echo "  make logs             - Ver logs en tiempo real"
	@echo "  make shell            - Shell interactivo en container"
	@echo "  make test             - Ejecutar tests"
	@echo "  make lint             - Chequear código (flake8)"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make build            - Compilar imagen Docker"
	@echo "  make push             - Push a Oracle Container Registry"
	@echo "  make clean            - Limpiar contenedores"
	@echo ""
	@echo "☁️  Oracle Cloud:"
	@echo "  make secrets          - Generar secretos para .env"
	@echo "  make ocir             - Build y push a OCIR"
	@echo "  make deploy           - Deploy a Container Instance"
	@echo "  make deploy-tf        - Deploy con Terraform"
	@echo ""
	@echo "🔧 Utilidades:"
	@echo "  make migrate          - Ejecutar migraciones de DB"
	@echo "  make psql             - Conectar a PostgreSQL"
	@echo "  make healthcheck      - Verificar salud de la app"
	@echo ""

# ─────────────────────────────────────────────────────────────────────────
# Instalación
# ─────────────────────────────────────────────────────────────────────────

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install
	pip install pytest pytest-cov flake8 black

# ─────────────────────────────────────────────────────────────────────────
# Desarrollo
# ─────────────────────────────────────────────────────────────────────────

dev:
	@echo "🚀 Levantando stack local..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Creando .env desde .env.example..."; \
		cp .env.example .env; \
		echo "✅ Archivo .env creado"; \
		echo "⚠️  Edita .env con tus credenciales"; \
	fi
	docker-compose up -d
	@echo "✅ Stack levantado"
	@echo "🌐 Frontend: http://localhost:5173"
	@echo "🔌 Backend:  http://localhost:8000"
	@echo "📊 Docs:     http://localhost:8000/docs"

logs:
	docker-compose logs -f backend

shell:
	docker-compose exec backend /bin/bash

test:
	pytest backend --cov=backend --cov-report=term-missing

lint:
	flake8 backend --max-line-length=120

# ─────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────

build:
	@echo "🐳 Compilando imagen Docker..."
	docker build -t bbva-seguros:latest .
	@echo "✅ Build completado"

push:
	@echo "📤 Subiendo a OCIR..."
	./scripts/build-and-push-ocir.sh latest
	@echo "✅ Push completado"

clean:
	@echo "🧹 Limpiando..."
	docker-compose down -v
	docker system prune -f
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Limpieza completada"

# ─────────────────────────────────────────────────────────────────────────
# Oracle Cloud
# ─────────────────────────────────────────────────────────────────────────

secrets:
	@bash scripts/generate-secrets.sh

ocir: build
	@echo "🚀 Build y Push a OCIR..."
	./scripts/build-and-push-ocir.sh v1.0.0
	@echo "✅ OCIR push completado"

deploy:
	@echo "🚀 Deployando a Oracle Cloud..."
	./scripts/deploy-oci.sh

deploy-tf:
	@echo "🚀 Deployando con Terraform..."
	cd deploy/terraform && terraform plan && terraform apply
	@echo "✅ Deployment completado"

# ─────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────

migrate:
	@echo "📊 Ejecutando migraciones..."
	docker-compose exec backend alembic upgrade head
	@echo "✅ Migraciones completadas"

psql:
	@echo "🗄️  Conectando a PostgreSQL..."
	docker-compose exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

healthcheck:
	@echo "🏥 Verificando salud de la aplicación..."
	@curl -s http://localhost:8000/api/health | python3 -m json.tool
	@echo ""
	@echo "✅ App está sana"

requirements:
	@echo "📦 Actualizando requirements.txt..."
	pip freeze > requirements.txt
	@echo "✅ Actualizado"

# ─────────────────────────────────────────────────────────────────────────
# Git
# ─────────────────────────────────────────────────────────────────────────

push-git:
	@echo "📤 Haciendo push a GitHub..."
	git add .
	git commit -m "Update: $(shell date '+%Y-%m-%d %H:%M:%S')"
	git push origin main
	@echo "✅ Push completado"

# ─────────────────────────────────────────────────────────────────────────
# Desarrollo rápido
# ─────────────────────────────────────────────────────────────────────────

start: dev
	@echo "✅ Stack listo para desarrollo"

stop:
	docker-compose down

restart:
	docker-compose restart

ps:
	docker-compose ps
