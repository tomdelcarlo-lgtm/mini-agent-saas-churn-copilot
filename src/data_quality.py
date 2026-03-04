from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE / "data" / "accounts_synthetic.csv"
DEFAULT_OUT = BASE / "data" / "data_quality_report.md"

REQUIRED_COLUMNS = [
    "account_id",
    "plan",
    "usage_90d",
    "usage_30d",
    "usage_delta_pct",
    "critical_tickets_30d",
    "nps",
    "on_time_payment_ratio",
    "late_payments_6m",
    "arr_usd",
]

ALLOWED_PLAN = {"basic", "pro", "enterprise"}
RANGES = {
    "usage_90d": (0, None),
    "usage_30d": (0, None),
    "usage_delta_pct": (-1, 1),
    "critical_tickets_30d": (0, None),
    "nps": (-100, 100),
    "on_time_payment_ratio": (0, 1),
    "late_payments_6m": (0, None),
    "arr_usd": (0, None),
}


def check_ranges(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    for col, (lo, hi) in RANGES.items():
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        bad = pd.Series(False, index=df.index)
        if lo is not None:
            bad |= s < lo
        if hi is not None:
            bad |= s > hi
        n_bad = int(bad.sum())
        if n_bad > 0:
            issues.append(f"- {col}: {n_bad} value(s) outside expected range [{lo}, {hi}]")
    return issues


def main(input_path: Path, out_path: Path) -> None:
    df = pd.read_csv(input_path)
    total = len(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    duplicate_ids = int(df["account_id"].duplicated().sum()) if "account_id" in df.columns else None

    null_lines = []
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            n_null = int(df[col].isna().sum())
            pct = (n_null / total * 100) if total else 0
            null_lines.append(f"- {col}: {n_null} null(s) ({pct:.2f}%)")

    plan_issues = []
    if "plan" in df.columns:
        invalid_plan = sorted(set(df["plan"].dropna().astype(str).unique()) - ALLOWED_PLAN)
        if invalid_plan:
            plan_issues.append(f"- plan: invalid categories found {invalid_plan}")

    range_issues = check_ranges(df)

    status = "PASS" if not missing_cols and not plan_issues and not range_issues else "WARN"

    lines = [
        "# Data Quality Report (SaaS Churn Copilot)",
        "",
        f"- Input file: `{input_path}`",
        f"- Rows: {total}",
        f"- Overall status: **{status}**",
        "",
        "## Schema checks",
        f"- Missing required columns: {missing_cols if missing_cols else 'None'}",
        f"- Duplicate account_id: {duplicate_ids if duplicate_ids is not None else 'N/A'}",
        "",
        "## Null checks",
        *null_lines,
        "",
        "## Category checks",
        *(plan_issues if plan_issues else ["- plan: OK"]),
        "",
        "## Range checks",
        *(range_issues if range_issues else ["- All numeric ranges look valid"]),
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Data quality report saved to: {out_path}")
    print(f"Status: {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SaaS input data quality report")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to input CSV")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Path to output markdown report")
    args = parser.parse_args()
    main(args.input, args.out)
