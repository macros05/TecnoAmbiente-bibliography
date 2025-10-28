Biblio Tecnoambiente
[![API: FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#)
[![Frontend: Angular](https://img.shields.io/badge/Frontend-Angular%20(SSR)-DD0031)](#)
[![DB: MySQL 8](https://img.shields.io/badge/DB-MySQL%208-4479A1)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#-licencia)
## Índice
- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Puesta en marcha](#puesta-en-marcha)
- [Variables de entorno](#variables-de-entorno)
- [Endpoints](#endpoints)
- [Capturas](#capturas)
- [Roadmap](#roadmap)
- [Autor](#autor)
- [Licencia](#licencia)

Aplicación web para la gestión bibliográfica de Tecnoambiente: altas, consulta, búsqueda con filtros y administración de referencias.








✨ Características

Catálogo de referencias con metadatos (título, autores, categoría, etiquetas…).

Búsqueda y filtros por palabra clave/categoría/fecha.

Detalle de cada referencia.

CRUD (crear/editar/eliminar) para usuarios con permiso.

API REST documentada automáticamente en /docs (OpenAPI).

Angular Universal (SSR) opcional para mejor SEO y rendimiento.
<img width="571" height="438" alt="image" src="https://github.com/user-attachments/assets/58dd9622-533d-4664-adf7-41cd85f72445" />

🚀 Puesta en marcha (local, sin Docker)
Requisitos

Python 3.11

MySQL 8+

Node.js 18+ y npm

1) Base de datos (MySQL)
mysql -u root -p
> CREATE DATABASE tecnoambiente;
> exit

# (Opcional) Importar datos de ejemplo
mysql -u root -p tecnoambiente < database/dump.sql

2) Backend (FastAPI)
cd backend
python -m venv venv                 # Windows: py -3 -m venv venv
# Activar entorno:
#   Windows: .\venv\Scripts\activate
#   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt


Configura la conexión a la BD (recomendado vía .env). Copia el ejemplo de la raíz y ajusta credenciales:

.env (en la raíz o en backend/ si cargas con dotenv):

DATABASE_URL=mysql+pymysql://USER:PASS@localhost:3306/tecnoambiente
JWT_SECRET=change-me
ALGORITHM=HS256


Arranca la API:

uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Swagger: http://localhost:8000/docs

3) Frontend (Angular)
cd frontend
npm install

# Desarrollo SPA
npm run start            # http://localhost:4200

# SSR (si está configurado)
npm run build:ssr
npm run serve:ssr        # http://localhost:4000


Configura la URL de la API en src/environments/environment*.ts:

export const environment = {
  production: false,                // true en environment.prod.ts
  apiUrl: 'http://localhost:8000'   // o 'https://tu-dominio.com/api'
};

🔌 Endpoints (vista general)

GET /api/referencias — listar/buscar referencias (query params para filtros/paginación)

GET /api/referencias/{id} — detalle de una referencia

POST /api/referencias — crear (requiere permisos)

PUT /api/referencias/{id} — actualizar

DELETE /api/referencias/{id} — eliminar

La documentación completa está en /docs y /redoc con el backend en ejecución.

🧪 Calidad y utilidades (opcional)

Backend

pip install ruff black pytest
ruff check backend        # lint
black backend             # format
pytest -q                 # tests si los añades


Frontend

npm run lint
npm run test

🖼️ Capturas (opcional)

Añade imágenes en docs/ y enlázalas aquí:

Catálogo	Detalle	Formulario

	
	
🔐 Seguridad (mínimos)

No subir .env ni archivos de uploads/.

Validación de entrada con Pydantic (backend).

CORS restringido al dominio final en producción.

HTTPS en producción (proxy inverso con NGINX o similar).

🗺️ Roadmap

 Paginación avanzada y ordenación en listados

 Autenticación con roles (admin/lector)

 Búsqueda full-text / por etiquetas

 Exportación CSV/JSON

 Tests E2E (Playwright/Cypress)

 CI (lint + build + tests)


CAPTURAS 
INICIO

<img width="631" height="186" alt="image" src="https://github.com/user-attachments/assets/bb4defdf-6f3b-4263-ad4a-5bf9dc09fe25" />

REGISTRO

<img width="716" height="153" alt="image" src="https://github.com/user-attachments/assets/3e308e22-e494-4e71-b84a-1f6d00389ef5" />

SUBIDA DOCUMENTOS

<img width="710" height="171" alt="image" src="https://github.com/user-attachments/assets/3516f73a-08f8-486e-918e-1297beb465e8" />

BUSCADOR

<img width="599" height="300" alt="image" src="https://github.com/user-attachments/assets/120945f2-1083-4a85-bb5e-d3b1eae378d6" />

MODIFICACION DOCUMENTOS

<img width="617" height="328" alt="image" src="https://github.com/user-attachments/assets/21243861-2540-4013-b2f7-e99b30393ab4" />
