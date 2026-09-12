# Quant Decision Engine

Quantitative research and decision-support application (v0.1).

Python calculation engine + FastAPI backend + Next.js TypeScript frontend.

**Not a broker, trading platform, or investment advisor.** Research calculations only.

## Architecture

```
Frontend (Next.js :3000)
    → API client (services/api.ts)
        → FastAPI (localhost:8000)
            → Quant engine (app/quant/*)
```

## Backend

```bash
cd quant-decision-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Tests:

```bash
PYTHONPATH=. pytest -v
```

API: `POST /api/analysis` · docs at `/docs` · health at `/health`

## Frontend

```bash
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev                  # http://localhost:3000
```

## Local full stack

1. Start backend on port 8000
2. Start frontend on port 3000
3. Open http://localhost:3000 → New Analysis → select method → Run

## Conventions

- VaR/CVaR: positive loss
- Sample statistics: ddof=1
- Annualization default: 252
- All API payloads JSON-serializable

## UI

Mobile-first quantitative research interface. See `frontend/UI_SPEC.md`.
