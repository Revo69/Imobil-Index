# 🏠 Imobil.Index

**Daily market analytics for Moldova's residential real estate** — sale prices,
monthly rentals, daily rentals, and indicative gross yield in one dashboard and
public aggregated API.

[![Live Demo](https://img.shields.io/badge/demo-live-2563eb?style=flat-square)](https://imobil-index.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![Automated](https://img.shields.io/badge/keep--alive-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

**[→ Open the live dashboard](https://imobil-index.streamlit.app)**

---

## What it does

Imobil.Index turns raw property listings into decision-ready market intelligence
for buyers, sellers, and investors. The dashboard reads safe, pre-aggregated
`api_*` tables from Supabase (Postgres) and surfaces them in four views:

| Tab | What you get |
|---|---|
| 🏷️ **For Sale** | City and sector pricing, room/area profiles, housing type, finish/condition, floor-position comparison, and 90-day trends |
| 📅 **Monthly Rent** | Rental price per m² by sector, top/bottom districts, indicative gross yield |
| 🌙 **Daily Rent** | Short-term rental pricing, occupancy-adjusted indicative gross yield, daily vs. monthly comparison |
| ✦ **Insights** | Rule-based signals, weekly price movement, regional value comparison, break-even context, yield notes, investment shortlist, and daily-vs-monthly return comparison |

Data is refreshed daily through an upstream ETL pipeline (**bronze → silver →
gold**: raw ingestion → cleaning/normalization → aggregated metrics). Gold stays
private; the dashboard and public users read only the aggregated API layer.

---

## Highlights

- **Listings-weighted pricing** — average price per m² is weighted by listing count per sector, not a naive mean, avoiding skew from thin markets
- **Lean historical queries** — the 90-day trend chart pulls only the columns and date range it needs (`date, city, sector, avg_per_m2_eur`), server-side filtered and paginated, instead of loading full tables into memory
- **Buyer-relevant sale profiles** — city comparison, rooms and area bands, housing type, finish/condition, and floor position provide clearly caveated comparisons without exposing listings
- **Regional value comparison** — shows cities outside Chisinau with the largest listing-weighted price gap to the current Chisinau average
- **Investment shortlist** — compares visible markets by indicative monthly and daily gross yield, average sale price, and available sale/rent supply
- **Daily rent assumption** — re-scales the published 60% daily-rent model across Daily Rent and Insights, showing sector-level gross return, break-even occupancy, and the daily-versus-monthly difference
- **Public API by design** — the `api_*` tables contain aggregated metrics only, use RLS, and allow anonymous read access without public writes; see the [Public API v1 contract](docs/public_api_v1.md)
- **Hourly caching** (`st.cache_data(ttl=3600)`) to keep the app responsive without hammering the database
- **Clear data-connection state** — public users see a calm recovery message instead of a raw exception when the API is temporarily unavailable
- **Self-waking deployment** — Streamlit Community Cloud puts idle free-tier apps to sleep; a plain HTTP request only returns the static "asleep" shell, so a Playwright script actually drives a headless browser to click the wake button, scheduled via GitHub Actions 4× daily

---

## Tech stack

| Layer | Tools |
|---|---|
| Dashboard | Streamlit, Plotly Express |
| Data | Supabase (Postgres + REST API) |
| Automation | GitHub Actions, Playwright |
| Language | Python 3.13+ (local development verified with Python 3.14) |

---

## Data flow

```
Listing sources
      │
      ▼
 Bronze  →  raw ingestion
      │
      ▼
 Silver  →  cleaning & normalization
      │
      ▼
 Gold   →  private aggregated metrics
      │
      ▼
 Public API → aggregated `api_*` tables with RLS
      ├── app.py → Streamlit dashboard
      └── public REST consumers
```

This repository holds the **dashboard, public API contract, API health checks,
and uptime automation**. It consumes the safe public API layer produced from
the upstream Gold data.

---

## Getting started

```bash
git clone https://github.com/Revo69/Imobil-Index.git
cd Imobil-Index
pip install -r requirements.txt
```

Add your Supabase credentials to `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"
```

Run locally:

```bash
streamlit run app.py
```

Check the public API connection without starting Streamlit:

```bash
python scripts/check_api_health.py
```

The smoke-check verifies row availability and freshness for every published
`api_*` table, including sale profiles, housing type, finish/condition, and floor-position metrics.
For REST endpoints, table definitions, access rules, and request examples, see
[Public API v1](docs/public_api_v1.md).

A ready-to-use [Dev Container](.devcontainer/devcontainer.json) is included for one-click setup in GitHub Codespaces.

---

## Keeping the app awake

```bash
pip install playwright
playwright install chromium
python wake_streamlit.py
```

This is run automatically every 6 hours by [`.github/workflows/keep-awake.yml`](.github/workflows/keep-awake.yml).

---

## Contact

**Serghei Matenco**
📩 [sergey.revo@outlook.com](mailto:sergey.revo@outlook.com)

© 2026 Imobil.Index
