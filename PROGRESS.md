# PROGRESS.md

Simple project progress log for Imobil.Index.

## Last Updated

2026-07-27

## Current State

- The dashboard is a single-file Streamlit app in `app.py`.
- It reads Supabase Gold tables for sale, monthly rent, daily rent, yield, and 90-day history.
- The UI has a left Explore filter panel and four tabs:
  - For Sale
  - Monthly Rent
  - Daily Rent
  - Insights
- The Insights tab contains deterministic, rule-based analytics only. No AI layer is used in the app.

## Recently Done

- Added or preserved modern dashboard layout with header, tabs, KPI cards, charts, and tables.
- Confirmed `render_insight_cards()` uses `st.columns()` and renders each HTML card separately.
- Improved insight-card text wrapping and mobile card sizing.
- Improved some Insights wording for business users.
- Added a short caveat under daily-vs-monthly break-even.

## Important Verified Semantics

- Data freshness should use the latest Gold snapshot date.
- Market average price per m2 should be weighted by `listings`.
- Yield values should be described as indicative gross yield.

## Current Verification

- `app.py` syntax passed with bundled Codex Python using:

```powershell
python -m py_compile app.py
```

- Ruff was not verified in the current local environment because `ruff` was not installed there.
- Streamlit visual verification was not completed in the current local environment because `streamlit` was not available there.

## Next Small Steps

1. Run checks in the real project environment:

```powershell
python -m py_compile app.py
python -m ruff check app.py
streamlit run app.py
```

2. Visually verify the app:

- Insights cards render as cards, not literal HTML.
- For Sale, Monthly Rent, Daily Rent, and Insights tabs still work.
- Left filters affect all tabs.
- Sector details table has no horizontal overflow.
- Header, tabs, and cards look clean on desktop.

3. After that, choose only one next improvement:

- polish Insights wording;
- improve mobile layout;
- improve error states;
- add SQL-side filtering for history;
- add new parser/database fields in the upstream project later.

## Parking Lot

- Daily vs monthly rent calculator.
- Weekend house index.
- Suburban radar improvements.
- Ideal apartment portrait.
- Rule-based weekly market notes.
- Future parser fields: rooms, area, floor, house/dacha/land, amenities, distance from Chisinau.

