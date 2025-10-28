# 🎉 ¡Sistema Completo Listo Para Ejecutar!

## Control de Aseo de Buses con IA - Versión 1.0

---

## ✅ ¿Qué tienes ahora?

Un sistema **completo** y **funcional** para el control de aseo de buses que incluye:

### Backend (Python + FastAPI)
- ✅ API REST completa con endpoints para autenticación, buses, eventos, alertas y reportes
- ✅ Base de datos PostgreSQL con modelos SQLModel
- ✅ Autenticación JWT con roles (Admin, Supervisor, Operario)
- ✅ Servicio de IA/ML con ONNX Runtime (incluye modo dummy para desarrollo)
- ✅ WebSockets para notificaciones en tiempo real
- ✅ Sistema de alertas automáticas (buses sucios repetidos, etc.)
- ✅ Exportación de reportes en CSV y PDF
- ✅ Todo self-hosted, costo $0

### Frontend (React + TypeScript)
- ✅ App móvil/web PWA instalable
- ✅ Vista de inspección con cámara en vivo
- ✅ **Análisis automático** cada 500ms sin botones
- ✅ Selector de PPU con creación rápida
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Offline-first con sincronización automática (configurado)
- ✅ Dark mode automático
- ✅ Responsive (mobile-first)

### Infraestructura
- ✅ Docker Compose con todos los servicios
- ✅ PostgreSQL + Redis
- ✅ Variables de entorno configurables
- ✅ CI/CD con GitHub Actions
- ✅ Tests configurados (Pytest + Vitest)

---

## 🚀 INICIO RÁPIDO (3 Comandos)

```bash
# 1. Ir al directorio del proyecto
cd bus-cleaning-control

# 2. Copiar configuración
cp backend/.env.example backend/.env && cp frontend/.env.example frontend/.env

# 3. Levantar todo
docker compose up -d
```

**¡Eso es todo!** 🎉

Espera 1-2 minutos la primera vez (descargando dependencias).

### Acceder al Sistema

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Credenciales**: `admin@buses.cl` / `Admin123!`

---

## 📁 Estructura del Proyecto

```
bus-cleaning-control/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── api/               # 📡 Endpoints REST
│   │   │   ├── auth.py        # Login, JWT tokens
│   │   │   ├── buses.py       # CRUD de buses/PPUs
│   │   │   ├── events.py      # Eventos de limpieza
│   │   │   ├── alerts.py      # Alertas automáticas
│   │   │   └── reports.py     # Reportes CSV/PDF
│   │   ├── core/              # ⚙️ Configuración
│   │   │   ├── config.py      # Settings de la app
│   │   │   ├── database.py    # Conexión a DB
│   │   │   ├── security.py    # JWT, passwords
│   │   │   └── deps.py        # Dependencias FastAPI
│   │   ├── models/            # 🗃️ Modelos de DB
│   │   │   ├── user.py        # Usuarios y roles
│   │   │   ├── bus.py         # Buses (PPUs)
│   │   │   ├── cleaning_event.py  # Inspecciones
│   │   │   ├── alert.py       # Alertas
│   │   │   └── audit.py       # Logs de auditoría
│   │   ├── services/          # 🧠 Lógica de negocio
│   │   │   ├── ml_service.py  # Análisis con IA
│   │   │   ├── alert_service.py   # Detección de alertas
│   │   │   └── report_service.py  # Generación de reportes
│   │   ├── schemas/           # 📋 Pydantic schemas
│   │   ├── scripts/           # 🛠️ Utilidades
│   │   │   └── create_admin.py    # Crear usuario admin
│   │   └── main.py            # 🚀 Entry point, WebSockets
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile             # Docker backend
│   └── .env.example           # Variables de entorno
│
├── frontend/                  # App React
│   ├── src/
│   │   ├── pages/            # 📄 Páginas
│   │   │   ├── LoginPage.tsx      # Login
│   │   │   ├── InspectionPage.tsx # 📸 Cámara + análisis auto
│   │   │   └── DashboardPage.tsx  # 📊 Dashboard
│   │   ├── components/       # 🧩 Componentes
│   │   │   └── Layout.tsx         # Layout principal
│   │   ├── stores/           # 💾 Estado global (Zustand)
│   │   │   └── authStore.ts       # Autenticación
│   │   ├── services/         # 🌐 API clients
│   │   │   └── api.ts             # Axios config
│   │   ├── types/            # 📐 TypeScript types
│   │   └── main.tsx          # Entry point
│   ├── package.json          # Dependencias npm
│   ├── vite.config.ts        # Vite + PWA config
│   ├── tailwind.config.js    # Estilos Tailwind
│   └── Dockerfile            # Docker frontend
│
├── ml/                       # 🤖 ML/IA (opcional)
│   ├── models/               # Modelos entrenados (.onnx)
│   └── scripts/              # Scripts de entrenamiento
│
├── .github/                  # 🔄 CI/CD
│   └── workflows/
│       └── ci.yml            # GitHub Actions
│
├── docker-compose.yml        # 🐳 Orquestación completa
├── README.md                 # 📖 Documentación principal
├── SETUP.md                  # 🛠️ Guía de instalación detallada
├── INSTRUCTIONS.md           # 📝 Este archivo
├── LICENSE                   # ⚖️ MIT License
└── .gitignore                # Git ignore
```

---

## 🎯 Características Principales Implementadas

### 1. Análisis Automático con IA ✨

- **Sin botones**: La cámara analiza automáticamente cada 500ms
- **Feedback instantáneo**: Badge con estado (Limpio/Sucio/Dudoso) + % confianza
- **Sugerencias específicas**: "Papeles en el piso", "Ventanas con manchas", etc.
- **Modo dummy**: Funciona sin modelo real (perfecto para desarrollo)
- **Extensible**: Listo para agregar modelo ONNX real

**Archivo**: `frontend/src/pages/InspectionPage.tsx` (líneas 90-130)

### 2. Sistema de Alertas Inteligente 🚨

Detecta automáticamente:
- **Buses repetidamente sucios**: 2+ eventos sucios en 72h
- **Muy sucio**: Alta confianza + múltiples problemas
- **Dudosos recurrentes**: 3+ eventos dudosos

Las alertas se crean automáticamente y se notifican en tiempo real vía WebSocket.

**Archivo**: `backend/app/services/alert_service.py`

### 3. Tiempo Real con WebSockets ⚡

- Notificaciones instantáneas al crear eventos
- Alertas push al dashboard
- Conexión persistente y auto-reconexión

**Archivo**: `backend/app/main.py` (líneas 45-100)

### 4. Reportes Profesionales 📊

- **CSV**: Exportación de eventos con filtros
- **PDF**: Reporte visual con estadísticas, gráficos y tablas
- **Filtros**: Por fecha, PPU, operario, estado

**Archivo**: `backend/app/services/report_service.py`

### 5. PWA Offline-First 📱

- Instalable en Android y escritorio
- Service Worker configurado
- Background sync de registros (cuando vuelve la conexión)
- Cache de imágenes y API calls

**Archivo**: `frontend/vite.config.ts` (PWA plugin)

---

## 🔧 Configuración Avanzada

### Variables de Entorno Clave

#### Backend (`backend/.env`)

```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://buscontrol:buscontrol123@db:5432/bus_cleaning

# Seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

# CORS (agregar tus dominios)
BACKEND_CORS_ORIGINS=http://localhost:5173

# IA/ML
ML_USE_DUMMY=true                    # true = clasificador dummy, false = ONNX real
ML_MODEL_PATH=/app/ml/models/cleaning_classifier.onnx
ML_CONFIDENCE_THRESHOLD_CLEAN=0.70   # Umbral para "limpio"
ML_CONFIDENCE_THRESHOLD_DIRTY=0.65   # Umbral para "sucio"

# Alertas
ALERT_DIRTY_THRESHOLD=2              # Cuántos eventos sucios para alerta
ALERT_DIRTY_WINDOW_HOURS=72          # Ventana de tiempo (horas)
ALERT_UNCERTAIN_THRESHOLD=3          # Eventos dudosos para alerta
```

#### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_OFFLINE=true
VITE_CAMERA_ANALYSIS_INTERVAL=500    # Intervalo de análisis (ms)
```

---

## 🧪 Testing

### Backend

```bash
cd backend

# Todos los tests
pytest

# Con coverage
pytest --cov=app tests/

# Solo un módulo
pytest tests/api/test_auth.py -v
```

### Frontend

```bash
cd frontend

# Unit tests
npm run test

# E2E tests (requiere Playwright)
npm run test:e2e
```

---

## 🚀 Flujo de Uso Completo

### Para Operarios (Vista Móvil)

1. **Login** → `admin@buses.cl` / `Admin123!`
2. **Ir a "Inspección"**
3. **Seleccionar PPU**:
   - Buscar existente en dropdown
   - O crear nuevo con botón "Nuevo PPU"
4. **Activar cámara** → Permitir permisos
5. **Esperar análisis automático** → Se ejecuta cada 500ms
6. **Ver resultado en overlay**:
   - Badge con estado (LIMPIO/SUCIO/DUDOSO)
   - % de confianza
   - Lista de problemas detectados
   - Sugerencias específicas
7. **Agregar observaciones** (opcional)
8. **Presionar "Enviar Registro"**
9. **Notificación en dashboard** → Supervisores ven evento en tiempo real

### Para Supervisores/Admins (Dashboard)

1. **Ir a "Dashboard"**
2. **Ver estadísticas** → Total, Limpios, Sucios, Dudosos
3. **Tabla de eventos recientes** → Últimos 50 registros
4. **Filtrar y exportar** → CSV o PDF (si implementado filtros UI)
5. **Ver alertas** → Buses con problemas recurrentes
6. **Resolver alertas** → Marcar como resueltas

---

## 📊 APIs Disponibles

### Autenticación

- `POST /auth/login` → Login con email/password
- `POST /auth/refresh` → Renovar access token

### Buses

- `GET /buses?search=ABC` → Listar buses (con búsqueda)
- `POST /buses` → Crear nuevo bus
- `GET /buses/{id}` → Obtener bus específico
- `PUT /buses/{id}` → Actualizar bus (supervisor+)
- `DELETE /buses/{id}` → Eliminar bus (supervisor+)

### Eventos de Limpieza

- `POST /events` → Crear evento (registrar inspección)
- `GET /events?from=&to=&ppu=&estado=` → Listar eventos con filtros
- `GET /events/{id}` → Obtener evento específico

### Análisis IA

- `POST /ai/analyze` → Analizar imagen (recibe base64, retorna estado + sugerencias)

### Alertas

- `GET /alerts?resolved=false` → Listar alertas (con filtros)
- `GET /alerts/{id}` → Obtener alerta específica
- `PATCH /alerts/{id}/resolve` → Resolver alerta (supervisor+)

### Reportes

- `GET /reports/summary?from=&to=` → Estadísticas resumen
- `GET /reports/export.csv` → Exportar eventos a CSV
- `GET /reports/export.pdf` → Exportar reporte a PDF

### WebSocket

- `ws://localhost:8000/ws` → Conexión WebSocket para tiempo real

---

## 🛠️ Comandos Docker Útiles

```bash
# Ver estado de servicios
docker compose ps

# Ver logs de todos los servicios
docker compose logs -f

# Ver logs solo del backend
docker compose logs -f backend

# Ver logs solo del frontend
docker compose logs -f frontend

# Reiniciar un servicio
docker compose restart backend

# Ejecutar comando en contenedor
docker compose exec backend python -m app.scripts.create_admin
docker compose exec db psql -U buscontrol -d bus_cleaning -c "SELECT * FROM users;"

# Detener todo
docker compose stop

# Detener y eliminar contenedores (mantiene volúmenes/datos)
docker compose down

# Eliminar TODO incluyendo datos
docker compose down -v

# Reconstruir imágenes
docker compose build --no-cache
docker compose up -d
```

---

## 🐛 Solución de Problemas Comunes

### 1. "La cámara no funciona"

**Causa**: getUserMedia() requiere contexto seguro (HTTPS o localhost)

**Solución**:
- En desarrollo usa `localhost` (ya configurado)
- En producción configura HTTPS
- Como alternativa temporal, usa el botón "Subir Foto"

### 2. "CORS Error" en el navegador

**Causa**: Backend no permite el origen del frontend

**Solución**:
```env
# backend/.env
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://tu-dominio.com
```

Reinicia backend: `docker compose restart backend`

### 3. "Connection refused" en PostgreSQL

**Solución**:
```bash
# Ver estado de la base de datos
docker compose ps db

# Si no está corriendo, reiniciar
docker compose up -d db

# Ver logs
docker compose logs db
```

### 4. Frontend no carga o pantalla en blanco

**Solución**:
```bash
# Ver logs del frontend
docker compose logs frontend

# Reconstruir
docker compose down
docker compose up -d --build frontend
```

### 5. "Model not found" en el backend

**Causa**: ML_USE_DUMMY=false pero no hay modelo ONNX

**Solución**:
```env
# backend/.env
ML_USE_DUMMY=true  # Usar clasificador dummy
```

O coloca un modelo real en `backend/ml/models/cleaning_classifier.onnx`

---

## 🔐 Seguridad en Producción

### Checklist Pre-Producción

1. **Cambiar SECRET_KEY**:
```bash
openssl rand -hex 32
# Copiar output a backend/.env
```

2. **Cambiar password de admin**:
- Login como admin
- Ir a configuración de usuario
- Cambiar contraseña

3. **Configurar CORS correctamente**:
```env
BACKEND_CORS_ORIGINS=https://tu-dominio.com
```

4. **Usar PostgreSQL real** (no SQLite en producción)

5. **Configurar HTTPS/SSL**:
- Usa Nginx o Caddy como reverse proxy
- Obtén certificado SSL con Let's Encrypt

6. **Rate limiting**: FastAPI + slowapi (opcional)

7. **Backups automáticos** de la base de datos

---

## 📈 Próximos Pasos

### Para Desarrollo

1. **Crear más usuarios**:
```bash
docker compose exec backend python -c "
from app.scripts.create_admin import create_admin_user
# Modificar script para crear operarios
"
```

2. **Agregar buses de prueba**:
- Via UI: Inspección → "Nuevo PPU"
- Via API: `POST /buses {"ppu": "ABCD12"}`

3. **Entrenar modelo personalizado**:
- Recolectar dataset de imágenes (limpio/sucio/dudoso)
- Usar script en `ml/scripts/train_classifier.py`
- Exportar a ONNX
- Colocar en `backend/ml/models/`
- Cambiar `ML_USE_DUMMY=false`

### Para Producción

1. **Deploy con docker-compose** en servidor
2. **Configurar dominio y SSL**
3. **Monitoreo**: Prometheus + Grafana (opcional)
4. **Logging**: ELK stack o CloudWatch (opcional)
5. **Backups**: PostgreSQL dumps diarios
6. **Escalamiento**: Docker Swarm o Kubernetes (si crece mucho)

---

## 🎓 Aprendizaje

### Archivos Clave para Entender

1. **Backend Main** → `backend/app/main.py`
   - Entry point de FastAPI
   - Configuración de WebSockets
   - Registro de routers

2. **ML Service** → `backend/app/services/ml_service.py`
   - Clasificador dummy vs ONNX
   - Análisis de imágenes
   - Detección de problemas

3. **Alert Service** → `backend/app/services/alert_service.py`
   - Lógica de alertas automáticas
   - Umbrales configurables

4. **Inspection Page** → `frontend/src/pages/InspectionPage.tsx`
   - Manejo de cámara
   - Análisis automático cada 500ms
   - Captura y envío de frames

5. **Auth Store** → `frontend/src/stores/authStore.ts`
   - Gestión de autenticación con Zustand
   - Persistencia de tokens

---

## 📞 Soporte

### Documentación

- **README.md**: Visión general del proyecto
- **SETUP.md**: Guía paso a paso de instalación
- **Este archivo**: Instrucciones completas de uso

### API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Logs

```bash
# Backend
docker compose logs -f backend

# Frontend
docker compose logs -f frontend

# Base de datos
docker compose logs -f db
```

---

## ✅ Verificación Final

Ejecuta estos comandos para verificar que todo funciona:

```bash
# 1. Servicios corriendo
docker compose ps
# ✅ 4 servicios: db, redis, backend, frontend

# 2. Backend responde
curl http://localhost:8000/health
# ✅ {"status":"ok","version":"1.0.0"}

# 3. Frontend carga
curl -I http://localhost:5173
# ✅ HTTP/1.1 200 OK

# 4. Base de datos accesible
docker compose exec db psql -U buscontrol -d bus_cleaning -c "\dt"
# ✅ Lista de tablas: users, buses, cleaning_events, alerts, audit_logs

# 5. Login funciona
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@buses.cl","password":"Admin123!"}'
# ✅ Retorna access_token
```

Si todo lo anterior funciona: **¡FELICIDADES! 🎉 El sistema está 100% operativo.**

---

## 🚀 ¡Empezar Ahora!

```bash
cd bus-cleaning-control
docker compose up -d
```

**Abre**: http://localhost:5173

**Login**: `admin@buses.cl` / `Admin123!`

**¡Comienza a inspeccionar buses con IA! 🚌✨**

---

**Desarrollado con ❤️ para mejorar la calidad del transporte público**

**Licencia**: MIT
**Stack**: Python, FastAPI, React, TypeScript, PostgreSQL, Docker
**Costo**: $0 (todo self-hosted)
