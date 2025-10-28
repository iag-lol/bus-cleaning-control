# Guía de Instalación y Ejecución

## Sistema Completo de Control de Aseo de Buses

Esta guía te llevará paso a paso para ejecutar el sistema completo.

---

## 📋 Requisitos Previos

### Opción 1: Con Docker (RECOMENDADO - Más Fácil)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (incluido con Docker Desktop)

### Opción 2: Sin Docker (Desarrollo Local)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (opcional)

---

## 🚀 Inicio Rápido con Docker (5 minutos)

### Paso 1: Clonar o Navegar al Proyecto

```bash
cd bus-cleaning-control
```

### Paso 2: Configurar Variables de Entorno

#### Backend
```bash
cp backend/.env.example backend/.env
```

Abre `backend/.env` y verifica que todo esté correcto. Las configuraciones por defecto funcionan para desarrollo local con Docker.

#### Frontend
```bash
cp frontend/.env.example frontend/.env
```

Las configuraciones por defecto del frontend también funcionan.

### Paso 3: Levantar Todos los Servicios

```bash
docker compose up -d
```

Este comando hará:
- ✅ Descargar las imágenes necesarias (PostgreSQL, Redis, etc.)
- ✅ Construir el backend y frontend
- ✅ Crear la base de datos
- ✅ Crear el usuario administrador
- ✅ Levantar todos los servicios

**Primera vez**: Puede tomar 3-5 minutos descargando dependencias.

### Paso 4: Verificar que Todo Esté Corriendo

```bash
docker compose ps
```

Deberías ver 4 servicios corriendo:
- ✅ `bus-cleaning-db` (PostgreSQL)
- ✅ `bus-cleaning-redis` (Redis)
- ✅ `bus-cleaning-backend` (FastAPI)
- ✅ `bus-cleaning-frontend` (React)

### Paso 5: Acceder a la Aplicación

Abre tu navegador y ve a:

**Frontend (Aplicación Principal)**
```
http://localhost:5173
```

**Backend API (Documentación Swagger)**
```
http://localhost:8000/docs
```

**Credenciales por Defecto:**
- Email: `admin@buses.cl`
- Password: `Admin123!`

⚠️ **IMPORTANTE**: Cambia estas credenciales inmediatamente en producción.

### Paso 6: Ver Logs (si hay problemas)

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs solo del backend
docker compose logs -f backend

# Ver logs solo del frontend
docker compose logs -f frontend
```

### Paso 7: Detener los Servicios

```bash
# Detener sin eliminar datos
docker compose stop

# Detener y eliminar contenedores (mantiene datos)
docker compose down

# Eliminar TODO (contenedores, volúmenes, datos)
docker compose down -v
```

---

## 🛠️ Instalación Sin Docker (Desarrollo Local)

### Backend

1. **Navegar al directorio backend**
```bash
cd backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Activar en Linux/Mac:
source venv/bin/activate

# Activar en Windows:
venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Edita `.env` y configura tu base de datos local:
```env
DATABASE_URL=postgresql+asyncpg://tu_usuario:tu_password@localhost:5432/bus_cleaning
```

5. **Crear base de datos PostgreSQL**
```sql
CREATE DATABASE bus_cleaning;
```

6. **Crear usuario administrador**
```bash
python -m app.scripts.create_admin
```

7. **Ejecutar servidor de desarrollo**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend disponible en: `http://localhost:8000`

### Frontend

1. **Navegar al directorio frontend**
```bash
cd frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
```

4. **Ejecutar servidor de desarrollo**
```bash
npm run dev
```

Frontend disponible en: `http://localhost:5173`

---

## 📱 Uso de la Aplicación

### Vista Móvil (Operario)

1. **Acceder desde móvil o desktop** en `http://localhost:5173`
2. **Iniciar sesión** con las credenciales de admin (o crear usuario operario)
3. **Ir a "Inspección"** (vista principal de operario)
4. **Seleccionar PPU**: Buscar un bus existente o crear uno nuevo
5. **Permitir cámara**: El navegador pedirá permiso
6. **Análisis automático**: El sistema analiza cada 500ms automáticamente
7. **Ver resultado**: Badge muestra LIMPIO/SUCIO/DUDOSO con sugerencias
8. **Agregar observaciones**: Escribir notas adicionales (opcional)
9. **Enviar**: Presionar botón "Enviar Registro"

### Panel Administrativo

1. **Ir a "Dashboard"** en el menú
2. **Ver estadísticas** en tiempo real
3. **Reportes**: Filtrar y exportar CSV/PDF
4. **Alertas**: Ver y resolver alertas automáticas
5. **Gestión**: Administrar PPUs y usuarios

---

## 🔧 Solución de Problemas

### La cámara no funciona

**Problema**: "getUserMedia() no está disponible"

**Soluciones**:
1. Usa HTTPS en producción (cámara requiere contexto seguro)
2. En desarrollo, usa `localhost` (es seguro)
3. Verifica permisos del navegador
4. Usa el botón "Subir Foto" como alternativa

### Error de conexión al backend

**Problema**: "Network Error" o "CORS Error"

**Soluciones**:
1. Verifica que el backend esté corriendo: `docker compose ps`
2. Revisa logs: `docker compose logs backend`
3. Verifica `BACKEND_CORS_ORIGINS` en `backend/.env`
4. Asegúrate que la URL en `frontend/.env` sea correcta

### Base de datos no conecta

**Problema**: "Connection refused" en PostgreSQL

**Soluciones con Docker**:
```bash
# Reiniciar servicios
docker compose restart db backend

# Ver logs de la base de datos
docker compose logs db
```

**Soluciones sin Docker**:
1. Verifica que PostgreSQL esté corriendo
2. Verifica credenciales en `.env`
3. Prueba conexión: `psql -U tu_usuario -d bus_cleaning`

### El modelo de IA no carga

**Solución**: El sistema usa un clasificador dummy por defecto (configurado con `ML_USE_DUMMY=true`). Este es perfecto para desarrollo y testing. Para usar un modelo real:

1. Entrena o descarga un modelo ONNX
2. Colócalo en `backend/ml/models/cleaning_classifier.onnx`
3. Cambia `ML_USE_DUMMY=false` en `backend/.env`
4. Reinicia el backend

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest                           # Todos los tests
pytest --cov=app tests/          # Con coverage
pytest tests/api/test_auth.py    # Test específico
```

### Frontend

```bash
cd frontend
npm run test                     # Unit tests (Vitest)
npm run test:e2e                 # E2E tests (Playwright)
```

---

## 🌐 Despliegue en Producción

### Checklist Pre-Producción

- [ ] Cambiar `SECRET_KEY` en `backend/.env` (generar nuevo con `openssl rand -hex 32`)
- [ ] Cambiar password de admin
- [ ] Configurar CORS correctamente (solo dominios permitidos)
- [ ] Usar PostgreSQL real (no SQLite)
- [ ] Configurar backups automáticos de base de datos
- [ ] Habilitar HTTPS/SSL (nginx o Caddy)
- [ ] Configurar rate-limiting
- [ ] Configurar logging y monitoreo
- [ ] Probar notificaciones Web Push con VAPID keys reales
- [ ] Validar funcionamiento offline

### Producción con Docker

```bash
# Build para producción
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Ejecutar en producción
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Variables de Entorno para Producción

**Backend** (`.env`):
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generar-nuevo-con-openssl>
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
BACKEND_CORS_ORIGINS=https://tu-dominio.com
ML_USE_DUMMY=false
```

**Frontend** (`.env`):
```env
VITE_API_URL=https://api.tu-dominio.com
VITE_WS_URL=wss://api.tu-dominio.com
```

---

## 📚 Recursos Adicionales

### Documentación API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Estructura del Proyecto

```
bus-cleaning-control/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints
│   │   ├── models/         # Modelos DB
│   │   ├── services/       # Lógica de negocio
│   │   └── main.py         # Entry point
│   └── requirements.txt
├── frontend/               # React App
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Páginas
│   │   └── stores/        # Zustand stores
│   └── package.json
├── docker-compose.yml     # Orquestación Docker
└── README.md              # Documentación principal
```

### Comandos Útiles

```bash
# Ver estado de servicios
docker compose ps

# Ver logs en vivo
docker compose logs -f [servicio]

# Reiniciar un servicio
docker compose restart [servicio]

# Ejecutar comando en contenedor
docker compose exec backend python -m app.scripts.create_admin
docker compose exec db psql -U buscontrol -d bus_cleaning

# Limpiar todo y empezar de cero
docker compose down -v
docker compose up -d
```

---

## 🆘 Soporte

### Problemas Comunes

1. **Puerto ya en uso**: Cambia los puertos en `docker-compose.yml`
2. **Falta espacio en disco**: Limpia Docker: `docker system prune -a`
3. **Permisos en Linux**: Agrega tu usuario al grupo docker: `sudo usermod -aG docker $USER`

### Contacto

Para reportar bugs o solicitar features, crea un issue en el repositorio.

---

## ✅ Verificación Final

Para verificar que todo está funcionando:

1. ✅ Backend responde: `curl http://localhost:8000/health`
2. ✅ Frontend carga: Abre `http://localhost:5173`
3. ✅ Login funciona: Usa `admin@buses.cl` / `Admin123!`
4. ✅ WebSocket conecta: Verifica en consola del navegador (F12)
5. ✅ Base de datos accesible: `docker compose exec db psql -U buscontrol -d bus_cleaning -c "\dt"`

Si todo lo anterior funciona: **¡Felicidades! 🎉 El sistema está completamente operativo.**

---

## 🚀 Próximos Pasos

1. Crear usuarios operarios adicionales
2. Agregar PPUs (patentes) de buses
3. Empezar a registrar inspecciones
4. Explorar dashboard y reportes
5. Configurar alertas automáticas
6. (Opcional) Entrenar modelo de IA personalizado

---

**¡Listo para mejorar la calidad del transporte público!** 🚌✨
