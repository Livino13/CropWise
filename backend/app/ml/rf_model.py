"""FCM + PSO + RF crop classification pipeline.

Flow (train): engineered features -> stratified split -> scale (train-only)
-> PSO feature weights (maximize CV accuracy on train) -> FCM soft-cluster
membership features -> hyperparameter-tuned RandomForest vs
HistGradientBoosting, champion selected by CV -> single holdout report.

Flow (serve): scale -> weight -> FCM membership -> champion.predict_proba.
"""
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.base import clone
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import (
    train_test_split, RandomizedSearchCV, StratifiedKFold, cross_val_score,
)
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .features import derive_features, FEATURE_COLUMNS
from .fcm import FCM, membership, xie_beni
from .pso import PSO

CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", "mungbean",
    "blackgram", "lentil", "pomegranate", "banana", "mango", "grapes", "watermelon",
    "muskmelon", "apple", "orange", "papaya", "coconut", "cotton", "jute", "coffee",
    "barley", "bitter_gourd", "blackpepper", "bottle_gourd", "brinjal", "cabbage",
    "cardamom", "cauliflower", "coriander", "cucumber", "drumstick", "garlic",
    "horsegram", "jackfruit", "okra", "onion", "pineapple", "potato", "pumpkin",
    "radish", "ragi", "rapeseed", "sorghum", "soybean", "sunflower", "sweet_potato",
    "tomato", "turmeric", "wheat",
]

CROP_LABELS = {crop: i for i, crop in enumerate(CROPS)}
REVERSE_LABELS = {i: crop for crop, i in CROP_LABELS.items()}

N_CLUSTERS = 5
FCM_M = 2.0


def _membership_features(Xw: np.ndarray, centers: np.ndarray, m: float = FCM_M) -> np.ndarray:
    """Soft cluster membership as extra features: (n_samples, n_clusters)."""
    return membership(Xw, centers, m).T


def transform_features(artifact: dict, X_raw: np.ndarray) -> np.ndarray:
    """Full inference transform: scale -> weight -> FCM membership features."""
    Xs = artifact["scaler"].transform(X_raw)
    Xw = Xs * artifact["weights"]
    centers = artifact.get("fcm_centers")
    if centers is not None:
        Xw = np.hstack([Xw, _membership_features(Xw, centers, artifact.get("fcm_m", FCM_M))])
    return Xw


def train_pipeline(csv_path: str = None, df: pd.DataFrame = None, save_path: str = None):
    if df is None:
        if csv_path is None:
            from .dataset import generate_crop_dataset
            df = generate_crop_dataset()
        else:
            df = pd.read_csv(csv_path)

    df_feat = derive_features(df)
    X = df_feat[FEATURE_COLUMNS].values.astype(float)
    y_raw = df_feat["label"].values

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # split BEFORE any fitting — scaler/PSO/FCM never see the holdout (no leakage)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    Xs_train = scaler.fit_transform(X_train)
    Xs_test = scaler.transform(X_test)

    # PSO: feature weights maximizing stratified CV accuracy on the training split
    pso = PSO(n_particles=12, n_iterations=20, w=0.7, c1=1.5, c2=1.5, seed=42)
    weights = pso.optimize(Xs_train, y_train)
    Xw_train = Xs_train * weights
    Xw_test = Xs_test * weights

    # FCM on the weighted training space -> soft membership features for the classifier
    fcm = FCM(n_clusters=N_CLUSTERS, m=FCM_M, max_iter=100, seed=42)
    centers, U = fcm.fit(Xw_train)
    xb = float(xie_beni(Xw_train, centers, U, FCM_M))

    F_train = np.hstack([Xw_train, U.T])
    F_test = np.hstack([Xw_test, _membership_features(Xw_test, centers)])

    # model comparison: tuned RF vs HistGradientBoosting, selected by CV
    searches = {
        "random_forest": RandomizedSearchCV(
            RandomForestClassifier(random_state=42, n_jobs=1),
            param_distributions={
                "n_estimators": [200, 300, 400, 500],
                "max_depth": [None, 12, 20, 30],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", 0.5],
            },
            n_iter=16, cv=3, scoring="accuracy", random_state=42, n_jobs=-1, refit=True,
        ),
        "hist_gradient_boosting": RandomizedSearchCV(
            HistGradientBoostingClassifier(random_state=42, early_stopping=False),
            param_distributions={
                "learning_rate": [0.03, 0.06, 0.1],
                "max_leaf_nodes": [15, 31, 63],
                "l2_regularization": [0.0, 0.5, 1.0],
                "max_iter": [200, 300],
            },
            n_iter=8, cv=3, scoring="accuracy", random_state=42, n_jobs=-1, refit=True,
        ),
    }
    comparison = {}
    for name, search in searches.items():
        search.fit(F_train, y_train)
        comparison[name] = {
            "cv3_mean": float(search.best_score_),
            "best_params": {k: (v if not isinstance(v, float) else round(v, 4)) for k, v in search.best_params_.items()},
        }

    champion_name = max(comparison, key=lambda k: comparison[k]["cv3_mean"])
    champion = searches[champion_name].best_estimator_
    comparison[champion_name]["selected"] = True

    # honest 5-fold CV of the selected model config
    cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv5_scores = cross_val_score(clone(champion), F_train, y_train, cv=cv5, scoring="accuracy", n_jobs=-1)

    # single holdout evaluation (reported, never used for selection)
    y_pred = champion.predict(F_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0)

    importances = None
    if hasattr(champion, "feature_importances_"):
        n_raw = len(FEATURE_COLUMNS)
        names = FEATURE_COLUMNS + [f"fcm_cluster_{i}" for i in range(N_CLUSTERS)]
        importances = {n: float(v) for n, v in zip(names, champion.feature_importances_)}

    artifact = {
        "model": champion,
        "model_name": champion_name,
        "scaler": scaler,
        "weights": weights,
        "fcm_centers": centers,
        "fcm_m": FCM_M,
        "n_clusters": N_CLUSTERS,
        "feature_columns": FEATURE_COLUMNS,
        "label_encoder": le,
        "accuracy": float(acc),
        "cv_scores": {"5fold_mean": float(cv5_scores.mean()), "5fold_std": float(cv5_scores.std())},
        "model_comparison": comparison,
        "confusion_matrix": cm,
        "report": report,
        "feature_importances": importances,
        "xie_beni": xb,
        "pso_cv_accuracy": float(pso.best_cv_accuracy_),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(df)),
    }

    if save_path:
        save_model(artifact, save_path)

    return artifact


def predict_top3(*args, **kwargs):
    """Supports both:
      - spec: predict_top3(model, weights, feature_columns, soil_input_dict)
      - production: predict_top3(artifact, soil_dict)
    Returns list of 3 dicts {crop, confidence} sorted descending.
    """
    if len(args) == 4:
        model, weights, feature_columns, soil = args
        if isinstance(model, dict) and "model" in model:
            return _predict_from_artifact(model, weights)
        scaler = kwargs.get("scaler")
        le = kwargs.get("label_encoder")
        df = pd.DataFrame([soil])
        df = derive_features(df)
        X = df[feature_columns].values.astype(float)
        if scaler is not None:
            X = scaler.transform(X)
        Xw = X * np.asarray(weights)
        proba = model.predict_proba(Xw)[0]
        top_idx = np.argsort(proba)[::-1][:3]
        if le is not None:
            labels = le.inverse_transform([int(i) for i in top_idx])
        else:
            labels = [REVERSE_LABELS.get(int(i), str(int(i))) for i in top_idx]
        return [{"crop": str(labels[j]), "confidence": float(proba[int(top_idx[j])])} for j in range(3)]

    if len(args) == 2:
        artifact, soil = args
        return _predict_from_artifact(artifact, soil, top_n=int(kwargs.get("top_n", 3)))
    if len(args) == 1 and isinstance(args[0], dict) and "model" in args[0]:
        artifact = args[0]
        soil = kwargs.get("soil") or kwargs.get("soil_input_dict") or next((v for v in kwargs.values() if isinstance(v, dict)), None)
        if soil is None:
            raise ValueError("soil dict required")
        return _predict_from_artifact(artifact, soil, top_n=int(kwargs.get("top_n", 3)))
    if "artifact" in kwargs:
        return _predict_from_artifact(kwargs["artifact"], kwargs.get("soil") or kwargs.get("soil_input_dict"), top_n=int(kwargs.get("top_n", 3)))
    raise TypeError(f"predict_top3 called with unexpected args {args} {kwargs}")


def _predict_from_artifact(artifact: dict, soil: dict, top_n: int = 3):
    df = pd.DataFrame([soil])
    df = derive_features(df)
    X_raw = df[artifact["feature_columns"]].values.astype(float)
    F = transform_features(artifact, X_raw)
    proba = artifact["model"].predict_proba(F)[0]
    top_idx = np.argsort(proba)[::-1][:top_n]
    le = artifact["label_encoder"]
    return [{"crop": le.inverse_transform([int(i)])[0], "confidence": float(proba[int(i)])} for i in top_idx]


def save_model(artifact: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)


def train_yield_model(df: pd.DataFrame, crop_col: str = "label", yield_col: str = "yield_t_ha"):
    """Regress expected yield (t/ha) from soil/climate inputs + crop identity.

    Requires >= 50 labeled rows; returns (model, meta) or (None, reason).
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.preprocessing import LabelEncoder as _LE

    needed = FEATURE_COLUMNS + [crop_col, yield_col]
    data = df.dropna(subset=[crop_col, yield_col]).copy()
    data = data[data[crop_col].isin(CROPS)]
    if len(data) < 50:
        return None, f"only {len(data)} labeled yield rows (need >= 50)"

    le_c = _LE().fit(data[crop_col])
    X = derive_features(data)[FEATURE_COLUMNS].values.astype(float)
    X = np.hstack([X, le_c.transform(data[crop_col]).reshape(-1, 1)])
    y = data[yield_col].astype(float).values

    model = HistGradientBoostingRegressor(random_state=42, max_iter=200)
    model.fit(X, y)
    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    meta = {"n_rows": int(len(data)), "cv_r2_mean": float(scores.mean()), "crop_encoder": le_c}
    return model, meta


def predict_yield(artifact: dict, soil: dict, crop: str):
    """Expected yield (t/ha) for a crop under the given conditions, or None."""
    model = artifact.get("yield_model")
    meta = artifact.get("yield_meta") or {}
    le_c = meta.get("crop_encoder")
    if model is None or le_c is None or crop not in le_c.classes_:
        return None
    try:
        df = derive_features(pd.DataFrame([soil]))
        X = df[FEATURE_COLUMNS].values.astype(float)
        X = np.hstack([X, le_c.transform([crop]).reshape(-1, 1)])
        return float(model.predict(X)[0])
    except Exception:
        return None


def load_model(path: str):
    return joblib.load(path)


load_artifact = load_model
