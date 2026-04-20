# Submission Checklist

This document outlines the requirements for submitting the AI Decision Ecosystem Engine project.

## Environment Setup

- [ ] Docker and Docker Compose installed
- [ ] Python 3.10+ available (for local dev)
- [ ] PostgreSQL running (via Docker Compose)

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start all services (builds image, starts containers, runs migrations)
docker compose up --build

# Or use the helper script:
make start          # Linux/macOS
.\start.ps1         # Windows PowerShell
```

The API will be available at `http://localhost:8000`.

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_decision_engine

# Apply migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload
```

## Migrations

Alembic is configured for database version control.

```bash
# Apply migrations (auto-run in docker compose start)
alembic upgrade head

# Revert to previous (if needed)
alembic downgrade -1

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"
```

All migrations are committed in `alembic/versions/`.

## Running Tests

```bash
# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cfo_agent.py -v

# Run with coverage (if pytest-cov installed)
pytest --cov=app
```

**Test Coverage:**
- Unit tests for agents (CEO, CFO, HR scoring logic)
- Unit tests for aggregator (decision thresholds + boundary cases)
- Integration tests for API endpoints (happy path + 404 cases)
- Service-level tests for scenario queries

**Test Count:** 22 passing tests

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):
- Triggers on pull requests
- Installs dependencies from requirements.txt
- Runs `pytest -q`
- All checks must pass before merge

## Repository Structure

```
.
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── presentation/           # API layer (routes, schemas, DI)
│   ├── application/            # Use cases (orchestration)
│   ├── domain/                 # Business logic (agents, entities, services)
│   └── infrastructure/         # Database, ORM, repositories
├── alembic/                    # Database migrations
├── tests/                      # Unit and integration tests
├── docs/                       # Project documentation
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # App image definition
├── Makefile                    # Build/run helpers (Linux/macOS)
├── start.ps1                   # Build/run helper (Windows)
├── stop.ps1                    # Stop helper (Windows)
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

## Architecture

**Clean Architecture (Layered):**
- **Domain**: Pure business logic (agents, decision rules), no external dependencies
- **Application**: Use cases (orchestration of domain + repositories)
- **Infrastructure**: Database, ORM, repositories (persistence implementation)
- **Presentation**: API routes, request/response schemas (thin controllers)

**Key Principles:**
- Domain has no external dependencies
- All database access via Repository Pattern
- ORM-only (no raw SQL)
- Dependency Injection for service/repository wiring

See `docs/architecture.md` in README for detailed layer breakdown.

## Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/scenarios` | Create scenario |
| POST | `/api/v1/scenarios/{id}/simulate` | Run simulation |
| GET | `/api/v1/scenarios` | List scenarios (paginated) |
| GET | `/api/v1/scenarios/{id}` | Get scenario details |
| GET | `/api/v1/scenarios/{id}/simulation` | Get simulation results |

## Swagger Documentation

```
http://localhost:8000/docs       # Interactive Swagger UI
http://localhost:8000/redoc      # ReDoc alternative
```

## Submission Validation Checklist

- [ ] All tests pass (`pytest -q` → 22 passed)
- [ ] API starts without errors (`docker compose up --build`)
- [ ] Migrations apply cleanly (`docker compose exec app alembic upgrade head`)
- [ ] GET/POST endpoints respond correctly (see demo in `docs/demo.md`)
- [ ] 404 handling works (missing scenario, simulation not run)
- [ ] Scenario input contract documented in README
- [ ] Decision thresholds documented (≥75=APPROVE, 50–74=REVISE, <50=REJECT)
- [ ] Clean architecture maintained (no raw SQL, ORM-only)
- [ ] No AI/LLM APIs used (deterministic logic only)
- [ ] GitHub Actions CI passes on PR
- [ ] Kanban workflow documented in `docs/workflow.md`

## Demo

See `docs/demo.md` for a 3-minute walkthrough with exact commands.
