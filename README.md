Hospital Supply Chain Cost Intelligence Dashboard
An end-to-end procurement analytics project: a Python pipeline generates and analyzes ~8,600 hospital purchase orders (Jan 2024 – Jun 2026), and an interactive dashboard surfaces cost-savings opportunities, supplier risk, and spend concentration.
Live dashboard →
Business questions answered
Where is money leaking? 15.4% of spend bypasses negotiated contracts, paying an 8–15% premium → ~$311K identified savings opportunity.
Which suppliers are a risk? One supplier's on-time delivery collapsed to ~73% (target: 90%) with the longest lead times → volume reallocation candidate.
Where should negotiation effort go? A Pareto analysis shows a small set of SKUs drives 80% of spend.
Project structure
```
├── dashboard.html              # interactive dashboard (Chart.js, live filters)
├── generate_and_analyze.py     # data generation + KPI analysis (pandas/NumPy)
├── procurement_data.csv        # 8,595 purchase orders (also used for the Power BI version)
└── README.md
```
Methodology
Data: synthetic transactional data generated with seeded randomness to mirror real procurement patterns — flu-season demand spikes (Oct–Feb), ~4.5% annual price inflation, supplier reliability drift, and a 14% off-contract purchase rate carrying an 8–15% price premium. No proprietary data is used.
Analysis (Python / pandas): contract-compliance quantification, supplier scorecards (on-time delivery vs. 90% SLA, lead times, spend share), Pareto/ABC spend concentration, and YoY trend decomposition.
Dashboard: single-file HTML with Chart.js; all KPIs recompute client-side with live department × period filtering.
Tech stack
Python (pandas, NumPy) · Chart.js · HTML/CSS/JavaScript · Power BI (companion report in progress)
Author
Viraj Paresh Mehta — MS Business Analytics, Hofstra University
Background in healthcare supply chain analytics 
