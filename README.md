# Iran War Portfolio Tracker

[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-GitHub_Pages-blue?logo=github)](https://gohjhb92.github.io/g1/)
[![Auto-Update](https://img.shields.io/badge/Auto--Update-Mon--Fri_21:00_UTC-green?logo=github-actions)](https://github.com/gohjhb92/g1/actions/workflows/update.yml)

> **Milkshakes Pod — Iran War Trade**
> Tracking assets that benefit from the US-Israel vs Iran conflict, Strait of Hormuz disruption, oil shock, and defense spending surge.

---

## Thesis

| Parameter | Detail |
|-----------|--------|
| War start | 2026-02-28 |
| Fragile ceasefire | 2026-04-08 |
| Thesis tracking start | **2026-04-13** |
| Core driver | Strait of Hormuz = ~20% of global oil transit; closure triggers oil shock, LNG scramble, and re-armament cycle |
| Key risks | Full ceasefire / normalization collapses energy premium; BWET unwinds sharply on re-routing |

The trade has two regimes:
- **Escalation on** → long energy (USO/XLE/XOM/CVX), tankers (BWET), LNG (LNG), defense (LMT/NOC/RTX/ITA/PLTR/KTOS), gold (GLD), commodities (HGER/REMX)
- **De-escalation / ceasefire** → trim longs, rotate into SCO (2× inverse crude) and TAIL (tail-risk hedge)

---

## Asset Rationale

| Ticker | Name | Category | Role in Thesis |
|--------|------|----------|----------------|
| **USO** | US Oil Fund | Energy | Direct crude oil exposure; spikes on Hormuz closure |
| **XLE** | Energy Select SPDR | Energy | Broad US energy equity basket |
| **XOM** | ExxonMobil | Energy | Integrated major; benefits from sustained high oil |
| **CVX** | Chevron | Energy | Integrated major; LNG & refining leverage |
| **BWET** | Breakwave Tanker Shipping ETF | Tanker | Best-performing non-leveraged ETF YTD (~200%); tanker rates explode on rerouting |
| **LNG** | Cheniere Energy | LNG | Qatar energy halt → Europe scrambles for US LNG; direct revenue beneficiary |
| **LMT** | Lockheed Martin | Defense | Hit ATH at war start; F-35, HIMARS, missile defense cycles |
| **NOC** | Northrop Grumman | Defense | B-21, GBSD; benefits from Pentagon budget surge |
| **RTX** | RTX Corp | Defense | Patriot missile systems, Raytheon munitions restocking |
| **ITA** | iShares Aerospace & Defense ETF | Defense | Diversified defense basket |
| **PLTR** | Palantir | Defense | AI/defense intelligence contracts; war-time data demand |
| **KTOS** | Kratos Defense | Defense | Drone and unmanned systems surge |
| **GLD** | SPDR Gold Shares | Commodities | Safe-haven surge; crossed $5,400/oz |
| **HGER** | Harbor Commodity All-Weather | Commodities | ~26% YTD; broad commodity exposure |
| **REMX** | VanEck Rare Earth & Strategic Metals | Commodities | Supply chain diversification pressure on rare earths |
| **SCO** | ProShares 2× Short Crude Oil | Hedge | De-escalation / ceasefire bet; inverse crude exposure |
| **TAIL** | Cambria Tail Risk ETF | Hedge | Tail-risk protection; benefits from volatility spikes |
| **SPY** | SPDR S&P 500 ETF | Benchmark | Down ~9% since war start — context for relative performance |
| **QQQ** | Invesco Nasdaq-100 ETF | Benchmark | Down ~20% YTD — tech bear market context |

---

## Dashboard

The live dashboard is hosted on **GitHub Pages** from the `/docs` folder:

[https://gohjhb92.github.io/g1/](https://gohjhb92.github.io/g1/)

Features:
- **War status banner** — manually toggle ESCALATING / CEASEFIRE / DE-ESCALATING (persists in browser)
- **Performance bar chart** — % change since thesis start date, sorted and color-coded by category
- **Cumulative line chart** — daily performance trajectory for each asset
- **Summary table** — price, today %, and since-start % for all tickers
- Mobile-friendly responsive layout

---

## Folder Structure

```
/
├── fetch_prices.py          # Fetch & update daily closes via yfinance
├── tracker.csv              # Master price history (also copied to docs/)
├── requirements.txt
├── README.md
├── .github/
│   └── workflows/
│       └── update.yml       # Auto-runs Mon–Fri at 21:00 UTC
└── docs/
    ├── index.html           # Chart.js dashboard (GitHub Pages)
    └── tracker.csv          # Copy of data served to the dashboard
```

---

## Setup

### Local

```bash
git clone https://github.com/gohjhb92/g1.git
cd g1
pip install -r requirements.txt
python fetch_prices.py           # populate tracker.csv from thesis start date
```

### GitHub Actions auto-update

The workflow at `.github/workflows/update.yml` runs automatically Monday–Friday at **21:00 UTC** (5 pm ET, after US market close). It:

1. Installs dependencies
2. Runs `fetch_prices.py` (incremental fetch)
3. Commits and pushes updated `tracker.csv` if new data is available

Enable GitHub Pages in your repo settings → **Pages** → Source: **Deploy from a branch** → Branch: `main` → Folder: `/docs`.

### Manual trigger

Go to **Actions → Update Portfolio Tracker → Run workflow** to trigger outside of schedule.

---

## Disclaimer

This repository and dashboard are for **informational and educational purposes only**. Nothing here constitutes financial advice, investment recommendations, or solicitation to buy or sell any security. Past performance is not indicative of future results. All investments carry risk, including possible loss of principal. Data is sourced via Yahoo Finance / yfinance and may be delayed, incorrect, or unavailable. The war status indicator reflects a manual assessment only and has no predictive value. Always consult a licensed financial advisor before making investment decisions.
