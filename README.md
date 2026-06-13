# social-media-app

A backend API for a social media platform built with **Python 3.14**, **FastAPI**, and **PostgreSQL**, following **Domain-Driven Design** principles.

## Features

- **Identity & Access Management** — user registration, login (JWT), logout (token blacklisting), profile retrieval
- **Argon2 password hashing** — industry-standard password security
- **Domain-Driven Design** — clean separation into domain, application, infrastructure, and presentation layers
- **Unit of Work** pattern for transactional integrity
- **Domain Events** — in-memory event bus for decoupled side effects
- **Async everything** — async SQLAlchemy + asyncpg for high concurrency

## Tech Stack

| Layer            | Technology                                       |
|------------------|--------------------------------------------------|
| Language         | Python 3.14                                      |
| Framework        | FastAPI + Uvicorn                                |
| Database         | PostgreSQL 16 + asyncpg                          |
| ORM              | SQLAlchemy 2.x (async)                           |
| Migrations       | Alembic                                          |
| Validation       | Pydantic v2                                      |
| Auth             | JWT (pyjwt) + Argon2 (passlib / argon2-cffi)     |
| Testing          | pytest, pytest-asyncio, httpx                    |
| Linting          | Ruff                                             |
| Package Manager  | uv                                               |
| Containerization | Docker + Docker Compose                          |

## Architecture

The project is structured as a **monolithic backend** with a single bounded context (Identity) organized in four layers:

```
app/
├── identity/
│   ├── domain/          # Entities, value objects, repository interfaces, domain events
│   ├── application/     # Use case handlers, DTOs
│   ├── infrastructure/  # SQLAlchemy models, repository implementations, JWT/password services
│   └── presentation/    # FastAPI router, exception mappers
└── shared/              # Base classes, config, event bus, database session factory
```

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/install/)

### Running the app

```bash
cp .env.example .env
docker compose up app
```

The API is available at **http://localhost:5001** — interactive docs at **http://localhost:5001/docs**.

### Running tests

```bash
docker compose run --rm app-test
```

### Other Compose services

| Service       | Description                                     |
|---------------|-------------------------------------------------|
| `app`         | Production server on port 5001                  |
| `app-debug`   | Dev server with debugpy + reload (port 5678)    |
| `app-test`    | Runs `pytest ./tests`                           |
| `migrations`  | Applies Alembic migrations on startup           |
| `postgres`    | PostgreSQL 16 on port 5433                      |

## API Endpoints

| Method | Endpoint         | Description                  |
|--------|------------------|------------------------------|
| POST   | `/auth/register` | Register a new user          |
| POST   | `/auth/login`    | Login, receive JWT token     |
| POST   | `/auth/logout`   | Logout, blacklist all tokens |
| GET    | `/auth/me`       | Get current user profile     |

## Environment Variables

| Variable             | Default                                              | Description              |
|----------------------|------------------------------------------------------|--------------------------|
| `DATABASE_URL`       | `postgresql+asyncpg://postgres:postgres@postgres:5432/appdb` | Async DB connection |
| `SYNC_DATABASE_URL`  | `postgresql://postgres:postgres@postgres:5432/appdb` | Sync DB (Alembic)        |
| `SECRET_KEY`         | *(required)*                                         | JWT signing secret       |
| `POSTGRES_PORT`      | `5433`                                               | Host PostgreSQL port     |
| `APP_PORT`           | `5001`                                               | Host app port            |
| `DEBUG_PORT`         | `5678`                                               | Host debugger port       |

## Running without Docker

```bash
uv sync
cp .env.example .env
# ensure DATABASE_URL points to a running PostgreSQL
alembic upgrade head
uvicorn app.main:app --reload
pytest
```