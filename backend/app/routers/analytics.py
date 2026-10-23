from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/analytics")
def get_analytics():
    # share the lazy model cache with the recommend router (loads once, not per request)
    from .recommend import get_artifact
    art = get_artifact()
    if art is not None:
        try:
            cols = art.get("feature_columns", [])
            weights = art.get("weights", [])
            cm = art.get("confusion_matrix", [])
            acc = art.get("accuracy", 0)
            report = art.get("report", {})
            classes = list(art.get("label_encoder", {}).classes_) if hasattr(art.get("label_encoder", {}), "classes_") else []
            return {
                "feature_weights": {c: float(w) for c, w in zip(cols, weights)} if len(weights) else {},
                "feature_columns": cols,
                "weights": [float(w) for w in weights] if len(weights) else [],
                "accuracy": float(acc),
                "confusion_matrix": cm,
                "classes": classes,
                "report": report,
                "cv_scores": art.get("cv_scores", {}),
                "model_comparison": art.get("model_comparison", {}),
                "model_name": art.get("model_name", "random_forest"),
                "feature_importances": art.get("feature_importances") or {},
                "pso_cv_accuracy": art.get("pso_cv_accuracy"),
                "trained_at": art.get("trained_at"),
                "n_samples": art.get("n_samples"),
            }
        except Exception as e:
            return {"error": str(e), "accuracy": 0, "feature_weights": {}, "confusion_matrix": [], "classes": []}
    # defaults before training
    from ..ml.features import FEATURE_COLUMNS
    return {
        "feature_weights": {c: 1.0 for c in FEATURE_COLUMNS},
        "feature_columns": FEATURE_COLUMNS,
        "weights": [1.0]*len(FEATURE_COLUMNS),
        "accuracy": 0,
        "confusion_matrix": [],
        "classes": [],
        "report": {},
        "note": "Model not yet trained — run train.py",
    }
