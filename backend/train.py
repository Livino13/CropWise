"""Train and save model artifact.

Usage:
  python train.py                        # train on data/crop_data.csv
  python train.py --csv path/to.csv      # custom dataset
  python train.py --out other.joblib     # custom artifact path
  python train.py --include-feedback     # append DB feedback rows (actual_crop) as samples
"""
from pathlib import Path
import argparse
import pandas as pd
from app.ml.rf_model import train_pipeline

DEFAULT_CSV = str(Path(__file__).parent / "data" / "crop_data.csv")
DEFAULT_OUT = str(Path(__file__).parent / "app" / "ml" / "artifacts" / "model.joblib")


def _feedback_frame() -> pd.DataFrame:
    from app.services.retrain import _feedback_rows
    return _feedback_rows()


def main():
    parser = argparse.ArgumentParser(description="Train the CropWise FCM+PSO+RF model")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="training CSV path")
    parser.add_argument("--out", default=DEFAULT_OUT, help="artifact output path")
    parser.add_argument("--include-feedback", action="store_true",
                        help="append DB rows with actual_crop as extra training samples")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    source = "train.py"
    if args.include_feedback:
        df_fb = _feedback_frame()
        if len(df_fb):
            df = pd.concat([df, df_fb.drop(columns=["yield_t_ha"], errors="ignore")], ignore_index=True)
            print(f"Appended {len(df_fb)} feedback rows -> {len(df)} total")
            source = f"train.py --include-feedback (+{len(df_fb)})"
        else:
            print("No feedback rows found in DB — training on CSV only")

    artifact = train_pipeline(df=df, save_path=args.out)
    print(f"Model saved to {args.out}")
    print(f"Holdout accuracy:   {artifact['accuracy']*100:.2f}%")
    cv = artifact["cv_scores"]
    print(f"5-fold CV accuracy: {cv['5fold_mean']*100:.2f}% (+/- {cv['5fold_std']*100:.2f})")
    print(f"Selected model:     {artifact['model_name']}")
    for name, info in artifact["model_comparison"].items():
        mark = " <- selected" if info.get("selected") else ""
        print(f"  {name:24s} cv3={info['cv3_mean']*100:.2f}%{mark}")
    print(f"PSO best CV acc:    {artifact['pso_cv_accuracy']*100:.2f}%")
    print(f"Xie-Beni (diag):    {artifact['xie_beni']:.4f}")
    print(f"Weights:            {artifact['weights'].round(2)}")

    # versioned copy + manifest (skip for custom --out paths)
    if Path(args.out).resolve() == Path(DEFAULT_OUT).resolve():
        try:
            from app.services.retrain import record_training_run
            version = record_training_run(artifact, source=source)
            print(f"Recorded as model v{version} in manifest")
        except Exception as e:
            print(f"(manifest update skipped: {e})")


if __name__ == "__main__":
    main()
