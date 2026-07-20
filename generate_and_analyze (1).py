"""
Healthcare Supply Chain Analytics — Data Generation & KPI Analysis
------------------------------------------------------------------
Portfolio project by Viraj Paresh Mehta

Generates a realistic hospital procurement dataset (Jan 2024 - Jun 2026),
then computes the KPIs used in the dashboard:
  - Total / monthly spend, YoY growth
  - Off-contract ("maverick") spend and the savings opportunity it creates
  - Supplier scorecards: on-time delivery %, avg lead time, spend share
  - Pareto (80/20) concentration of spend by item
Outputs:
  data/procurement_data.csv    - raw transactional data (~8,700 POs)
  data/dashboard_data.json     - pre-aggregated data consumed by dashboard.html
"""

import json
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------------- reference data
CATALOG = {
    # category: [(item, base_unit_cost, avg_qty), ...]
    "PPE & Safety": [
        ("Nitrile Exam Gloves (box 200)", 11.50, 220),
        ("N95 Respirators (case 210)", 142.00, 18),
        ("Isolation Gowns (case 100)", 96.00, 26),
        ("Face Shields (case 96)", 84.00, 9),
    ],
    "Surgical Supplies": [
        ("Suture Kits (box 36)", 188.00, 14),
        ("Surgical Drapes (case 60)", 132.00, 12),
        ("Laparoscopic Trocars (box 6)", 410.00, 5),
        ("Sterile Gauze (case 600)", 58.00, 30),
    ],
    "Pharmaceuticals": [
        ("Saline IV Bags 1L (case 12)", 74.00, 48),
        ("Heparin Vials (box 25)", 168.00, 16),
        ("Propofol Vials (box 10)", 210.00, 12),
        ("Epinephrine Auto-Inj (box 12)", 640.00, 4),
    ],
    "Lab & Diagnostics": [
        ("Blood Collection Tubes (case 1000)", 118.00, 15),
        ("Rapid Flu Test Kits (box 25)", 265.00, 10),
        ("Reagent Pack - Chemistry", 890.00, 3),
        ("Specimen Containers (case 500)", 64.00, 12),
    ],
    "Medical Equipment": [
        ("Infusion Pump Sets (case 24)", 340.00, 6),
        ("Pulse Oximeter Sensors (box 24)", 295.00, 5),
        ("ECG Electrodes (case 600)", 87.00, 18),
        ("Ventilator Circuits (case 20)", 260.00, 4),
    ],
}

SUPPLIERS = {
    "MedLine Direct":      {"otd": 0.96, "price_f": 1.00, "lead": 6},
    "Cardinal Supply Co":  {"otd": 0.93, "price_f": 0.98, "lead": 7},
    "OmniHealth Partners": {"otd": 0.88, "price_f": 0.95, "lead": 9},
    "Apex Medical Group":  {"otd": 0.78, "price_f": 0.93, "lead": 11},  # cheap but unreliable
    "Regional MedSupply":  {"otd": 0.91, "price_f": 1.06, "lead": 4},   # fast but pricey
}

DEPARTMENTS = ["Emergency", "Surgery", "ICU", "Oncology", "Cardiology", "Laboratory", "General Medicine"]
DEPT_W = [0.20, 0.19, 0.16, 0.11, 0.12, 0.12, 0.10]

MONTHS = pd.period_range("2024-01", "2026-06", freq="M")

# ---------------------------------------------------------------- generate POs
rows, po_num = [], 10000
for m in MONTHS:
    # seasonality: flu season lifts PPE/pharma volume Oct-Feb
    flu = 1.28 if m.month in (10, 11, 12, 1, 2) else 1.0
    # mild inflation over time
    infl = 1.0 + 0.045 * ((m.year - 2024) + (m.month - 1) / 12)
    n_pos = int(rng.normal(290, 22))
    for _ in range(n_pos):
        cat = rng.choice(list(CATALOG), p=[0.24, 0.20, 0.22, 0.17, 0.17])
        item, base_cost, avg_qty = CATALOG[cat][rng.integers(len(CATALOG[cat]))]
        sup_name = rng.choice(list(SUPPLIERS))
        sup = SUPPLIERS[sup_name]

        seasonal = flu if cat in ("PPE & Safety", "Pharmaceuticals", "Lab & Diagnostics") else 1.0
        qty = max(1, int(rng.normal(avg_qty * seasonal, avg_qty * 0.30)))

        # ~14% of orders bypass negotiated contracts -> pay an 8-15% premium
        on_contract = rng.random() > 0.14
        maverick_prem = 1.0 if on_contract else rng.uniform(1.08, 1.15)
        unit_cost = round(base_cost * sup["price_f"] * infl * maverick_prem * rng.normal(1, 0.03), 2)

        # Apex's reliability deteriorates through 2025-26
        otd_p = sup["otd"]
        if sup_name == "Apex Medical Group" and m >= pd.Period("2025-01"):
            otd_p -= 0.10
        lead = max(1, int(rng.normal(sup["lead"], 2)))
        promised = sup["lead"] + 2
        on_time = (lead <= promised) and (rng.random() < otd_p + 0.05)

        day = int(rng.integers(1, 28))
        rows.append({
            "po_id": f"PO-{po_num}",
            "order_date": f"{m.year}-{m.month:02d}-{day:02d}",
            "department": rng.choice(DEPARTMENTS, p=DEPT_W),
            "category": cat,
            "item": item,
            "supplier": sup_name,
            "unit_cost": unit_cost,
            "quantity": qty,
            "total_cost": round(unit_cost * qty, 2),
            "lead_time_days": lead,
            "promised_days": promised,
            "on_time": on_time,
            "on_contract": on_contract,
        })
        po_num += 1

df = pd.DataFrame(rows)
df.to_csv("data/procurement_data.csv", index=False)
print(f"Generated {len(df):,} purchase orders | total spend ${df.total_cost.sum():,.0f}")

# ---------------------------------------------------------------- KPI analysis
df["month"] = df["order_date"].str[:7]
df["year"] = df["order_date"].str[:4]

spend_24 = df.loc[(df.month >= "2024-01") & (df.month <= "2024-12"), "total_cost"].sum()
spend_25 = df.loc[(df.month >= "2025-01") & (df.month <= "2025-12"), "total_cost"].sum()

# savings opportunity = premium paid on off-contract spend
mav = df[~df.on_contract]
mav_spend = mav.total_cost.sum()
est_savings = mav_spend * (1 - 1 / 1.115)  # midpoint of the 8-15% premium

# supplier scorecard
sc = (df.groupby("supplier")
        .agg(spend=("total_cost", "sum"),
             orders=("po_id", "count"),
             otd=("on_time", "mean"),
             avg_lead=("lead_time_days", "mean"))
        .round({"spend": 0, "otd": 3, "avg_lead": 1})
        .sort_values("spend", ascending=False)
        .reset_index())

# Pareto by item
pareto = (df.groupby("item")["total_cost"].sum()
            .sort_values(ascending=False).reset_index())
pareto["cum_pct"] = (pareto.total_cost.cumsum() / pareto.total_cost.sum() * 100).round(1)

payload = {
    "kpis": {
        "total_spend": round(df.total_cost.sum()),
        "spend_2024": round(spend_24),
        "spend_2025": round(spend_25),
        "yoy_pct": round((spend_25 / spend_24 - 1) * 100, 1),
        "maverick_spend": round(mav_spend),
        "maverick_pct": round(mav_spend / df.total_cost.sum() * 100, 1),
        "est_savings": round(est_savings),
        "otd_overall": round(df.on_time.mean() * 100, 1),
        "avg_lead": round(df.lead_time_days.mean(), 1),
        "total_pos": len(df),
    },
    "monthly": (df.groupby(["month"])
                  .agg(spend=("total_cost", "sum"), otd=("on_time", "mean"))
                  .round({"spend": 0, "otd": 3}).reset_index()
                  .to_dict("records")),
    "monthly_dept": (df.groupby(["month", "department"])["total_cost"].sum()
                       .round(0).reset_index().to_dict("records")),
    "category": (df.groupby(["category", "on_contract"])["total_cost"].sum()
                   .round(0).reset_index().to_dict("records")),
    "dept": (df.groupby("department")["total_cost"].sum()
               .round(0).sort_values(ascending=False).reset_index().to_dict("records")),
    "suppliers": sc.to_dict("records"),
    "supplier_otd_trend": (df.groupby(["month", "supplier"])["on_time"].mean()
                             .round(3).reset_index().to_dict("records")),
    "pareto": pareto.head(12).round(0).to_dict("records"),
}
with open("data/dashboard_data.json", "w") as f:
    json.dump(payload, f)

print(f"YoY spend growth 2024->2025: {payload['kpis']['yoy_pct']}%")
print(f"Off-contract spend: ${mav_spend:,.0f} ({payload['kpis']['maverick_pct']}%) "
      f"-> est. savings opportunity ${est_savings:,.0f}")
print(f"On-time delivery: {payload['kpis']['otd_overall']}% | Avg lead {payload['kpis']['avg_lead']} days")
print(sc.to_string(index=False))
