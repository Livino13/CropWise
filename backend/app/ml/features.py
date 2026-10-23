"""Feature engineering: 7 raw soil/climate inputs + agronomic interaction features."""
import pandas as pd
import numpy as np

RAW_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

DERIVED_COLUMNS = [
    "NPK_sum",
    "N_P_ratio",
    "K_P_ratio",
    "log_rainfall",
    "temp_humidity_index",
    "aridity_index",
]

# 13 model features actually fed to training (previously synthetics were computed then discarded)
FEATURE_COLUMNS = RAW_COLUMNS + DERIVED_COLUMNS


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["NPK_sum"] = df["N"] + df["P"] + df["K"]
    df["N_P_ratio"] = df["N"] / (df["P"] + 1.0)
    df["K_P_ratio"] = df["K"] / (df["P"] + 1.0)
    df["log_rainfall"] = np.log1p(df["rainfall"])
    df["temp_humidity_index"] = df["temperature"] * df["humidity"] / 100.0
    df["aridity_index"] = df["rainfall"] / (df["temperature"] + 1.0)
    return df
