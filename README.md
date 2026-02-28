# Biblio Tecnoambiente

[![API: FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#)
[![Frontend: Angular](https://img.shields.io/badge/Frontend-Angular%20(SSR)-DD0031)](#)
[![DB: MySQL 8](https://img.shields.io/badge/DB-MySQL%208-4479A1)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#-licencia)

## Índice
- [✨ Características](#-características)
- [🧱 Arquitectura](#-arquitectura)
- [🧰 Requisitos](#-requisitos)
- [🚀 Puesta en marcha](#-puesta-en-marcha-local-sin-docker)
- [🔌 Endpoints](#-endpoints-vista-general)
- [🖼️ Capturas](#️-capturas)
- [🔐 Seguridad](#-seguridad)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Autor](#-autor)
- [📄 Licencia](#-licencia)

Aplicación web para la gestión bibliográfica de Tecnoambiente: altas, consulta, búsqueda con filtros y administración de referencias.

---

## ✨ Características

- Catálogo de referencias con metadatos (título, autores, categoría, etiquetas…).
- Búsqueda y filtros por palabra clave/categoría/fecha.
- Detalle de cada referencia.
- CRUD (crear/editar/eliminar) para usuarios con permiso.
- API REST documentada automáticamente en **/docs** (OpenAPI).
- Angular Universal (SSR) opcional para mejor SEO y rendimiento.

<img width="571" height="438" alt="image" src="https://github.com/user-attachments/assets/58dd9622-533d-4664-adf7-41cd85f72445" />

---

## 🧱 Arquitectura
```mermaid
flowchart LR
  FE["Angular (SSR opcional)"] -- HTTP --> BE[FastAPI]
  BE -- SQLAlchemy --> DB[(MySQL 8)]


## 🧰 Requisitos

- Python 3.11
- MySQL 8+
- Node.js 18+ y npm

---

## 🚀 Puesta en marcha (local, sin Docker)

### 1) Base de datos (MySQL)
```bash
mysql -u root -p
> CREATE DATABASE tecnoambiente;
> exit

# (Opcional) Importar datos de ejemplo
mysql -u root -p tecnoambiente < database/dump.sql
```

### 2) Backend (FastAPI)
```bash
cd backend
python -m venv venv                 # Windows: py -3 -m venv venv
# Activar entorno:
#   Windows: .\venv\Scripts\activate
#   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Configura la conexión a la BD (recomendado vía **.env**). Copia el ejemplo de la raíz y ajusta credenciales:

**.env (en la raíz o en backend/ si cargas con dotenv):**
```
DATABASE_URL=mysql+pymysql://USER:PASS@localhost:3306/tecnoambiente
JWT_SECRET=change-me
ALGORITHM=HS256
```

Arranca la API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Swagger: http://localhost:8000/docs
```

### 3) Frontend (Angular)
```bash
cd frontend
npm install

# Desarrollo SPA
npm run start            # http://localhost:4200

# SSR (si está configurado)
npm run build:ssr
npm run serve:ssr        # http://localhost:4000
```

Configura la URL de la API en `src/environments/environment*.ts`:

```ts
export const environment = {
  production: false,                // true en environment.prod.ts
  apiUrl: 'http://localhost:8000'   // o 'https://tu-dominio.com/api'
};
```

---

## 🔌 Endpoints (vista general)

- GET /api/referencias — listar/buscar referencias (query params para filtros/paginación)
- GET /api/referencias/{id} — detalle de una referencia
- POST /api/referencias — crear (requiere permisos)
- PUT /api/referencias/{id} — actualizar
- DELETE /api/referencias/{id} — eliminar

La documentación completa está en **/docs** y **/redoc** con el backend en ejecución.

---

## 🧪 Calidad y utilidades (opcional)

**Backend**
```bash
pip install ruff black pytest
ruff check backend        # lint
black backend             # format
pytest -q                 # tests si los añades
```

**Frontend**
```bash
npm run lint
npm run test
```

---

## 🖼️ Capturas


### INICIO
<img width="1470" height="828" alt="image" src="https://github.com/user-attachments/assets/12d6ff47-3430-4e44-99fa-e79d63f7c040" />

### REGISTRO
<img width="1461" height="704" alt="image" src="https://github.com/user-attachments/assets/d9833e7f-296f-402a-9faf-4a8372b1ea3e" />

### SUBIDA DOCUMENTOS
<img width="1470" height="636" alt="image" src="https://github.com/user-attachments/assets/175c85a5-d8af-4f10-82f9-1c00d9f3d02a" />

### LISTA DE PDFS
<img width="1470" height="800" alt="image" src="https://github.com/user-attachments/assets/6a24ca5b-0322-45a4-bbc4-5839b8d91c13" />

### BUSCADOR
<img width="1470" height="802" alt="image" src="https://github.com/user-attachments/assets/1528a249-a3e4-49fa-96fb-967c68487d58" />

### MODIFICACIÓN DOCUMENTOS
<img width="1188" height="718" alt="image" src="https://github.com/user-attachments/assets/7bbc68ac-6d48-4554-903a-847d057b72df" />

---

## 🔐 Seguridad 

- Validación de entrada con **Pydantic** (backend).
- CORS restringido al dominio final en producción.
- HTTPS en producción (proxy inverso con **NGINX**).

---

## 🗺️ Roadmap

- Paginación avanzada y ordenación en listados
- Autenticación con roles (admin/lector)
- Búsqueda full-text / por etiquetas
- CI (lint + build + tests)

---

## 👤 Autor

**Marcos Morales** · moralesgonzalezmarcos104@gmail.com

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia **MIT**.  
Incluye el archivo `LICENSE` en la raíz.

