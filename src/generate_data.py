from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "data" / "accounts_synthetic.csv"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def main(n: int = 800, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)

    account_id = [f"ACC-{i:04d}" for i in range(1, n + 1)]
    plan = rng.choice(["basic", "pro", "enterprise"], size=n, p=[0.4, 0.4, 0.2])

    usage_90d = rng.normal(1000, 350, size=n).clip(80, None)
    usage_delta_pct = rng.normal(0, 0.22, size=n).clip(-0.8, 0.8)
    usage_30d = (usage_90d * (1 + usage_delta_pct)).clip(30, None)

    critical_tickets_30d = rng.poisson(lam=1.1, size=n)
    nps = rng.normal(35, 30, size=n).clip(-100, 100)

    on_time_payment_ratio = rng.normal(0.9, 0.12, size=n).clip(0, 1)
    late_payments_6m = rng.poisson(1.0, size=n)
    arr_usd = rng.normal(24000, 15000, size=n).clip(1500, None)

    plan_weight = np.select(
        [plan == "basic", plan == "pro", plan == "enterprise"],
        [0.15, 0.0, -0.2],
    )

    churn_logit = (
        1.7 * (-usage_delta_pct)
        + 0.35 * critical_tickets_30d
        - 0.02 * nps
        + 1.2 * (1 - on_time_payment_ratio)
        + 0.18 * late_payments_6m
        + plan_weight
        - 0.6
    )

    churn_prob = sigmoid(churn_logit)
    churned_60d = rng.binomial(1, churn_prob)

    # Expansion proxy: lower churn + strong NPS + healthy usage + non-enterprise plan
    expansion_logit = (
        -1.1 * churn_prob
        + 0.015 * (nps)
        + 1.2 * np.maximum(usage_delta_pct, -0.2)
        + np.where(plan == "enterprise", -0.35, 0.0)
        + 0.25
    )
    expansion_prob = sigmoid(expansion_logit)

    df = pd.DataFrame(
        {
            "account_id": account_id,
            "plan": plan,
            "usage_90d": usage_90d.round(2),
            "usage_30d": usage_30d.round(2),
            "usage_delta_pct": usage_delta_pct.round(4),
            "critical_tickets_30d": critical_tickets_30d,
            "nps": nps.round(1),
            "on_time_payment_ratio": on_time_payment_ratio.round(3),
            "late_payments_6m": late_payments_6m,
            "arr_usd": arr_usd.round(2),
            "churned_60d": churned_60d,
            "expansion_prob_proxy": expansion_prob.round(4),
        }
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"✅ Synthetic dataset saved to: {OUT}")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
