"""Build step for Vercel.

Trains the model artifact only when it is missing. Local and CLI deploys ship
the pre-trained ``model.joblib`` (see ``.vercelignore``), while a fresh Git
clone has no artifact because ``*.joblib`` is git-ignored.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "app" / "ml" / "artifacts" / "model.joblib"

if ARTIFACT.exists():
    print(f"Using existing model artifact: {ARTIFACT} ({ARTIFACT.stat().st_size / 1e6:.1f} MB)")
else:
    print("Model artifact missing - training from data/crop_data.csv ...")
    subprocess.run([sys.executable, "train.py"], cwd=ROOT, check=True)
    print(f"Model saved to {ARTIFACT}")
