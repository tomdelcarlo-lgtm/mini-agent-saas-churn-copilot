from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "accounts_synthetic.csv"
MODEL_PATH = BASE / "data" / "churn_model.joblib"

FEATURES_NUM = [
    "usage_90d",
    "usage_30d",
    "usage_delta_pct",
    "critical_tickets_30d",
    "nps",
    "on_time_payment_ratio",
    "late_payments_6m",
    "arr_usd",
]
FEATURES_CAT = ["plan"]
TARGET = "churned_60d"
REQUIRED_COLUMNS = FEATURES_NUM + FEATURES_CAT + [TARGET]


def load_and_validate(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def main(input_path: Path) -> None:
    df = load_and_validate(input_path)

    X = df[FEATURES_NUM + FEATURES_CAT]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("clf", LogisticRegression(max_iter=1200, class_weight="balanced", solver="liblinear")),
        ]
    )

    model.fit(X_train, y_train)

    p = model.predict_proba(X_test)[:, 1]
    y_hat = (p >= 0.5).astype(int)

    print("AUC:", round(roc_auc_score(y_test, p), 4))
    print(classification_report(y_test, y_hat))

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train churn model with your own CSV data")
    parser.add_argument("--input", type=Path, default=DATA_PATH, help="Path to input CSV")
    args = parser.parse_args()
    main(args.input)
