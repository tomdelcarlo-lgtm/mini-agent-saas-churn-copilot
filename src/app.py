from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parents[1]
PRED_PATH = BASE / "data" / "predictions.csv"

st.set_page_config(page_title="Churn & Expansion Copilot", layout="wide")
st.title("📉➡️📈 Churn & Expansion Copilot")
st.caption("MVP for CSM/AM teams: churn risk + next best action per account")

if not PRED_PATH.exists():
    st.warning("predictions.csv not found. Run first: generate_data.py, train.py, predict_and_plan.py")
    st.stop()

df = pd.read_csv(PRED_PATH)

c1, c2, c3 = st.columns(3)
c1.metric("Accounts", len(df))
c2.metric("High churn risk", int((df["churn_risk_label"] == "high").sum()))
c3.metric("Expansion opp > 0.65", int((df["expansion_opportunity_score"] > 0.65).sum()))

st.subheader("Filters")
plan_filter = st.multiselect("Plan", sorted(df["plan"].unique().tolist()), default=sorted(df["plan"].unique().tolist()))
risk_filter = st.multiselect("Risk label", ["low", "medium", "high"], default=["medium", "high"])

df_view = df[(df["plan"].isin(plan_filter)) & (df["churn_risk_label"].isin(risk_filter))].copy()

df_view = df_view.sort_values(by=["churn_risk_score", "arr_usd"], ascending=[False, False])

st.subheader("Prioritized account queue")
st.dataframe(
    df_view[
        [
            "account_id",
            "plan",
            "arr_usd",
            "churn_risk_score",
            "churn_risk_label",
            "expansion_opportunity_score",
            "top_drivers",
            "next_best_action",
        ]
    ],
    width="stretch",
)

st.subheader("Generate weekly account action plan")
if st.button("Generate weekly account action plan"):
    top = df.sort_values(by=["churn_risk_score", "arr_usd"], ascending=[False, False]).head(15)
    lines = ["# Weekly Account Action Plan\n"]
    for _, r in top.iterrows():
        lines.append(
            f"- **{r['account_id']}** | risk={r['churn_risk_score']:.2f} ({r['churn_risk_label']}) | "
            f"expansion={r['expansion_opportunity_score']:.2f}\\n"
            f"  - Drivers: {r['top_drivers']}\\n"
            f"  - Action: {r['next_best_action']}"
        )

    report = "\n".join(lines)
    st.markdown(report)
    st.download_button(
        label="Download plan (.md)",
        data=report,
        file_name="weekly_account_action_plan.md",
        mime="text/markdown",
    )
