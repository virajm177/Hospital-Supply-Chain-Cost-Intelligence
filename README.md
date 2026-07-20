# Hospital Supply Chain Cost Intelligence Dashboard

An end-to-end procurement analytics project: a Python pipeline generates and analyzes ~8,600 hospital purchase orders (Jan 2024 – Jun 2026), and an interactive dashboard surfaces cost-savings opportunities, supplier risk, and spend concentration.

**Live demo:** open `dashboard.html` in any browser (or host it free on GitHub Pages).

## Business questions answered
1. **Where is money leaking?** 15.4% of spend bypasses negotiated contracts, paying an 8–15% premium → **~$311K identified savings opportunity**.
2. **Which suppliers are a risk?** Apex Medical Group's on-time delivery collapsed to ~73% (target: 90%) with the longest lead times → volume reallocation candidate.
3. **Where should negotiation effort go?** A Pareto analysis shows a small set of SKUs drives 80% of spend.

## Project structure
```
├── dashboard.html              # interactive dashboard (Chart.js, live filters)
├── generate_and_analyze.py     # data generation + KPI analysis (pandas/NumPy)
├── data/
│   ├── procurement_data.csv    # 8,595 purchase orders — import this into Power BI/Tableau
│   └── dashboard_data.json     # pre-aggregated data feeding the dashboard
└── README.md
```

## Skills demonstrated
- **Python (pandas, NumPy):** data modeling, groupby aggregations, KPI engineering
- **Analytics thinking:** contract-compliance analysis, supplier scorecards, Pareto/ABC analysis, YoY trend decomposition, seasonality
- **Data visualization:** KPI design, interactive filtering (department × period), executive "key findings" storytelling
- **Domain:** healthcare supply chain (builds directly on my Northwell Health supply chain analytics experience)

## Resume bullets (pick 2–3, adjust numbers to your final run)
- Built an end-to-end supply chain analytics dashboard (Python, pandas, Chart.js) analyzing 8,600+ hospital purchase orders across 7 departments and 5 suppliers, with interactive department/period filtering.
- Identified a **$311K annual savings opportunity** by quantifying off-contract "maverick" spend (15.4% of $19.5M total) paying an 8–15% price premium.
- Designed supplier scorecards tracking on-time delivery vs. a 90% SLA target, flagging a supplier whose OTD degraded to 73% for volume reallocation.
- Applied Pareto (80/20) analysis to concentrate contract-renegotiation effort on the top SKUs driving 80% of procurement spend.

> Tip: on your resume, describe the *insight and business impact* first, tools second. In interviews, walk through the "key findings" strip — it's the 30-second executive summary.

## Rebuild it in Power BI (recommended second version)
Recruiters for BA/DA roles often filter for Power BI specifically. Import `data/procurement_data.csv` and recreate:
1. **Measures (DAX):**
   - `Total Spend = SUM(procurement[total_cost])`
   - `Off-Contract Spend = CALCULATE([Total Spend], procurement[on_contract] = FALSE())`
   - `Maverick % = DIVIDE([Off-Contract Spend], [Total Spend])`
   - `Savings Opportunity = [Off-Contract Spend] * (1 - 1/1.115)`
   - `OTD % = DIVIDE(CALCULATE(COUNTROWS(procurement), procurement[on_time] = TRUE()), COUNTROWS(procurement))`
   - `Spend YoY % = DIVIDE([Total Spend] - CALCULATE([Total Spend], SAMEPERIODLASTYEAR('Date'[Date])), CALCULATE([Total Spend], SAMEPERIODLASTYEAR('Date'[Date])))`
2. **Date table** via `CALENDARAUTO()` marked as date table, related to `order_date`.
3. **Visuals:** KPI cards, line chart (monthly spend), stacked bar (category × on_contract), matrix supplier scorecard with conditional formatting on OTD, Pareto (combo bar + cumulative line measure).
4. **Slicers:** department, year, supplier.

Publish to Power BI Service and link it alongside the GitHub repo.

## How to publish
1. Create a GitHub repo (e.g. `hospital-supply-chain-analytics`), push all files.
2. Settings → Pages → deploy from `main` → your dashboard is live at `https://<username>.github.io/hospital-supply-chain-analytics/dashboard.html`.
3. Add the link to your resume header and LinkedIn Featured section.

---
*Data is synthetic, generated with seeded randomness to mirror real procurement patterns (flu-season demand spikes, price inflation, supplier reliability drift). No proprietary data is used.*
