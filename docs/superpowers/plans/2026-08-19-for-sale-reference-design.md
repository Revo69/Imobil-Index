# For Sale Reference Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the selected compact, editorial dashboard reference to Imobil.Index, starting with the For Sale tab, while preserving all filters, tabs, public `api_*` contracts, and listing-weighted calculations.

**Architecture:** Keep the current Streamlit structure: `app.py` owns data loading, filtering, and tab order; `dashboard_transforms.py` remains the single source for aggregation and freshness logic; `dashboard_components.py`, `dashboard_charts.py`, and `dashboard_theme.py` receive presentational changes only. The selected reference changes hierarchy and visual treatment, not the data model.

**Tech Stack:** Python, Streamlit, Plotly, pandas, Supabase public `api_*` views, unittest, Ruff.

**Spec:** Selected visual reference: `C:\Users\123\.codex\generated_images\01a01b8d-14d1-7b43-838a-14a8cff2d992\exec-a4c8545b-9d56-4611-916d-4a23f5e195b7.png`.

## Global Constraints

- Preserve the left `Explore market` panel, all controls, all four tabs, their current filter scope, and empty/error states.
- Keep current public `api_*` read contracts. Do not add a query, table, metric, or Supabase change for this design work.
- `Data as of` comes only from `latest_data_date()` over loaded Gold/public snapshot data. It appears once in the application header and must not be repeated in a market-signals block.
- Any displayed market average remains `weighted_average(df, price_col)`, weighted by `listings`. Never average city-sector averages equally.
- Do not invent metrics implied by the reference, including days on market, price cuts, `live` status, percentile ranges, or price movement when the available data cannot support them.
- Keep the existing sale-profile branch: room/area selections use `build_sale_market_from_segments()` and the profile trend; unfiltered sales use the current market data and `render_sales_trend()`.
- Visible copy stays business-friendly, specific about scope, and uses `Chișinău` consistently. Yield remains labelled as indicative gross yield.
- Every visual change must retain readable desktop and 390 px mobile layouts, visible values where practical, and coherent chart typography/colours.
- Do not change `dashboard_transforms.py` formulas unless a failing invariance test proves a bug in existing behaviour; this design plan assumes no formula change.

---

## Data-to-Interface Contract

| Reference element | Product source and formula | Required fallback |
| --- | --- | --- |
| Application date | `max(latest_data_date(df_sales), latest_data_date(df_rent), latest_data_date(df_yield))` already assembled as `latest_snapshot` | `No snapshot` |
| For Sale hero | Existing `render_sales_trend(df_hist_sales, selected_cities)` or `render_profile_sales_trend(...)`; existing 90-day and filter logic | Existing trend empty state, without a fake chart |
| Current-market price | `weighted_average(df, "avg_per_m2_eur")` | Current empty state |
| Signals | Existing filtered `df`: total listings, most-active sector, lowest/highest sector, sector median, and price spread | Hide the signal rail if `df` is empty |
| Rankings and detail | Existing `render_listing_sections` / `render_price_sections`, budget guide, city comparison, profile disclosure, and sector table | Existing per-block empty state |
| Period movement | Existing Insights-only weekly helpers, only when their current comparability threshold is met | Do not show a movement signal |

## Implementation Tasks

### Task 1: Establish the visual and semantic baseline

**Files:**
- Inspect: `app.py`, `dashboard_components.py`, `dashboard_charts.py`, `dashboard_theme.py`, `dashboard_transforms.py`
- Inspect: `tests/test_dashboard_transforms.py`, `tests/test_sale_tab_layout.py`
- Create: `tests/test_reference_design_contract.py`

- [ ] Record one desktop and one 390 px screenshot of the current For Sale page before editing, including the default state and a Chișinău preset state.
- [ ] Add source-level regression checks for the two non-negotiable layout facts: `render_app_header(latest_snapshot)` is called once, and the For Sale trend remains before the current-market summary.
- [ ] Add data-contract tests without changing production formulas:

```python
def test_weighted_market_price_is_not_sector_average(self) -> None:
    market = pd.DataFrame({"listings": [90, 10], "avg_per_m2_eur": [1000, 2000]})
    self.assertEqual(weighted_average(market, "avg_per_m2_eur"), 1100.0)

def test_snapshot_label_comes_from_latest_loaded_snapshot(self) -> None:
    self.assertEqual(latest_data_date(pd.DataFrame({"date": ["2026-08-17"]})), pd.Timestamp("2026-08-17"))
```

- [ ] Run the baseline suite before changing UI code:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m py_compile app.py
.\.venv\Scripts\python.exe -m ruff check app.py dashboard_components.py dashboard_charts.py dashboard_theme.py
```

### Task 2: Define one coherent visual system, without changing behaviour

**Files:**
- Modify: `dashboard_theme.py`
- Modify: CSS block in `app.py`

- [ ] Evolve the existing green, off-white, muted-border token system rather than introduce an isolated new palette.
- [ ] Add narrowly named tokens/styles for the dark sale hero, quiet signal rail, compact metric cells, section rhythm, and mobile stacking.
- [ ] Keep current Streamlit widget styling and selected-state accessibility; the left panel must remain recognisably the same working control area.
- [ ] Apply the styles to existing class names or new presentational classes only. No data variables, filter keys, callbacks, API calls, or transformations change in this task.
- [ ] Check the source diff to confirm this task touches no `load_*`, `filter_*`, `build_*`, or `weighted_average` code.

### Task 3: Replace the duplicated top-date treatment and construct the For Sale frame

**Files:**
- Modify: `dashboard_components.py`
- Modify: `app.py`
- Modify: `tests/test_reference_design_contract.py`

- [ ] Keep `render_app_header(latest_snapshot)` as the sole visible snapshot-date owner. It should retain the actual latest snapshot text and become a compact top-right status treatment.
- [ ] Introduce a presentational `render_market_signal_rail(...)` component that accepts already-filtered data and explicitly has no date argument.
- [ ] Lay out the default For Sale entry as: existing left filter panel; tab navigation; dark `Chișinău price pulse` hero; adjacent `Chișinău signals`; then the current-market and ranking/detail sections.
- [ ] The signal rail may use only existing values: weighted price per m2, total listings, most-active sector/listings, lowest/highest sector, price range, or sector median. It must not use labels such as `Market signals — 19 Aug`, `Live`, `Price drops`, or `Days on market`.
- [ ] For a selected city other than Chișinău, preserve the current explanatory trend empty state and avoid calling the rail `Chișinău signals` unless the content is actually Chișinău-specific. Prefer a neutral `Market signals` title for non-Chișinău filtered views.
- [ ] Add source tests that prevent a second `Data as of` literal in the signal component and preserve `render_sales_trend` / `render_profile_sales_trend` before `render_tab_header`.

### Task 4: Restyle existing charts and summaries around the selected hierarchy

**Files:**
- Modify: `dashboard_charts.py`
- Modify: `app.py`
- Modify: `dashboard_components.py`
- Modify: `tests/test_sale_tab_layout.py`

- [ ] Restyle `render_sales_trend` and the sale-profile trend with the dark-hero chart treatment while retaining their data frames, 90-day window, Chișinău condition, labels, last-point annotations, hover text, and existing empty states.
- [ ] Keep the existing direct latest-point labels readable against the dark background; chart colours must retain sufficient contrast and remain distinguishable without hover.
- [ ] Reuse the existing `render_market_highlights` values as compact cells/rail signals instead of adding a parallel calculation. Its median remains the unweighted median across visible sectors and its label must say so.
- [ ] Keep `Current market view`, prices/listings rankings, Budget guide, city comparison, `Property characteristics`, and sector table in their existing logical order after the hero. Adapt their spacing/cards only.
- [ ] Do not add a reference-style sector percentile/dumbbell chart unless a later scoped request defines its business meaning, source grain, formula, label, and empty state.
- [ ] Extend layout tests only for the intended order; do not replace behavioural tests with screenshots alone.

### Task 5: Carry the shared design language through the other tabs safely

**Files:**
- Modify: `app.py`
- Modify: `dashboard_components.py`
- Modify: `dashboard_charts.py` (only shared chart chrome)
- Modify: `tests/test_sale_tab_layout.py`

- [ ] Apply shared shell, typography, card, tab, and responsive styles to Monthly Rent, Daily Rent, and Insights without forcing sale-specific `Chișinău` hero content into them.
- [ ] Preserve their current primary stories and order: monthly rent summary/rankings/yield; daily occupancy-adjusted yield before rankings and closed return scenarios; weekly brief before decision notes in Insights.
- [ ] Preserve all existing labels and qualifiers for `per month`, occupancy assumptions, and indicative gross yield. Review every changed label against its calculation and scope.
- [ ] Verify `Chart focus` still switches only the main rankings in each tab, exactly as the existing caption promises.

### Task 6: Validate logic, copy, interactions, and responsive quality

**Files:**
- Modify: `PROGRESS.md` after verified completion only
- Inspect: all changed files and local Streamlit screenshots

- [ ] Run focused automated checks after each implementation task and the complete suite at the end:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m py_compile app.py dashboard_components.py dashboard_charts.py dashboard_theme.py
.\.venv\Scripts\python.exe -m ruff check app.py dashboard_components.py dashboard_charts.py dashboard_theme.py
```

- [ ] Start the app with the project environment and visually inspect at a desktop viewport and 390 x 844 mobile viewport. Capture fresh screenshots for comparison with the selected reference.

```powershell
.\.venv\Scripts\streamlit.exe run app.py --server.address 127.0.0.1 --server.port 8503
```

- [ ] Run this manual scenario matrix with real loaded data: default For Sale; Chișinău preset; another-city preset; room-only profile; area-only profile; Prices and Listings focus; empty state via a restrictive listings threshold; all four tabs.
- [ ] For each scenario, check: one visible snapshot date; no fabricated metric/copy; labels match units and filter scope; weighted price is still based on listings; trend/weekly periods retain their actual conditions; values do not overflow or become unreadable.
- [ ] Compare code paths before/after to confirm public `api_*` calls, data-loading functions, and transform formulas are unchanged. Check `git diff --check` and `git status --short`.
- [ ] Update `PROGRESS.md` with only verified facts: files changed, checks run, viewports checked, and explicit confirmation that filters, API contract, and calculations were not changed.

## Review Checklist

- [ ] The application has exactly one top-level `Data as of` display and it uses the latest snapshot, not the system clock.
- [ ] No calculated average regressed from listing-weighted to equally weighted sector averages.
- [ ] Every reference-inspired UI element has a real source, precise label, unit, and fallback state.
- [ ] The left panel, tabs, filters, API contract, and For Sale profile branch remain intact.
- [ ] The interface reads coherently within about five seconds: current scope, price movement, current signals, then detailed comparison.
- [ ] Both desktop and mobile screenshots were actually checked before declaring the design complete.
