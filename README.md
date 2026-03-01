# Biblio Tecnoambiente

[![API: FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#)
[![Frontend: Angular](https://img.shields.io/badge/Frontend-Angular%20(SSR)-DD0031)](#)
[![DB: MySQL 8](https://img.shields.io/badge/DB-MySQL%208-4479A1)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#-license)

## Table of Contents

- [✨ Features](#-features)
- [🧱 Architecture](#-architecture)
- [🧰 Requirements](#-requirements)
- [🚀 Getting Started](#-getting-started-local-without-docker)
- [🔌 Endpoints](#-endpoints-overview)
- [🖼️ Screenshots](#️-screenshots)
- [🔐 Security](#-security)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Author](#-author)
- [📄 License](#-license)

Web application for bibliography management at Tecnoambiente: create, browse, search with filters and manage references.

---

## ✨ Features

- Reference catalogue with metadata (title, authors, category, tags…).
- Search and filters by keyword, category and date.
- Detail view for each reference.
- Full CRUD (create / edit / delete) for users with the right permissions.
- Auto-documented REST API at **/docs** (OpenAPI).
- Angular Universal (SSR) optional support for better SEO and performance.

<img width="571" height="438" alt="image" src="https://github.com/user-attachments/assets/58dd9622-533d-4664-adf7-41cd85f72445" />

---

## 🧱 Architecture

```mermaid
flowchart LR
  FE["Angular (optional SSR)"] -- HTTP --> BE[FastAPI]
  BE -- SQLAlchemy --> DB[(MySQL 8)]
```

---

## 🧰 Requirements

- Python 3.11
- MySQL 8+
- Node.js 18+ and npm

---

## 🚀 Getting Started (local, without Docker)

### 1) Database (MySQL)

```bash
mysql -u root -p
> CREATE DATABASE tecnoambiente;
> exit
# (Optional) Import sample data
mysql -u root -p tecnoambiente < database/dump.sql
```

### 2) Backend (FastAPI)

```bash
cd backend
python -m venv venv                 # Windows: py -3 -m venv venv
# Activate environment:
#   Windows:      .\venv\Scripts\activate
#   macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
```

Configure the database connection via **.env**. Copy the example file and fill in your credentials:

**.env (at root or inside backend/ if loaded with dotenv):**

```
DATABASE_URL=mysql+pymysql://USER:PASS@localhost:3306/tecnoambiente
JWT_SECRET=change-me
ALGORITHM=HS256
```

Start the API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Swagger UI: http://localhost:8000/docs
```

### 3) Frontend (Angular)

```bash
cd frontend
npm install

# SPA development mode
npm run start            # http://localhost:4200

# SSR (if configured)
npm run build:ssr
npm run serve:ssr        # http://localhost:4000
```

Set the API URL in `src/environments/environment*.ts`:

```ts
export const environment = {
  production: false,                // true in environment.prod.ts
  apiUrl: 'http://localhost:8000'   // or 'https://your-domain.com/api'
};
```

---

## 🔌 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/referencias` | List / search references (query params for filters & pagination) |
| GET | `/api/referencias/{id}` | Get a single reference |
| POST | `/api/referencias` | Create a reference (requires permissions) |
| PUT | `/api/referencias/{id}` | Update a reference |
| DELETE | `/api/referencias/{id}` | Delete a reference |

Full documentation available at **/docs** and **/redoc** while the backend is running.

---

## 🧪 Code Quality (optional)

**Backend**

```bash
pip install ruff black pytest
ruff check backend        # lint
black backend             # format
pytest -q                 # run tests
```

**Frontend**

```bash
npm run lint
npm run test
```

---

## 🖼️ Screenshots

### Home
<img width="1470" height="828" alt="image" src="https://github.com/user-attachments/assets/12d6ff47-3430-4e44-99fa-e79d63f7c040" />

### Register
<img width="1461" height="704" alt="image" src="https://github.com/user-attachments/assets/d9833e7f-296f-402a-9faf-4a8372b1ea3e" />

### Upload Documents
<img width="1470" height="636" alt="image" src="https://github.com/user-attachments/assets/175c85a5-d8af-4f10-82f9-1c00d9f3d02a" />

### PDF List
<img width="1470" height="800" alt="image" src="https://github.com/user-attachments/assets/6a24ca5b-0322-45a4-bbc4-5839b8d91c13" />

### Search
<img width="1470" height="802" alt="image" src="https://github.com/user-attachments/assets/1528a249-a3e4-49fa-96fb-967c68487d58" />

### Edit Documents
<img width="1188" height="718" alt="image" src="https://github.com/user-attachments/assets/7bbc68ac-6d48-4554-903a-847d057b72df" />

---

## 🔐 Security

- Input validation with **Pydantic** (backend).
- CORS restricted to the production domain.
- HTTPS in production via reverse proxy (**NGINX**).

---

## 🗺️ Roadmap

- [ ] Advanced pagination and sorting in listings
- [ ] Role-based authentication (admin / reader)
- [ ] Full-text search and tag-based filtering
- [ ] CI pipeline (lint + build + tests)

---

## 👤 Author

**Marcos Morales** · moralesgonzalezmarcos104@gmail.com

---

## 📄 License

This project is distributed under the **MIT** license.
See the `LICENSE` file at the root of the repository.
