# 🚗 Sistema Automatizado de Seguros Auto - BBVA

Sistema de 2 agentes que monitorea comentarios en Instagram, detecta la palabra "quiero" y envía automáticamente un DM con oferta de seguros auto con 35% de descuento.

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

Hecho con ❤️ para BBVA Seguros Auto
