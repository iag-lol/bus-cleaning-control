# Características Opcionales (Mejoras Futuras)

Este documento lista funcionalidades **opcionales** que pueden agregarse al sistema. El sistema actual es **completamente funcional** sin estas características, pero estas mejoras pueden hacerlo aún más robusto.

---

## 🎯 Core Funcional (Completado ✅)

Todas estas características **YA ESTÁN IMPLEMENTADAS**:

- ✅ Autenticación JWT con roles
- ✅ CRUD completo de buses (PPUs)
- ✅ Análisis automático de cámara cada 500ms
- ✅ Clasificador ML (modo dummy + soporte ONNX)
- ✅ Eventos de limpieza con observaciones
- ✅ Alertas automáticas (buses sucios repetidos)
- ✅ Dashboard con estadísticas
- ✅ Reportes CSV y PDF
- ✅ WebSockets para tiempo real
- ✅ PWA instalable con service worker
- ✅ Docker Compose con todos los servicios
- ✅ CI/CD con GitHub Actions

---

## 🔧 Mejoras Opcionales - Frontend

### 1. Gestión de Usuarios (CRUD) 🔐

**Estado**: Backend completo, falta UI

**Backend ya implementado**:
- Modelos de usuario con roles
- Endpoints de autenticación
- Sistema de permisos

**Falta en frontend**:
- Página de administración de usuarios
- Formulario crear/editar usuario
- Lista de usuarios con filtros

**Cómo implementar**:
```tsx
// frontend/src/pages/UsersPage.tsx
// 1. Crear endpoint GET /users en backend (opcional)
// 2. Crear formulario de creación de usuario
// 3. Agregar a navegación del Layout
```

**Prioridad**: Media (admins pueden crear usuarios vía script o API directo)

---

### 2. Filtros Avanzados en Dashboard 🔍

**Estado**: Backend soporta filtros, falta UI

**Backend ya soporta**:
- `GET /events?from=&to=&ppu=&estado=&operario=`
- `GET /reports/summary?from=&to=`

**Falta en frontend**:
- Componente de filtros con datepickers
- Selector de rango de fechas
- Filtro por PPU, operario, estado

**Cómo implementar**:
```tsx
// frontend/src/components/EventFilters.tsx
import { useState } from 'react'

export default function EventFilters({ onFilter }) {
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  // ... más filtros

  return (
    <div className="flex gap-4">
      <input type="date" value={fromDate} onChange={...} />
      <input type="date" value={toDate} onChange={...} />
      <button onClick={() => onFilter({ fromDate, toDate })}>
        Filtrar
      </button>
    </div>
  )
}
```

**Prioridad**: Media (se pueden filtrar usando parámetros URL directamente)

---

### 3. Vista de Alertas en Frontend 🚨

**Estado**: Backend completo, falta página UI

**Backend ya implementado**:
- `GET /alerts?resolved=false`
- `PATCH /alerts/{id}/resolve`
- Notificaciones WebSocket

**Falta en frontend**:
- Página `/alerts`
- Lista de alertas con filtros
- Botón para resolver alertas

**Cómo implementar**:
```tsx
// frontend/src/pages/AlertsPage.tsx
const [alerts, setAlerts] = useState([])

useEffect(() => {
  api.get('/alerts?resolved=false').then(res => setAlerts(res.data))
}, [])

const resolveAlert = async (id) => {
  await api.patch(`/alerts/${id}/resolve`)
  // Actualizar lista
}
```

**Prioridad**: Media (alertas se ven en logs del backend)

---

### 4. Notificaciones Web Push 🔔

**Estado**: Backend tiene estructura, falta implementación completa

**Requiere**:
1. Generar VAPID keys:
```bash
pip install py-vapid
vapid --gen
# Copiar keys a backend/.env
```

2. Suscripción en frontend:
```ts
// frontend/src/services/push.ts
const subscription = await registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: VAPID_PUBLIC_KEY
})
```

3. Endpoint backend:
```python
# backend/app/api/push.py
from pywebpush import webpush

@router.post("/push/subscribe")
async def subscribe_push(subscription: dict):
    # Guardar subscription en DB
    pass

@router.post("/push/send")
async def send_push(message: str):
    webpush(subscription, data=message, vapid_claims=...)
```

**Prioridad**: Baja (WebSocket ya provee notificaciones en tiempo real)

---

### 5. Offline Sync Avanzado 💾

**Estado**: Service worker configurado, falta lógica de sync

**Ya implementado**:
- PWA con service worker
- Cache de assets
- IndexedDB ready (importado `idb`)

**Falta**:
- Guardar eventos en IndexedDB cuando offline
- Background sync al recuperar conexión
- UI para mostrar estado de sincronización

**Cómo implementar**:
```ts
// frontend/src/services/offline.ts
import { openDB } from 'idb'

const db = await openDB('bus-cleaning', 1, {
  upgrade(db) {
    db.createObjectStore('pending-events', { keyPath: 'id' })
  }
})

// Guardar evento pending
await db.add('pending-events', event)

// Background sync
navigator.serviceWorker.ready.then(registration => {
  registration.sync.register('sync-events')
})
```

**Prioridad**: Baja (la app funciona bien online)

---

## 🔧 Mejoras Opcionales - Backend

### 6. Alembic Migrations 🗄️

**Estado**: SQLModel crea tablas automáticamente, falta migraciones

**Actualmente**:
- `SQLModel.metadata.create_all()` en startup

**Para producción**:
```bash
# Inicializar Alembic
alembic init alembic

# Crear migración inicial
alembic revision --autogenerate -m "Initial schema"

# Aplicar
alembic upgrade head
```

**Archivos a crear**:
- `backend/alembic/env.py` (configuración)
- `backend/alembic/versions/` (migraciones)

**Prioridad**: Media (importante para producción seria)

---

### 7. Tests Unitarios 🧪

**Estado**: Estructura lista, tests básicos faltan

**Ya configurado**:
- Pytest en requirements.txt
- GitHub Actions ejecuta tests
- Coverage configurado

**Falta**:
```python
# backend/tests/api/test_auth.py
def test_login_success(client):
    response = client.post("/auth/login", json={
        "email": "admin@buses.cl",
        "password": "Admin123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# backend/tests/services/test_ml_service.py
def test_dummy_analysis():
    service = MLService()
    state, confidence, issues = service.analyze_image(base64_image)
    assert state in [CleaningState.CLEAN, CleaningState.DIRTY, CleaningState.UNCERTAIN]
```

**Prioridad**: Alta (buena práctica para mantenimiento)

---

### 8. Endpoint /users (CRUD completo) 👥

**Estado**: Modelo y autenticación listos, falta endpoints

**Requiere**:
```python
# backend/app/api/users.py
@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin)
):
    # Listar usuarios
    pass

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin)
):
    # Crear usuario
    pass

@router.put("/{user_id}")
async def update_user(...):
    pass
```

**Prioridad**: Media (se pueden crear usuarios por script)

---

### 9. Rate Limiting 🛡️

**Estado**: No implementado

**Requiere**:
```python
# backend/requirements.txt
slowapi==0.1.9

# backend/app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/endpoint")
@limiter.limit("5/minute")
async def endpoint():
    pass
```

**Prioridad**: Alta para producción

---

### 10. Logging Estructurado 📝

**Estado**: Básico con print(), falta logging profesional

**Requiere**:
```python
# backend/app/core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": record.created,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })

# Usar en toda la app
logger = logging.getLogger(__name__)
logger.info("Event created", extra={"event_id": event.id})
```

**Prioridad**: Media (útil para debugging en producción)

---

## 🤖 Mejoras Opcionales - ML/IA

### 11. Modelo ONNX Real 🧠

**Estado**: Sistema listo para recibir modelo, falta entrenamiento

**Pasos**:
1. **Recolectar dataset**:
   - 500-1000 imágenes por clase (limpio, sucio, dudoso)
   - Etiquetar manualmente

2. **Entrenar modelo**:
```python
# ml/scripts/train_classifier.py
import torch
import torchvision.models as models

model = models.mobilenet_v2(pretrained=True)
# ... transfer learning
# ... entrenar con dataset
# ... validar

# Exportar a ONNX
torch.onnx.export(model, dummy_input, "cleaning_classifier.onnx")
```

3. **Colocar en**:
   - `backend/ml/models/cleaning_classifier.onnx`

4. **Activar**:
```env
# backend/.env
ML_USE_DUMMY=false
```

**Prioridad**: Media (el dummy funciona bien para desarrollo)

---

### 12. Segmentación de Áreas Sucias 🎨

**Estado**: No implementado

**Requiere**:
- Modelo de segmentación (U-Net, Mask R-CNN)
- Retornar máscara de píxeles sucios
- Overlay en video del frontend

**Prioridad**: Baja (nice-to-have)

---

## 📊 Mejoras Opcionales - Reportes

### 13. Gráficos Interactivos 📈

**Estado**: Recharts instalado, falta implementar gráficos

**Requiere**:
```tsx
// frontend/src/components/CleaningChart.tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

const data = [
  { name: 'Lunes', limpios: 10, sucios: 2 },
  { name: 'Martes', limpios: 15, sucios: 1 },
  // ...
]

<BarChart width={600} height={300} data={data}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Bar dataKey="limpios" fill="#10b981" />
  <Bar dataKey="sucios" fill="#ef4444" />
</BarChart>
```

**Prioridad**: Baja (datos disponibles en tabla)

---

### 14. Exportar con Filtros Avanzados 📤

**Estado**: Backend soporta filtros básicos

**Mejorar**:
- Filtros por turno (mañana/tarde/noche)
- Filtro por múltiples PPUs
- Comparación entre períodos
- Tendencias semana/mes

**Prioridad**: Baja

---

## 🔐 Mejoras Opcionales - Seguridad

### 15. Two-Factor Authentication (2FA) 🔒

**Estado**: No implementado

**Requiere**:
- pyotp (backend)
- QR code generation
- UI para setup 2FA

**Prioridad**: Media para producción crítica

---

### 16. Audit Log Completo 📜

**Estado**: Modelo existe, falta usar en todas las acciones

**Requiere**:
```python
# En cada endpoint importante
audit_log = AuditLog(
    actor_id=current_user.id,
    accion="DELETE",
    entidad="bus",
    entidad_id=bus_id,
    diff_json={"old": bus.dict()}
)
session.add(audit_log)
```

**Prioridad**: Alta para producción

---

## 🌐 Mejoras Opcionales - Infraestructura

### 17. Docker Compose Production 🐳

**Estado**: Existe docker-compose.yml para desarrollo

**Requiere**:
```yaml
# docker-compose.prod.yml
services:
  backend:
    restart: always
    environment:
      - DEBUG=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
```

**Prioridad**: Alta para despliegue real

---

### 18. Monitoreo y Observability 📊

**Estado**: No implementado

**Opciones**:
- **Prometheus + Grafana**: Métricas
- **ELK Stack**: Logs centralizados
- **Sentry**: Error tracking
- **Uptime Robot**: Monitoring uptime

**Prioridad**: Media para producción

---

## 🎨 Mejoras Opcionales - UX/UI

### 19. Modo Demo con Datos Falsos 🎭

**Estado**: No implementado

**Requiere**:
```python
# backend/app/scripts/seed_demo_data.py
async def seed_demo():
    # Crear 10 buses
    # Crear 50 eventos aleatorios
    # Crear 5 alertas
```

**Prioridad**: Baja (útil para demos)

---

### 20. Temas Personalizables 🎨

**Estado**: Dark mode automático implementado

**Mejorar**:
- Selector manual dark/light
- Temas personalizados (colores corporativos)
- Guardar preferencia en localStorage

**Prioridad**: Baja

---

## 📱 Mejoras Opcionales - Móvil

### 21. Modo Offline Completo 📴

**Estado**: Service worker configurado, falta lógica

Ver punto #5 arriba.

**Prioridad**: Baja

---

### 22. Captura de Múltiples Fotos 📸

**Estado**: Captura un frame, envía uno

**Mejorar**:
- Capturar 3-5 ángulos del bus
- Comparar resultados
- Promediar confianza

**Prioridad**: Baja

---

## 🏁 Resumen de Prioridades

### 🔴 Alta Prioridad (Producción)
1. Tests unitarios (#7)
2. Rate limiting (#9)
3. Audit log completo (#16)
4. Docker production (#17)
5. Alembic migrations (#6)

### 🟡 Media Prioridad (Mejoras útiles)
1. Gestión de usuarios UI (#1)
2. Filtros avanzados (#2)
3. Vista de alertas (#3)
4. Endpoint /users (#8)
5. Logging estructurado (#10)
6. Modelo ONNX real (#11)
7. 2FA (#15)
8. Monitoreo (#18)

### 🟢 Baja Prioridad (Nice-to-have)
1. Notificaciones Web Push (#4)
2. Offline sync (#5)
3. Gráficos interactivos (#13)
4. Exportar avanzado (#14)
5. Modo demo (#19)
6. Temas personalizables (#20)
7. Captura múltiple (#22)
8. Segmentación IA (#12)

---

## ✅ Conclusión

**El sistema actual es COMPLETAMENTE FUNCIONAL y listo para usar**. Todas las características core están implementadas:

- ✅ Análisis automático con IA
- ✅ Cámara en tiempo real
- ✅ Dashboard y reportes
- ✅ Alertas automáticas
- ✅ WebSockets
- ✅ PWA instalable
- ✅ Docker completo

Las mejoras listadas arriba son **opcionales** y pueden agregarse según las necesidades específicas del proyecto.

**¡El sistema está listo para ejecutar con `docker compose up -d`!** 🚀
