# Imobil.Index 2025 — Real Estate Analytics Dashboard 🏠

**Imobil.Index** is a data pipeline and analytics dashboard for the Moldovan real estate market.  
It collects property listings, processes them through a structured *bronze → silver → gold* pipeline, and visualizes key market insights in an interactive Streamlit app.

---

## 🚀 Features
- **Automated ETL pipeline**  
  - Bronze: raw listings ingestion  
  - Silver: normalization and cleaning  
  - Gold: aggregated metrics and materialized views  

- **Interactive dashboard** (Streamlit + Plotly)  
  - Active listings count  
  - Average price per square meter  
  - Top‑10 cheapest and most expensive districts  
  - 90‑day price dynamics for Chișinău sectors  
  - Full searchable table of all regions  

- **Supabase integration** for cloud database and API access  
- **CI/CD workflows** with GitHub Actions for daily updates  

---

## 📊 Tech Stack
- **Python 3.11**  
- **Supabase (Postgres + API)**  
- **Streamlit** for dashboard UI  
- **Plotly Express** for charts  
- **GitHub Actions** for automation  

---

## 📈 Dashboard Preview
The dashboard provides real‑time insights into Moldova’s housing market:
- Transparent metrics for buyers, sellers, and analysts  
- Clean minimalist design with dark theme support  
- Updated daily via automated pipeline  

---

## 📅 Data Pipeline
- **Collect links** → store raw data in SQLite (bronze)  
- **Parse bronze** → enrich and normalize records (silver)  
- **Commit & push** → sync database artifacts  
- **Silver loader** → upload normalized data to Supabase  
- **Gold loader** → refresh materialized views for analytics  

---

## 🎯 Goal
To make the Moldovan real estate market **transparent, accessible, and analyzable** for everyone — from casual buyers to professional analysts.

---

## 📧 Contact
Maintained by **Revoland Analytics**  
📩 sergey.revo@outlook.com  

---
