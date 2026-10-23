from fastapi import APIRouter
from ..services.retrain import start_retrain, get_status

router = APIRouter(prefix="/api/model", tags=["model"])


@router.post("/retrain")
def retrain():
    """Start a background retrain using farmer feedback rows. 409 if already running."""
    started = start_retrain()
    if not started:
        return {"status": "already_running", **{k: get_status().get(k) for k in ("last_started",)}}
    return {"status": "started"}


@router.get("/status")
def status():
    return get_status()
