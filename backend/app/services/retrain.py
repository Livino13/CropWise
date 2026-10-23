"""Closed feedback loop: retrain on real farmer outcomes with champion/challenger.

Recommendations rows carrying `actual_crop` become extra training samples. The
challenger is only promoted to model.joblib if its 5-fold CV accuracy beats the
incumbent (small tolerance). Artifacts are versioned under artifacts/model_v{n}.joblib
with a JSON manifest, so any previous model can be inspected.
"""
import json
import logging
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

logger = logging.getLogger("cropwise.retrain")

ARTIFACTS_DIR = Path(__file__).parent.parent / "ml" / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
MANIFEST_PATH = ARTIFACTS_DIR / "manifest.json"
BASE_CSV = Path(__file__).parent.parent.parent / "data" / "crop_data.csv"
PROMOTE_TOLERANCE = 0.005  # challenger may trail incumbent by up to 0.5% CV

_status = {"running": False, "last_result": None, "last_error": None, "last_started": None}
_lock = threading.Lock()


def get_status() -> dict:
    return dict(_status)


def start_retrain() -> bool:
    """Start a background retrain; returns False if one is already running."""
    if not _lock.acquire(blocking=False):
        return False
    if _status["running"]:
        _lock.release()
        return False
    _status["running"] = True
    _status["last_error"] = None
    _status["last_started"] = datetime.now(timezone.utc).isoformat()
    threading.Thread(target=_run_safe, daemon=True).start()
    return True


def _run_safe():
    try:
        _status["last_result"] = _run()
        _status["last_error"] = None
    except Exception as e:
        logger.exception("retrain failed")
        _status["last_error"] = str(e)
    finally:
        _status["running"] = False
        _lock.release()


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception:
            pass
    return {"current_version": 1, "history": []}


def _save_manifest(m: dict):
    MANIFEST_PATH.write_text(json.dumps(m, indent=2))


def record_training_run(artifact: dict, source: str, promoted: bool = True):
    """Bump version, keep a versioned copy, update manifest (used by train.py too)."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    version = int(manifest.get("current_version", 0)) + 1
    versioned = ARTIFACTS_DIR / f"model_v{version}.joblib"
    shutil.copy2(MODEL_PATH, versioned)
    manifest["current_version"] = version
    manifest["history"].append({
        "version": version,
        "trained_at": artifact.get("trained_at") or datetime.now(timezone.utc).isoformat(),
        "cv5_mean": (artifact.get("cv_scores") or {}).get("5fold_mean"),
        "holdout_accuracy": artifact.get("accuracy"),
        "model_name": artifact.get("model_name"),
        "n_samples": artifact.get("n_samples"),
        "source": source,
        "promoted": promoted,
    })
    manifest["history"] = manifest["history"][-20:]
    _save_manifest(manifest)
    return version


def _feedback_rows() -> pd.DataFrame:
    from ..core.database import SessionLocal
    from ..models.recommendation import Recommendation
    from ..ml.rf_model import CROPS

    db = SessionLocal()
    try:
        rows = (
            db.query(
                Recommendation.N, Recommendation.P, Recommendation.K,
                Recommendation.temperature, Recommendation.humidity,
                Recommendation.ph, Recommendation.rainfall,
                Recommendation.actual_crop, Recommendation.actual_yield,
            )
            .filter(Recommendation.actual_crop.isnot(None))
            .all()
        )
    finally:
        db.close()

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=[
        "N", "P", "K", "temperature", "humidity", "ph", "rainfall",
        "label", "yield_t_ha",
    ])
    # keep only valid crops and numeric soil/climate values inside model limits
    df = df[df["label"].isin(CROPS)]
    for col in ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]:
        df = df[pd.to_numeric(df[col], errors="coerce").notna()]
        df[col] = df[col].astype(float)
    return df.reset_index(drop=True)


def _run() -> dict:
    from ..ml.rf_model import train_pipeline, train_yield_model, load_model
    from ..routers.recommend import reset_artifact_cache

    df_base = pd.read_csv(BASE_CSV)
    df_fb = _feedback_rows()
    n_feedback = len(df_fb)
    df_all = pd.concat([df_base, df_fb], ignore_index=True) if n_feedback else df_base

    challenger = train_pipeline(df=df_all)  # not saved yet

    incumbent_cv = None
    if MODEL_PATH.exists():
        try:
            incumbent_cv = (load_model(str(MODEL_PATH)).get("cv_scores") or {}).get("5fold_mean")
        except Exception:
            logger.exception("could not read incumbent artifact")

    challenger_cv = challenger["cv_scores"]["5fold_mean"]
    promote = incumbent_cv is None or challenger_cv >= (incumbent_cv - PROMOTE_TOLERANCE)

    # yield regressor: trained whenever enough real labeled yields exist
    yield_meta = None
    if n_feedback >= 50:
        ym, yinfo = train_yield_model(df_fb)
        if ym is not None:
            challenger["yield_model"] = ym
            challenger["yield_meta"] = yinfo
            yield_meta = {"n_rows": yinfo["n_rows"], "cv_r2_mean": yinfo["cv_r2_mean"]}

    result = {
        "feedback_rows": n_feedback,
        "total_rows": len(df_all),
        "challenger_cv5": challenger_cv,
        "incumbent_cv5": incumbent_cv,
        "holdout_accuracy": challenger["accuracy"],
        "promoted": bool(promote),
        "yield_model": yield_meta,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }

    if promote:
        from ..ml.rf_model import save_model
        save_model(challenger, str(MODEL_PATH))
        version = record_training_run(challenger, source=f"retrain(+{n_feedback} feedback rows)")
        result["version"] = version
        reset_artifact_cache()
    else:
        result["note"] = "challenger did not beat incumbent — current model kept"
    return result
