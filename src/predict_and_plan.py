from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "accounts_synthetic.csv"
MODEL_PATH = BASE / "data" / "churn_model.joblib"
OUT_PATH = BASE / "data" / "predictions.csv"

FEATURE_COLS = [
    "usage_90d",
    "usage_30d",
    "usage_delta_pct",
    "critical_tickets_30d",
    "nps",
    "on_time_payment_ratio",
    "late_payments_6m",
    "arr_usd",
    "plan",
]


def load_and_validate(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def churn_label(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def expansion_score(row: pd.Series) -> float:
    score = (
        0.45 * (1 - row["churn_risk_score"])
        + 0.25 * max(row["usage_delta_pct"], -0.3)
        + 0.2 * (max(min((row["nps"] + 100) / 200, 1), 0))
        + 0.1 * row["on_time_payment_ratio"]
    )
    if row["plan"] == "enterprise":
        score -= 0.08
    return float(np.clip(score, 0, 1))


def top_drivers(row: pd.Series) -> str:
    drivers = []
    if row["usage_delta_pct"] < -0.2:
        drivers.append("usage decline")
    if row["critical_tickets_30d"] >= 3:
        drivers.append("critical tickets")
    if row["nps"] < 0:
        drivers.append("low NPS")
    if row["late_payments_6m"] >= 2 or row["on_time_payment_ratio"] < 0.75:
        drivers.append("payment friction")
    if not drivers:
        drivers.append("stable health signals")
    return ", ".join(drivers[:3])


def next_best_action(row: pd.Series) -> str:
    if row["churn_risk_score"] >= 0.7:
        return "Urgent save play: exec sponsor call + product fix plan in 7 days"
    if row["churn_risk_score"] >= 0.4:
        return "CSM check-in: adoption workshop + ticket resolution follow-up"
    if row["expansion_opportunity_score"] >= 0.65:
        return "Upsell motion: propose seat expansion/use-case deep dive"
    return "Monitor monthly and keep regular success cadence"


def main(input_path: Path) -> None:
    df = load_and_validate(input_path)
    model = joblib.load(MODEL_PATH)

    df["churn_risk_score"] = model.predict_proba(df[FEATURE_COLS])[:, 1]
    df["churn_risk_label"] = df["churn_risk_score"].apply(churn_label)
    df["expansion_opportunity_score"] = df.apply(expansion_score, axis=1)
    df["top_drivers"] = df.apply(top_drivers, axis=1)
    df["next_best_action"] = df.apply(next_best_action, axis=1)

    weekly = df.sort_values(by=["churn_risk_score", "arr_usd"], ascending=[False, False]).copy()

    weekly.to_csv(OUT_PATH, index=False)
    print(f"✅ Predictions + actions saved to: {OUT_PATH}")
    print(
        weekly[
            [
                "account_id",
                "churn_risk_score",
                "churn_risk_label",
                "expansion_opportunity_score",
                "top_drivers",
                "next_best_action",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate predictions/action plan from input CSV")
    parser.add_argument("--input", type=Path, default=DATA_PATH, help="Path to input CSV")
    args = parser.parse_args()
    main(args.input)
