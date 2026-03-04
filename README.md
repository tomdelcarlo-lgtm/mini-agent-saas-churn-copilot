# Churn & Expansion Copilot (Mini-Agent #1)

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Demo-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-MVP-blue)

An MVP for B2B SaaS teams to prioritize accounts at churn risk and identify expansion opportunities.

## Value proposition

This agent **does not predict for prediction’s sake**:
- estimates `churn_risk_score` per account,
- suggests `next_best_action` for CSM/AM teams,
- explains key drivers (e.g., usage decline + critical tickets).

## Expected input

Per-account signals (example):
- product usage (30d vs 90d)
- critical support tickets
- NPS
- plan tier
- payment history

## Output

- `churn_risk_score` (0-1)
- `churn_risk_label` (low/medium/high)
- `expansion_opportunity_score` (0-1)
- `next_best_action`
- `top_drivers`

## Project structure

```bash
mini-agent-saas-churn-copilot/
├─ data/
│  ├─ accounts_synthetic.csv
│  └─ predictions.csv
├─ notebooks/
│  └─ mvp_walkthrough.ipynb   # optional (you can build in Colab)
├─ src/
│  ├─ generate_data.py
│  ├─ train.py
│  ├─ predict_and_plan.py
│  └─ app.py
├─ requirements.txt
└─ README.md
```

## Local quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/generate_data.py
python src/train.py
python src/predict_and_plan.py
streamlit run src/app.py
```

## Bring your own data (BYOD)

1. Copy the template:
   - `cp data/input_template.csv data/accounts.csv`
2. Fill `data/accounts.csv` with your own records, keeping the same column names.
3. (Recommended) Run a data quality check first:
   - `python src/data_quality.py --input data/accounts.csv`
4. Train and predict with your file:
   - `python src/train.py --input data/accounts.csv`
   - `python src/predict_and_plan.py --input data/accounts.csv`

## Colab quickstart

1. Upload this folder to Drive (or clone it).
2. Run in order:
   - `python src/generate_data.py`
   - `python src/train.py`
   - `python src/predict_and_plan.py`
3. If you want the UI, run Streamlit locally on your machine.

## 60-second demo script

- 0–10s: “Built for B2B SaaS to improve retention and expansion.”
- 10–25s: “Inputs: usage trend, critical tickets, NPS, plan, payments.”
- 25–40s: “Model outputs churn score + recommended action per account.”
- 40–55s: “Business impact: focus CSM time on highest-risk/highest-upside accounts.”
- 55–60s: “Can adapt to your stack in 1–2 weeks.”

## Next improvements (post-MVP)

- SHAP-based explainability
- probability calibration
- segmentation by industry / ARR band
- integrations with HubSpot / Salesforce / Zendesk
