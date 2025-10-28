# Sistema de Control de Aseo de Buses

Sistema completo de gestión y control de limpieza de buses con detección automática mediante IA, tiempo real y costo $0.

## Características

- **Análisis automático con IA**: Detección en tiempo real del estado de limpieza (Limpio/Sucio/Dudoso)
- **App móvil PWA**: Instalable, offline-first, análisis automático desde cámara
- **Panel web administrativo**: Dashboard en tiempo real, reportes, alertas
- **Costo $0**: Todo self-hosted, sin servicios pagos externos
- **Privacidad**: Inferencia en dispositivo cuando es posible
- **Tiempo real**: WebSockets para notificaciones instantáneas
- **Offline-first**: Background sync de registros
- **Reportes**: Exportación CSV y PDF

## Stack Tecnológico

### Backend
- **FastAPI** (Python 3.11+): API REST + WebSockets
- **SQLModel**: ORM y validación
- **PostgreSQL**: Base de datos principal
- **ONNX Runtime**: Inferencia ML en CPU
- **Redis** (opcional): Cache y colas

### Frontend
- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS**: Estilos utility-first
- **Zustand**: Gestión de estado
- **Workbox**: Service Worker y PWA
- **Socket.IO Client**: Tiempo real

### ML/IA
- **ONNX Runtime**: Inferencia optimizada
- **PyTorch**: Transfer learning (opcional)
- **OpenCV**: Procesamiento de imágenes

### DevOps
- **Docker** + **Docker Compose**: Contenedores
- **GitHub Actions**: CI/CD
- **Pytest** + **Vitest** + **Playwright**: Testing

## Inicio Rápido

### Requisitos previos
- Docker y Docker Compose
- Node.js 18+ (solo para desarrollo local sin Docker)
- Python 3.11+ (solo para desarrollo local sin Docker)

### Instalación con Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repo-url>
cd bus-cleaning-control
```

2. **Configurar variables de entorno**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Editar los archivos .env según sea necesario
```

3. **Levantar todos los servicios**
```bash
docker compose up -d
```

4. **Aplicar migraciones de base de datos**
```bash
docker compose exec backend alembic upgrade head
```

5. **Crear usuario administrador inicial**
```bash
docker compose exec backend python -m app.scripts.create_admin
```

6. **Acceder a la aplicación**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:5173/admin

### Credenciales por defecto
- **Email**: admin@buses.cl
- **Password**: Admin123!

**¡CAMBIAR INMEDIATAMENTE EN PRODUCCIÓN!**

## Desarrollo Local (sin Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configurar DATABASE_URL en .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Estructura del Proyecto

```
bus-cleaning-control/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints
│   │   ├── core/        # Config, seguridad, deps
│   │   ├── models/      # Modelos SQLModel
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Lógica de negocio
│   │   └── main.py      # Entry point
│   ├── tests/           # Tests backend
│   ├── alembic/         # Migraciones DB
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React App
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas/Vistas
│   │   ├── stores/      # Zustand stores
│   │   ├── services/    # API clients
│   │   └── utils/       # Utilidades
│   ├── public/
│   │   └── models/      # Modelos ML (ONNX)
│   ├── package.json
│   └── Dockerfile
├── ml/                  # ML/IA
│   ├── models/          # Modelos entrenados
│   ├── scripts/         # Scripts de entrenamiento
│   └── notebooks/       # Jupyter notebooks
├── docker-compose.yml
└── .github/
    └── workflows/       # CI/CD
```

## Uso de la Aplicación

### Vista Móvil (Operario)

1. **Acceder a la app**: Abrir en navegador móvil o instalar PWA
2. **Seleccionar PPU**: Buscar o crear nueva patente
3. **Activar cámara**: Permitir acceso a cámara
4. **Análisis automático**: El sistema analiza cada 500ms automáticamente
5. **Ver resultado**: Badge muestra Limpio/Sucio/Dudoso + sugerencias
6. **Agregar observaciones**: Escribir notas adicionales
7. **Enviar registro**: Presionar botón "Enviar"
8. **Modo offline**: Los registros se guardan y sincronizan al recuperar conexión

### Panel Administrativo

1. **Dashboard**: Vista general con KPIs y stream en tiempo real
2. **Reportes**: Filtrar por fecha, PPU, operario, estado
3. **Exportar**: Descargar CSV o PDF
4. **Alertas**: Ver y resolver alertas automáticas
5. **Gestión**: CRUD de PPUs y usuarios
6. **Notificaciones**: Recibir alertas push en tiempo real

## Configuración Avanzada

### Variables de Entorno - Backend

```env
# Base de datos
DATABASE_URL=postgresql://user:password@db:5432/bus_cleaning

# Seguridad
SECRET_KEY=<generar-con-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

# Redis (opcional)
REDIS_URL=redis://redis:6379/0

# ML
ML_MODEL_PATH=/app/ml/models/cleaning_classifier.onnx
ML_CONFIDENCE_THRESHOLD=0.65

# Uploads
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Variables de Entorno - Frontend

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_OFFLINE=true
VITE_CAMERA_ANALYSIS_INTERVAL=500
```

## Testing

### Backend
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend
```bash
cd frontend
npm run test          # Unit tests (Vitest)
npm run test:e2e      # E2E tests (Playwright)
```

## Despliegue en Producción

### Checklist pre-producción

- [ ] Cambiar `SECRET_KEY` en backend/.env
- [ ] Cambiar credenciales de admin
- [ ] Configurar CORS correctamente
- [ ] Usar PostgreSQL real (no SQLite)
- [ ] Configurar backups de base de datos
- [ ] Habilitar HTTPS/SSL
- [ ] Configurar límites de rate-limiting
- [ ] Revisar logs y monitoreo
- [ ] Probar notificaciones Web Push
- [ ] Validar funcionamiento offline

### Docker Compose para producción

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## API Documentation

La documentación interactiva de la API está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Modelo de IA

El sistema incluye un clasificador de limpieza básico entrenado con MobileNet. Para mejorar el modelo:

1. Recolectar dataset de imágenes (limpio/sucio/dudoso)
2. Ejecutar script de transfer learning:
```bash
cd ml
python scripts/train_classifier.py --dataset /path/to/dataset
```
3. Exportar a ONNX:
```bash
python scripts/export_to_onnx.py --checkpoint best_model.pth
```
4. Copiar modelo a `frontend/public/models/` y `backend/ml/models/`

## Troubleshooting

### La cámara no funciona
- Verificar permisos del navegador
- Usar HTTPS en producción (getUserMedia requiere contexto seguro)
- Probar con "Subir foto" como alternativa

### WebSockets no conectan
- Verificar CORS en backend
- Revisar firewall/proxy
- Comprobar URL de WebSocket en frontend/.env

### Base de datos no conecta
- Verificar que el contenedor `db` esté corriendo: `docker compose ps`
- Revisar logs: `docker compose logs db`
- Verificar credenciales en .env

### Modelo de IA no carga
- Verificar que el archivo .onnx exista en la ruta configurada
- Revisar logs de backend
- Usar modelo dummy si es necesario (ver `ML_USE_DUMMY=true`)

## Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de código
- **Backend**: Black, flake8, mypy
- **Frontend**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Tests**: Coverage mínimo 70%

## Licencia

MIT License - ver archivo [LICENSE](LICENSE)

## Soporte

Para reportar bugs o solicitar features, crear un issue en GitHub.

---

**Desarrollado con ❤️ para mejorar la calidad del transporte público**
