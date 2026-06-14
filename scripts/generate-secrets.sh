#!/bin/bash

# ═════════════════════════════════════════════════════════════════════════
# 🔐 Generar secretos seguros para .env
# ═════════════════════════════════════════════════════════════════════════
# Uso: ./scripts/generate-secrets.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Generador de Secretos - BBVA Seguros                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no instalado"
    exit 1
fi

# Generar SECRET_KEY
echo "🔑 Generando SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "  ✓ SECRET_KEY generado"

# Generar POSTGRES_PASSWORD
echo ""
echo "🔑 Generando POSTGRES_PASSWORD..."
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*') for _ in range(24)))")
echo "  ✓ POSTGRES_PASSWORD generado"

# Mostrar template de .env
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 Añade estos valores a tu .env:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "❗ IMPORTANTE: Reemplaza estos valores también en .env:"
echo "  • OPENAI_API_KEY=sk-proj-tu_key_aqui"
echo "  • INSTAGRAM_EMAIL=tu_email@gmail.com"
echo "  • INSTAGRAM_PASSWORD=tu_app_password"
echo "  • OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxx"
echo "  • OCI_VCN_ID=ocid1.vcn.oc1.iad.xxxxx"
echo "  • OCI_SUBNET_ID=ocid1.subnet.oc1.iad.xxxxx"
echo ""
echo "✅ Secretos generados exitosamente"
