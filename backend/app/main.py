from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from .core.database import Base, engine
from .core.config import settings
# Import models so their tables are registered on Base.metadata before create_all
from .models import Field, Recommendation  # noqa: F401
from .routers import recommend, weather, analytics, fields, history, feedback, model, guidance, chat, plan


def _ensure_columns():
    """Additive migration for existing SQLite files (no Alembic in this project)."""
    insp = inspect(engine)
    if "fields" in insp.get_table_names():
        existing = {c["name"] for c in insp.get_columns("fields")}
        ddl = [
            ("soil_n", "FLOAT"), ("soil_p", "FLOAT"), ("soil_k", "FLOAT"),
            ("soil_ph", "FLOAT"), ("soil_tested_at", "TIMESTAMP"),
        ]
        with engine.begin() as conn:
            for name, col_type in ddl:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE fields ADD COLUMN {name} {col_type}"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    yield


app = FastAPI(title="CropWise API", version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def _sec_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router)
app.include_router(weather.router)
app.include_router(analytics.router)
app.include_router(fields.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(model.router)
app.include_router(guidance.router)
app.include_router(chat.router)
app.include_router(plan.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/meta")
def meta():
    return {"name": "CropWise", "version": "1.0.0", "pipeline": "FCM+PSO+RF"}

@app.get("/")
def root():
    return {"message": "CropWise API — see /docs"}
