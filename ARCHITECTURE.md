# ARCHITECTURE.md

Architecture review and refactoring plan for Imobil.Index.

Last reviewed: 2026-07-30

## Purpose

This document describes the current Streamlit dashboard structure and a
beginner-friendly target structure for gradual AI-assisted development.

It is intentionally a plan only. No application code is changed here.

## Current Project Structure

```text
Imobil-Index/
  app.py
  dashboard_charts.py
  components.py
  data.py
  transforms.py
  theme.py
  requirements.txt
  README.md
  AGENTS.md
  PROGRESS.md
  ARCHITECTURE.md
  .gitignore
  wake_streamlit.py
  docs/
    public_api_v1.md
  sql/
    public_api_layer.sql
    refresh_gold_updates_api_layer.sql
    add_estate_segments_api_layer.sql
    add_estate_segments_daily_api_layer.sql
    revoke_internal_public_access.sql
    check_public_api_layer.sql
  .github/
    workflows/
      keep-awake.yml
  .devcontainer/
    devcontainer.json
```

## What Each File Owns Today

| File or folder | Current responsibility |
|---|---|
| `app.py` | Main Streamlit dashboard: page setup, CSS injection, UI constants, remaining chart-specific render helpers, tab logic, and main execution flow. |
| `dashboard_charts.py` | Shared Plotly config, `st.plotly_chart` wrapper, common Plotly layout styling, and ranked/listing/price chart sections. |
| `components.py` | Shared UI primitives: section heading, empty state, and chart title. |
| `data.py` | Supabase client creation, public API column contracts, cached data loaders, and paginated fetch helper. |
| `transforms.py` | Pure pandas helpers for freshness, weighted averages, labels, city/profile filtering, segment summaries, and profile-to-market aggregation. |
| `theme.py` | Shared dashboard theme tokens, CSS-variable generation, and named chart color scales. |
| `requirements.txt` | Runtime dependencies for Streamlit Cloud / local setup. |
| `README.md` | Public project overview, setup, data-flow explanation, and live dashboard link. |
| `AGENTS.md` | AI-agent working rules, dashboard UX standards, data semantics, and preferred checks. |
| `PROGRESS.md` | Lightweight project log, recent changes, verification status, and next steps. |
| `.gitignore` | Local Python, Streamlit secrets, cache, editor, and temp-file exclusions. |
| `docs/public_api_v1.md` | Public API contract and examples for safe aggregated API tables. |
| `sql/*.sql` | Manual Supabase SQL scripts for API layer creation, refresh-function updates, access cleanup, and health checks. |
| `wake_streamlit.py` | Playwright-based keep-awake script for Streamlit Community Cloud. |
| `.github/workflows/keep-awake.yml` | Scheduled GitHub Action that runs `wake_streamlit.py`. |
| `.devcontainer/devcontainer.json` | Codespaces/devcontainer setup and auto-run command for Streamlit. |

## Current `app.py` Shape

`app.py` is the product entrypoint and currently holds several layers at once.
The exact line count can vary by tool because of line-ending handling, but it is
already a large single file with roughly two thousand lines and many render
functions.

Main sections observed:

| Area | Current contents |
|---|---|
| Config/constants | `st.set_page_config`, deal-type constants, city constants, and category orders. |
| Style | Large inline CSS block injected through `st.markdown(..., unsafe_allow_html=True)`, with CSS variables generated from `theme.py`. |
| Data loading | Delegated to `data.py` through `load_historical_data`, `load_historical_segment_data`, and `load_data` imports. |
| Data helpers | Delegated to `transforms.py` for freshness, labels, weighted averages, segment filtering, segment aggregation, and market rebuilding. |
| UI primitives | Section heading, empty state, and chart title delegated to `components.py`; header, KPI card, and insight cards remain in `app.py`. |
| Chart helpers | Shared Plotly wrapper/style and ranked/listing/price chart sections delegated to `dashboard_charts.py`; segment charts, yield charts, and trend lines remain in `app.py`. |
| Insight logic | Decision notes, break-even analysis, outside-Chisinau radar, yield opportunity notes. |
| Main flow | Load data, derive filter options, render header, left filter panel, four tabs, footer. |

## Where Layers Are Mixed

The current design is acceptable for a solo MVP, but it is becoming harder for
AI-assisted work because every change requires reading a very large `app.py`.

| Mixed concern | Example | Why it matters |
|---|---|---|
| Data access + UI | Supabase table calls now live in `data.py`, but `app.py` still directly consumes the loaded DataFrames in the main flow. | This is a good first split, but data contracts and UI assumptions are still only loosely documented. |
| Data transformation + rendering | Core pandas helpers now live in `transforms.py`, but some insight preparation still lives near render functions. | Keep moving only pure helpers when the boundary is obvious. |
| Data transformation + data loading | `data.py` loads public API data, while `transforms.py` handles profile-filtered market aggregates. | This boundary is now clearer; later tests can protect it. |
| Data loaders + error policy | `data.py` has a shared paginated fetch helper, while the wrappers keep required-vs-optional behavior. | The behavior is now easier to see, but it still needs tests or typed contracts later. |
| Streamlit internals + app theme | CSS targets internal `data-testid` selectors. | This works today, but it is fragile across Streamlit upgrades. |
| SQL contract + app assumptions | Public API tables and app queries are coordinated through docs and scripts, not typed contracts. | Column drift can appear only at runtime. |

## Review Findings

### P1: `app.py` Is Too Large For Safe Growth

Current state: `app.py` still owns header/cards, remaining chart-specific logic,
tabs, and app flow. Shared UI primitives live in `components.py`, shared chart
helpers and ranked/listing/price chart sections live in `dashboard_charts.py`, data
loading lives in `data.py`, core pandas helpers live in `transforms.py`, and
theme tokens live in `theme.py`.

Risk: AI-assisted edits need too much context and can create accidental changes
outside the intended area.

Target: continue splitting gradually. The next low-risk candidates are remaining
chart-specific helpers or insight-specific service helpers.

### Resolved: `pandas` Is Explicit In `requirements.txt`

Current state: `requirements.txt` now declares `pandas>=2.2,<3` explicitly.

Remaining note: if the project later needs fully reproducible builds, replace
range-based dependency entries with a lockfile or exact pins.

### Resolved: Theme Tokens Have A Shared Source

Current state: `theme.py` owns shared dashboard theme tokens, CSS variable
generation, Plotly text/grid/hover colors, and named chart scales.

Remaining note: some older inline CSS details and specialist chart palettes can
still be normalized later, but the main source of truth now exists.

### Resolved: One-Off Red Chart Palette Is Named

Current state: the `For Sale` highest-price chart now uses
`HIGH_PRICE_COLOR_SCALE` from `theme.py`.

Remaining note: the palette values were intentionally preserved to avoid a
visual behavior change during structural cleanup.

### Partially Resolved: Similar Supabase Loaders Share Pagination

Current state:

- `data.py` has one shared `fetch_paginated_rows()` helper.
- `load_historical_data` remains a required dataset.
- `load_historical_segment_data` remains optional and returns an empty
  DataFrame on failure.

Risk: the required-vs-optional behavior is clearer now, but not covered by
tests yet.

Target: add a tiny testable data-service layer later if failure behavior becomes
more complex.

### P2: CSS Uses Internal Streamlit Selectors

Current state: CSS targets selectors such as `data-testid="stHeader"`,
`stToolbar`, `stDecoration`, `stTabs`, `stMetric`, and others.

Risk: these selectors are not the stable public API. Pinning
`streamlit==1.58.0` reduces the immediate risk, but upgrades need visual QA.

Target: keep this approach for now because Streamlit styling often needs it, but
centralize the CSS and add a Streamlit upgrade checklist.

### P3: Local Environment Discovery Is Fragile

Current state: the project now has a local `.venv` using Python 3.14.6. Ruff is
available there and passes for the active Python files.

Risk: Python 3.14 is newer than many common production defaults, so dependency
compatibility should be watched during deploys and CI setup.

Target: keep using the project-local `.venv` for local checks and consider
pinning the deployment Python version if Streamlit Cloud behavior differs.

## Target Architecture

Keep the project beginner-friendly. Do not jump to a framework-heavy package
layout. Use a small `src/imobil_index/` package only when the first extraction
is ready.

Recommended target:

```text
Imobil-Index/
  app.py
  requirements.txt
  README.md
  AGENTS.md
  PROGRESS.md
  ARCHITECTURE.md
  wake_streamlit.py
  docs/
    public_api_v1.md
  sql/
    ...
  src/
    imobil_index/
      __init__.py
      config.py
      theme.py
      data/
        __init__.py
        client.py
        loaders.py
        transforms.py
      services/
        __init__.py
        metrics.py
        insights.py
      ui/
        __init__.py
        styles.py
        components.py
        charts.py
        filters.py
        tabs_sale.py
        tabs_rent.py
        tabs_insights.py
```

## Target Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Thin Streamlit entrypoint: page config, load data, build filters, call tab renderers, footer. |
| `config.py` | Constants: table names, column strings, deal types, city constants, room/area order, history window. |
| `theme.py` | Single source of truth for colors, spacing, chart roles, and Plotly style values. |
| `data/client.py` | Supabase client creation from `st.secrets`. |
| `data/loaders.py` | Cached Supabase reads and shared pagination helper. No Streamlit rendering except cache decorators if kept there. |
| `data/transforms.py` | DataFrame filtering, segment aggregation, trend preparation, freshness dates. |
| `services/metrics.py` | Weighted averages, KPI row selection, market spread, listings summaries. |
| `services/insights.py` | Deterministic business insight card data: decision notes, break-even, yield opportunities. |
| `ui/styles.py` | CSS generation/injection from `theme.py`; Streamlit selector hacks live here only. |
| `ui/components.py` | Header, section title, KPI card, insight cards, empty state, table wrapper. |
| `ui/charts.py` | Plotly chart builders and shared chart styling. |
| `ui/filters.py` | Left filter panel and preset/session-state behavior. |
| `ui/tabs_sale.py` | For Sale tab orchestration only. |
| `ui/tabs_rent.py` | Monthly Rent and Daily Rent tab orchestration. |
| `ui/tabs_insights.py` | Insights tab orchestration. |

## Dependency Direction

Keep dependencies one-way:

```text
app.py
  -> ui.tabs_*
  -> ui.components / ui.charts / services / data.transforms
  -> config / theme

data.loaders
  -> data.client / config

services
  -> data.transforms / config

ui
  -> services / data.transforms / theme
```

Avoid these dependencies:

```text
data -> ui
services -> streamlit
theme -> data
config -> streamlit
```

This keeps data and business logic testable without starting Streamlit.

## Data Layer Plan

The data layer should own only loading and raw API contracts.

Planned functions:

| Function | Purpose |
|---|---|
| `get_supabase_client()` | Create the Supabase client from secrets. |
| `fetch_paginated(table, columns, *, gte_date=None, order_by=None, optional=False)` | Shared pagination and consistent error policy. |
| `load_current_data()` | Load current API tables: sale, sale segments, rent, yield. |
| `load_sale_history()` | Load `api_estate_daily`. |
| `load_sale_segment_history()` | Load `api_estate_segments_daily`, optional until enough snapshots exist. |

The app should not know pagination details.

## Services Layer Plan

The services layer should own business meaning.

Examples:

| Service | Purpose |
|---|---|
| `weighted_average` | Listing-weighted average calculation. |
| `build_sale_market_from_segments` | Rebuild city-sector sale grain from room/area segments. |
| `build_segment_summary` | Aggregate by room group or area band. |
| `build_break_even_table` | Build daily-vs-monthly comparison. |
| `build_decision_notes` | Return card data, not HTML. |
| `build_yield_opportunities` | Return card data, not Streamlit UI. |

Services return values or DataFrames. They do not call `st.markdown`.

## UI Layer Plan

The UI layer should own display, not business calculation.

Examples:

| UI module | Purpose |
|---|---|
| `styles.py` | Inject CSS generated from theme tokens. |
| `components.py` | Reusable Streamlit/HTML components. |
| `charts.py` | Plotly figure creation and chart rendering. |
| `filters.py` | Sidebar/left-panel controls and session-state reset behavior. |
| `tabs_sale.py` | Render sale workflow using prepared data and service outputs. |
| `tabs_rent.py` | Render monthly/daily rent workflows. |
| `tabs_insights.py` | Render insight cards and insight charts. |

## Theme Plan

Create one source of truth:

```text
theme.py
  THEME = {
      "bg": "...",
      "surface": "...",
      "ink": "...",
      "text": "...",
      "muted": "...",
      "border": "...",
      "sale_scale": [...],
      "rent_scale": [...],
      "daily_scale": [...],
      "yield_scale": [...],
      "high_price_scale": [...],
  }
```

Then:

- CSS variables are generated from `THEME`.
- Plotly layout colors read from `THEME`.
- One-off palettes are replaced by named semantic scales.

## Streamlit Styling Policy

Because Streamlit does not expose every styling hook as a stable public API, the
project may continue using some `data-testid` selectors.

Rules:

1. Keep all selector-based CSS in `ui/styles.py`.
2. Add comments only for fragile selectors.
3. Before upgrading Streamlit, visually check:
   - header hidden correctly;
   - left panel spacing;
   - tab toolbar;
   - number input;
   - metric/card spacing;
   - dataframe borders;
   - mobile layout.
4. Do not add isolated CSS hacks inside tab renderers.

## Refactoring Sequence

Use small safe steps. Each step should be deployable by itself.

### Step 0: Dependency Hygiene

Scope:

- Add `pandas` explicitly to `requirements.txt`.

Why first:

- Very low effort.
- Removes hidden reliance on transitive dependencies.

Verification:

```powershell
python -m py_compile app.py
python -m ruff check app.py
streamlit run app.py
```

### Step 1: Theme Tokens

Scope:

- Introduce `theme.py`.
- Move color constants from `app.py` into `theme.py`.
- Replace the one-off red scale with a named semantic scale.
- Keep generated CSS visually identical at first.

Why:

- Fixes the duplicate CSS/Plotly color source of truth.
- Reduces future UI drift.

Acceptance:

- No chart changes except intentional color-token naming.
- Dashboard still looks the same.

### Step 2: Shared Supabase Pagination

Scope:

- Add `data/loaders.py`.
- Move duplicated pagination into `fetch_paginated`.
- Preserve cache TTL and current table names.
- Make error policy explicit:
  - required history: fail visibly;
  - optional profile history: empty state;
  - current market data: fail dashboard load.

Why:

- Removes copy/paste.
- Makes failure behavior deliberate.

### Step 3: Data Transforms

Scope:

- Add `data/transforms.py`.
- Move pure DataFrame helpers:
  - labels;
  - freshness;
  - weighted average;
  - city/listing filters;
  - profile filters;
  - segment aggregation;
  - sale market rebuild.

Why:

- These are easiest to test without Streamlit.
- Reduces risk when editing charts or UI.

### Step 4: UI Primitives

Scope:

- Add `ui/components.py`.
- Move header, section, KPI card, insight cards, empty state, chart title, and table wrapper.

Why:

- Makes visual consistency easier.
- Keeps HTML/CSS usage in one place.

### Step 5: Charts

Scope:

- Add `ui/charts.py`.
- Move Plotly style and chart builders.
- Keep chart functions data-in, figure/render-out.

Why:

- Chart styling becomes centralized.
- Future visual QA gets simpler.

### Step 6: Tabs

Scope:

- Add:
  - `ui/tabs_sale.py`
  - `ui/tabs_rent.py`
  - `ui/tabs_insights.py`
- Keep `app.py` as orchestrator.

Why:

- Makes each product area independently editable.
- Reduces AI context load for future features.

## Suggested First PR

Keep the first PR deliberately boring:

1. Add `pandas` to `requirements.txt`.
2. Add `theme.py` with existing tokens.
3. Replace the inline red scale with a named constant.
4. Do not move tab code yet.

This fixes two real issues without doing a risky structural rewrite.

## Suggested Second PR

Extract data loading only:

1. Add `src/imobil_index/data/loaders.py`.
2. Move Supabase pagination there.
3. Keep Streamlit cache behavior unchanged.
4. Keep `app.py` imports simple and obvious.

## Suggested Third PR

Extract pure transforms:

1. Add `src/imobil_index/data/transforms.py`.
2. Move pure pandas helpers.
3. Add a tiny test file later if the project adopts tests.

## What Not To Do Yet

- Do not rewrite the app into many files in one pass.
- Do not introduce classes just to organize functions.
- Do not add a complex dependency injection system.
- Do not move SQL scripts into Python migrations until the database workflow is
  clearer.
- Do not redesign the UI while moving modules. Visual changes and structural
  refactors should be separate.

## Verification Checklist For Each Refactor Step

Minimum:

```powershell
python -m py_compile app.py
git diff --check
```

Preferred real environment:

```powershell
python -m ruff check app.py
streamlit run app.py
```

Manual visual checks:

- Header shows latest snapshot date.
- Left filters render and reset correctly.
- For Sale, Monthly Rent, Daily Rent, and Insights tabs open.
- Room/area filters affect only For Sale.
- KPI cards use listing-weighted averages.
- Trend chart does not pretend profile history exists before enough snapshots.
- No card overlap on desktop.
- Mobile layout remains usable.

## Decision

The current single-file architecture was a reasonable MVP choice and matches the
earlier project rule to avoid structural rewrites unless explicitly requested.

Now that the dashboard has four tabs, public API tables, profile segments, and
more history logic, the target should be gradual modularization:

1. dependencies and theme;
2. data loading;
3. data transforms;
4. UI primitives;
5. charts;
6. tab modules.

This keeps the project understandable for a beginner while making future
AI-assisted development much safer.
