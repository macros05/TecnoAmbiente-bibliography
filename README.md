Biblio Tecnoambiente

Aplicación web para la gestión bibliográfica de Tecnoambiente: altas, consulta, búsqueda con filtros y administración de referencias.








✨ Características

Catálogo de referencias con metadatos (título, autores, categoría, etiquetas…).

Búsqueda y filtros por palabra clave/categoría/fecha.

Detalle de cada referencia.

CRUD (crear/editar/eliminar) para usuarios con permiso.

API REST documentada automáticamente en /docs (OpenAPI).

Angular Universal (SSR) opcional para mejor SEO y rendimiento.

🗂️ Estructura del repositorio
biblio-tecnoambiente/
├─ backend/                     # API FastAPI (Python)
│  ├─ main.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ crud.py
│  ├─ auth.py
│  ├─ database.py
│  ├─ requirements.txt
│  └─ uploads/                  # (vacía; no se versiona contenido)
├─ frontend/                    # Angular (SSR opcional)
│  ├─ src/
│  ├─ angular.json
│  └─ package.json
├─ database/                    # dump.sql (estructura y/o datos de ejemplo)
├─ docs/                        # capturas, diagramas (opcional)
├─ .gitignore
├─ .gitattributes
├─ .env.example                 # plantilla de variables
└─ README.md

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
