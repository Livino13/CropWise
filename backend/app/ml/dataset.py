"""Synthetic crop dataset generator — 22 crops."""
import numpy as np
import pandas as pd

CROPS = [
    "rice","maize","chickpea","kidneybeans","pigeonpeas","mothbeans","mungbean",
    "blackgram","lentil","pomegranate","banana","mango","grapes","watermelon",
    "muskmelon","apple","orange","papaya","coconut","cotton","jute","coffee",
]

# (N_mean, P_mean, K_mean, temp_mean, hum_mean, ph_mean, rain_mean)
CROP_PROFILES = {
    "rice":        (80, 40, 40, 24, 80, 6.0, 200),
    "maize":       (75, 50, 35, 22, 65, 6.2, 90),
    "chickpea":    (40, 60, 80, 18, 16, 7.0, 80),
    "kidneybeans": (20, 65, 35, 20, 22, 5.8, 105),
    "pigeonpeas":  (20, 65, 35, 27, 50, 5.5, 100),
    "mothbeans":   (20, 40, 20, 28, 55, 7.0, 50),
    "mungbean":    (20, 40, 20, 28, 85, 6.5, 50),
    "blackgram":   (40, 60, 20, 25, 65, 7.0, 70),
    "lentil":      (20, 60, 20, 25, 65, 7.0, 70),
    "pomegranate": (20, 10, 15, 22, 90, 6.5, 110),
    "banana":      (100, 55, 50, 27, 80, 6.0, 100),
    "mango":       (20, 20, 30, 27, 50, 6.0, 95),
    "grapes":      (20, 125, 200, 23, 82, 6.0, 70),
    "watermelon":  (100, 10, 50, 27, 85, 6.0, 50),
    "muskmelon":   (100, 10, 50, 27, 85, 6.5, 25),
    "apple":       (20, 125, 200, 22, 92, 6.0, 110),
    "orange":      (20, 10, 10, 23, 92, 7.0, 110),
    "papaya":      (50, 50, 50, 33, 92, 6.5, 150),
    "coconut":     (20, 10, 30, 27, 95, 6.0, 175),
    "cotton":      (120, 40, 20, 24, 80, 7.0, 80),
    "jute":        (80, 40, 40, 25, 80, 6.5, 175),
    "coffee":      (100, 20, 30, 25, 60, 6.5, 160),
}

def generate_crop_dataset(n_samples=2200, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    per_crop = n_samples // len(CROPS)
    rows = []
    for crop in CROPS:
        nm = np.array(CROP_PROFILES[crop], dtype=float)
        # stds: moderate spread
        stds = np.array([15, 15, 15, 3, 10, 0.5, 25], dtype=float)
        for _ in range(per_crop):
            vals = rng.normal(nm, stds)
            vals[0] = np.clip(vals[0], 0, 140)   # N
            vals[1] = np.clip(vals[1], 5, 145)   # P
            vals[2] = np.clip(vals[2], 5, 205)   # K
            vals[3] = np.clip(vals[3], 8, 44)    # temp
            vals[4] = np.clip(vals[4], 14, 100)  # humidity
            vals[5] = np.clip(vals[5], 3.5, 10)  # ph
            vals[6] = np.clip(vals[6], 20, 300)  # rainfall
            rows.append([*vals, crop])
    df = pd.DataFrame(rows, columns=["N","P","K","temperature","humidity","ph","rainfall","label"])
    # shuffle
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df
