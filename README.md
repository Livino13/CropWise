# CropWise

Farmer-friendly crop recommendation and field planning: an ML crop ranker, deterministic field-specific growing plans, fertilizer and pest guidance, local weather, and a Gemini-powered assistant.

**Live:** [cropwise-psi.vercel.app](https://cropwise-psi.vercel.app) · **API:** [cropwise-api.vercel.app](https://cropwise-api.vercel.app) · **Docs:** [cropwise-api.vercel.app/docs](https://cropwise-api.vercel.app/docs)

## Features

- **51-crop recommendation** from FCM clustering, PSO feature weighting and a Random Forest classifier.
- **Crop Guide** with photos, in-season guidance, confidence bands and a soil-number glossary.
- **Field-specific plans** built from soil values, coordinates, weather and soil-test data.
- **Growing, fertilizer and pest guidance** with doses kept separate from AI narration.
- **AI assistant** across pages; the Gemini key stays server-side.
- **Fields, history, feedback**, weather lookup, and photos for all 51 crops (emoji fallback).

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Zustand, Leaflet |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| ML | FCM + PSO + Random Forest, 51 classes, ~99.7% CV accuracy |
| Data | SQLite locally; PostgreSQL supported |
| External | Open-Meteo weather, SoilGrids soil data, Gemini via OpenAI-compatible API |

The model ranks crops; plans come from a deterministic engine, not an LLM. Gemini is used only for chat and optional plan narration.

## Run locally

**Backend**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python train.py
python -m uvicorn app.main:app --reload
```

API at `http://127.0.0.1:8000`, interactive docs at `/docs`.

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

App at `http://localhost:5173`; Vite proxies `/api` to the local backend.

**Docker**

```powershell
$env:LLM_API_KEY="your-key"
docker compose up --build
```

Frontend on `:3000`, backend on `:8000`.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEY` | Gemini key. Chat is disabled when empty. |
| `LLM_MODEL`, `LLM_FALLBACK_MODEL` | Primary and fallback model names. |
| `LLM_BASE_URL` | OpenAI-compatible Gemini endpoint. |
| `DATABASE_URL` | SQLAlchemy URL. Defaults to local SQLite. |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins. |
| `SECRET_KEY` | Application secret. |

Copy `backend/.env.example` to `backend/.env`. Never commit `.env`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/api/meta` | App and pipeline metadata |
| POST | `/api/recommend` | Rank crops from soil and climate inputs |
| POST | `/api/plan` | Growing, fertilizer and pest plan |
| POST | `/api/chat` | Gemini assistant |
| POST | `/api/weather` | Climate averages by coordinates |
| GET/POST | `/api/fields` | List or create fields |
| GET/PUT/DELETE | `/api/fields/{id}` | Read, update or delete a field |
| GET/PATCH | `/api/history` | Recommendation history |
| POST/GET | `/api/feedback` | Submit or read feedback |

Full request/response schemas are in `/docs`.

## Deploy

Two Vercel projects are built from this repository:

- **Frontend** (`cropwise`): root directory `frontend`, Vite preset, `VITE_API_URL=https://cropwise-api.vercel.app`. Pushes to `main` deploy it automatically.
- **Backend** (`cropwise-api`): `backend/api/index.py` exposes the FastAPI ASGI app and `backend/vercel.json` rewrites all paths to it. Deploy from the CLI so the trained model ships with the function:

```powershell
cd backend
python build.py    # trains only if model.joblib is missing
vercel --prod
```

`model.joblib` (~44 MB) is git-ignored and bundled through `includeFiles`. Set `LLM_API_KEY`, `LLM_MODEL`, `LLM_FALLBACK_MODEL`, `LLM_BASE_URL`, `CORS_ORIGINS` and `SECRET_KEY` in the Vercel project; `DATABASE_URL` defaults to `sqlite:////tmp/cropwise.db`.

## Project layout

```text
backend/
  api/index.py          Vercel ASGI entrypoint
  app/ml/               ML pipeline and model artifacts
  app/routers/          FastAPI endpoints
  app/services/         Crop profiles, agronomy, plan engine, LLM client
  data/                 Training data
frontend/
  public/crops/         Crop photos
  src/pages/            Dashboard, Result, Crop Guide, Fields, History, Profile
docker-compose.yml
```

## Limitations

- Sign-in is a local demo flow; add real authentication before public multi-user use.
- Fertilizer and pesticide doses are guidance only; confirm them with a local dealer or agriculture officer.
- Vercel uses SQLite in `/tmp`, which is ephemeral; set `DATABASE_URL` to PostgreSQL (Neon, Supabase) for persistence.
- Crop photo licensing should be reviewed before making the repository public.

## License

No license has been selected yet.
