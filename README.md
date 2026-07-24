# 🏠 Imobil.Index

**Real-time analytics for Moldova's residential real estate market** — for-sale prices, monthly rentals, and daily (short-term) rentals, all in one live dashboard.

[![Live Demo](https://img.shields.io/badge/demo-live-2563eb?style=flat-square)](https://imobil-index.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![Automated](https://img.shields.io/badge/keep--alive-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

**[→ Open the live dashboard](https://imobil-index.streamlit.app)**

---

## What it does

Imobil.Index turns raw property listings into decision-ready market intelligence for buyers, sellers, and investors. The dashboard reads pre-aggregated data from a Supabase (Postgres) **gold layer** and surfaces it as three interactive views:

| Tab | What you get |
|---|---|
| 🏷️ **For Sale** | Price per m² by sector, cheapest/most expensive districts, 90-day price trend for Chișinău |
| 📅 **Monthly Rent** | Rental price per m² by sector, top/bottom districts, annualized rental yield |
| 🌙 **Daily Rent** | Short-term rental pricing, occupancy-adjusted yield, daily vs. monthly yield comparison |

Data is refreshed daily through an upstream ETL pipeline (**bronze → silver → gold**: raw ingestion → cleaning/normalization → aggregated metrics), and this dashboard consumes the final gold-layer tables via the Supabase API.

---

## Highlights

- **Listings-weighted pricing** — average price per m² is weighted by listing count per sector, not a naive mean, avoiding skew from thin markets
- **Lean historical queries** — the 90-day trend chart pulls only the columns and date range it needs (`date, city, sector, avg_per_m2_eur`), server-side filtered and paginated, instead of loading full tables into memory
- **Hourly caching** (`st.cache_data(ttl=3600)`) to keep the app responsive without hammering the database
- **Graceful per-tab failure handling** — an empty dataset in one tab shows an error without killing the other two (avoids the classic `st.stop()`-in-a-tab pitfall)
- **Self-waking deployment** — Streamlit Community Cloud puts idle free-tier apps to sleep; a plain HTTP request only returns the static "asleep" shell, so a Playwright script actually drives a headless browser to click the wake button, scheduled via GitHub Actions 4× daily

---

## Tech stack

| Layer | Tools |
|---|---|
| Dashboard | Streamlit, Plotly Express |
| Data | Supabase (Postgres + REST API) |
| Automation | GitHub Actions, Playwright |
| Language | Python 3.12 |

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
  Gold   →  aggregated metrics (gold_estate_current, gold_estate_daily,
             gold_rent_current, gold_rent_yield)
      │
      ▼
 Supabase (Postgres + API)
      │
      ▼
 app.py  →  Streamlit dashboard (this repo)
```

This repository holds the **dashboard and its uptime automation**; it consumes the gold-layer tables produced upstream.

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
SUPABASE_KEY = "your-anon-or-service-key"
```

Run locally:

```bash
streamlit run app.py
```

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
