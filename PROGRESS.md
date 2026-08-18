# PROGRESS.md

Simple project progress log for Imobil.Index.

## Last Updated

2026-08-19

## Current State

- The dashboard is still centered on `app.py`, with data loading in
  `dashboard_data.py`, shared chart helpers in `dashboard_charts.py`, shared UI
  primitives and card renderers in `dashboard_components.py`, theme tokens in
  `dashboard_theme.py`, and pure pandas helpers in `dashboard_transforms.py`.
- It reads Supabase Gold tables for sale, monthly rent, daily rent, yield, and 90-day history.
- The UI has a left Explore filter panel and four tabs:
  - For Sale
  - Monthly Rent
  - Daily Rent
  - Insights
- The Insights tab contains deterministic, rule-based market signals only. No AI layer is used in the app.

## Recently Done

- Added the first standard-library regression tests for dashboard transforms:
  listing-weighted prices, profile aggregation, weekly snapshot selection,
  city-level weekly weighting, and occupancy-adjusted daily return.
- Added a focused GitHub Actions workflow for the dashboard logic:
  it uses Python 3.13, installs only runtime dependencies, compiles the
  dashboard modules, and runs the deterministic tests without Supabase secrets.
- Replaced the weekly comparison's deprecated generic timedelta with an
  explicit seven-day unit, discovered while running the new tests.
- Restored the proven two-column Explore panel after the native sidebar hid its
  opening control together with Streamlit's hidden header. No filter keys,
  calculations, or public data contracts changed.
- Reduced the default Insights view after a UX audit:
  - city and sector weekly signals are now one `Weekly market brief`, with a
    city-level view when at least three comparable cities exist and a clear
    sector-level fallback otherwise;
  - outside-Chisinau cards and the regional chart now form one `Regional value
    comparison` section;
  - secondary yield cards and the investment shortlist are behind a collapsed
    `Investment analysis` disclosure;
  - daily-versus-monthly break-even and return decisions now live in Daily
    Rent, next to the occupancy assumption they use;
  - sale-price decision cards now show `EUR/m2` explicitly where applicable.
- Deferred a separate mobile filter-panel pass. It needs its own responsive
  layout design so the existing global and For Sale filters remain easy to use.
- Added `Daily vs monthly return` using the existing public
  `api_rent_yield` contract, with no schema or refresh change:
  - `Expected occupancy` is one clearly scoped slider in the left filter panel;
  - daily gross return is re-scaled from the published 60% occupancy model;
  - the comparison stays at city-sector grain and requires the selected minimum
    supply for both sale and rent data;
  - it shows direct return, break-even occupancy, and daily-versus-monthly
    values, with gross-yield cost caveats.
- Refined the occupancy control after user testing: it updates the Daily Rent
  yield chart, break-even, and return comparison, while monthly-rent values
  stay fixed.
- Added rule-based weekly market signals using existing public sale history and
  current visible city-sector markets:
  - compares the latest snapshot to the closest snapshot at least seven days
    earlier, only for markets present in both snapshots;
  - shows median movement, the largest increase, and the lowest movement;
  - stays hidden when fewer than three comparable markets are available;
  - clearly states that it tracks average asking price per m2 rather than
    transaction prices or a listing-weighted market index.
- Unified visible numeric formatting across the dashboard:
  - dots separate thousands and commas separate decimal fractions, for example
    `105.865,4`;
  - KPI cards, insight cards, chart labels and hover values, and dashboard
    tables use shared formatting helpers;
  - Plotly axes use the same separator convention;
  - currency remains in the label or after the value, not as an `EUR` prefix.
- Added or preserved modern dashboard layout with header, tabs, KPI cards, charts, and tables.
- Confirmed `render_insight_cards()` uses `st.columns()` and renders each HTML card separately.
- Improved insight-card text wrapping and mobile card sizing.
- Improved some Insights wording for business users.
- Added a short caveat under daily-vs-monthly break-even.
- Fixed an Insights crash after the `api_*` cutover: yield cards now skip
  all-null yield metrics instead of calling `idxmax()` on all-NA values.
- Fixed public API layer refresh: `refresh_gold_estate()` and
  `refresh_gold_rent()` now also maintain the `api_*` tables after refreshing
  Gold.
- Added public API v1 documentation and a SQL health-check for the public API
  layer.
- Added the first Silver-powered public API table for sale segments by rooms
  and area band.
- Connected `api_estate_segments_current` to the For Sale dashboard tab.
- Restyled the For Sale segment charts to match the quieter horizontal bar
  style used by the main sector charts.
- Added dashboard UX/UI standards to `AGENTS.md` so future UI work keeps the
  same modern, polished, analytics-focused design direction.
- Ran a focused UI polish pass for chart/container consistency across the
  dashboard.
- Promoted room and area controls into the left filter panel as a For Sale
  profile filter:
  - For Sale KPI cards, rankings, segment charts, and the sector table now use
    the selected room/area profile when it is active;
  - profile-filtered sale metrics are rebuilt from `api_estate_segments_current`
    with listing-weighted aggregation back to city-sector grain;
  - the 90-day sale trend stays overall-only because profile-level history is
    not available in the current public API layer.
- Added the next public API layer step for profile-level sale history:
  - new SQL script `sql/add_estate_segments_daily_api_layer.sql` creates
    `api_estate_segments_daily`;
  - `refresh_gold_estate()` now maintains profile daily snapshots through the
    new script;
  - `sql/check_public_api_layer.sql` verifies the new table, access model, and
    refresh-function marker;
  - `docs/public_api_v1.md` documents the new public API table and example
    request.
- Connected optional `api_estate_segments_daily` loading in the dashboard:
  - when room/area filters are active, For Sale can render a profile-level
    90-day trend once enough daily snapshots exist;
  - before the SQL table exists or before enough snapshots accumulate, the app
    stays up and shows a clear empty state.
- Applied `sql/add_estate_segments_daily_api_layer.sql` to Supabase production
  on 2026-07-30 and ran `select public.refresh_gold_estate();`:
  - `api_estate_segments_daily` exists with RLS enabled;
  - latest profile-history snapshot is 2026-07-29 with 279 aggregated rows;
  - `anon` and `authenticated` can read the table and cannot write to it;
  - public API parity/access/function checks returned `OK`.
- Added `dashboard_theme.py` as the first shared UI theme source for CSS variables,
  Plotly chart styling, and named chart color scales.
- Replaced the one-off For Sale high-price red palette with a named
  `HIGH_PRICE_COLOR_SCALE`.
- Added `pandas>=2.2,<3` explicitly to `requirements.txt`.
- Added a shared `fetch_paginated_rows()` helper so the historical sale and
  profile-history loaders use one Supabase pagination path.
- Moved Supabase client creation, cached data loaders, API column contracts, and
  pagination helper from `app.py` into `dashboard_data.py`.
- Moved pure pandas transformation helpers from `app.py` into
  `dashboard_transforms.py`:
  freshness, weighted averages, city/profile filters, segment summaries, and
  profile-to-market aggregation.
- Moved shared Plotly chart helpers from `app.py` into `dashboard_charts.py`:
  `PLOTLY_CHART_CONFIG`, `render_plotly_chart()`, and
  `apply_common_chart_style()`.
- Moved ranked/listing/price chart sections from `app.py` into `dashboard_charts.py`
  and removed the temporary callback plumbing by introducing
  `dashboard_components.py`.
- Replaced the inline Daily Rent high-price purple palette with named
  `HIGH_DAILY_RENT_COLOR_SCALE`.
- Moved shared UI primitives `render_section()`, `render_empty_state()`, and
  `render_chart_title()` from `app.py` into `dashboard_components.py`.
- Moved shared card/header UI helpers `format_int()`, `render_app_header()`,
  `render_kpi_card()`, and `render_insight_cards()` from `app.py` into
  `dashboard_components.py`.
- Renamed `charts.py` to `dashboard_charts.py` to avoid a Streamlit Cloud
  import crash with `KeyError: 'charts'`.
- Renamed remaining generic helper modules to `dashboard_components.py`,
  `dashboard_data.py`, `dashboard_theme.py`, and `dashboard_transforms.py` after
  Streamlit Cloud also crashed on `KeyError: 'components'`.
- Replaced `pd.Timedelta(days=HISTORY_WINDOW_DAYS)` with explicit
  `pd.Timedelta(HISTORY_WINDOW_DAYS, unit="D")` in trend filters.
- Added a dashboard-style data-loading error state:
  - public users see a calm connection message instead of technical exception
    text;
  - technical details are shown only when `IMOBIL_DEBUG_ERRORS=1` is set.
- Kept the data-loading error renderer in `app.py` after local visual testing
  exposed a Streamlit hot-reload import cache issue with new helpers added to
  `dashboard_components.py`.
- Local Streamlit and Supabase loading were user-verified as working on
  2026-07-31 after the Python 3.14 / `.venv` recovery.

## Important Verified Semantics

- Data freshness should use the latest Gold snapshot date.
- Market average price per m2 should be weighted by `listings`.
- Yield values should be described as indicative gross yield.

## Current Verification

- `app.py`, `dashboard_charts.py`, `dashboard_components.py`,
  `dashboard_data.py`, `dashboard_theme.py`, and `dashboard_transforms.py`
  syntax passed in the project `.venv` using:

```powershell
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m py_compile app.py dashboard_charts.py dashboard_components.py dashboard_data.py dashboard_theme.py dashboard_transforms.py
```

- Ruff passed in the project `.venv` using:

```powershell
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m ruff check app.py dashboard_charts.py dashboard_components.py dashboard_data.py dashboard_theme.py dashboard_transforms.py
```

- Streamlit visual verification was not completed in the Codex sandbox.
- On 2026-07-31 the app started locally with Python 3.14.6 after recreating
  `.venv`; the page reached the dashboard data-loading state without import
  errors. Supabase data loading could not be completed in the Codex runtime
  because outbound socket access was denied (`WinError 1013`), so a full local
  visual check still needs a normal user terminal/browser environment.
- The user later confirmed the app works locally with Supabase in a normal
  terminal/browser environment.
- Supabase public API health was checked again on 2026-07-31 through the
  Supabase connector:
  - project `estate-md` is `ACTIVE_HEALTHY` on Postgres 17.6;
  - `api_estate_current`, `api_estate_daily`, `api_estate_segments_current`,
    `api_estate_segments_daily`, `api_rent_current`, and `api_rent_daily`
    all have max snapshot date 2026-07-31;
  - `api_rent_yield` has 76 rows and was refreshed on 2026-07-31;
  - public API table access checks passed for 7 of 7 tables;
  - internal raw/bronze/silver/Gold objects are closed for public roles;
  - `refresh_gold_estate()` and `refresh_gold_rent()` still report `OK`;
  - Supabase Security Advisor has no ERROR/WARN items, only expected INFO
    notices for closed internal tables with RLS enabled and no policies.
- Added a small mobile layout polish pass:
  - Streamlit column rows stack into one column on narrow screens;
  - main tabs wrap into a compact two-by-two layout;
  - header, cards, empty states, and data-loading error states use tighter
    mobile spacing;
  - card minimum heights relax on mobile to avoid awkward empty space.
- The user visually confirmed the dashboard looks good on both phone and
  desktop after the mobile layout polish.
- Added `scripts/check_api_health.py` as a simple local smoke-check for
  `.streamlit/secrets.toml`, Supabase client creation, and public `api_*`
  table freshness without starting Streamlit.
- Ran `scripts/check_api_health.py` successfully on 2026-07-31:
  all 7 public API tables returned `OK`, with sale/rent snapshots at
  2026-07-31 and `api_rent_yield` refreshed on 2026-07-31.
- Designed the next public API feature: a current `New build vs resale` sale
  comparison based on `silver_estate.housing_type`.
  - The field is 99.8% populated under the existing sale-quality rules and has
    two clean values: `Новострой` and `Вторичный`.
  - The planned aggregated-only table is
    `api_estate_housing_type_current`, grouped by date, municipality, city,
    sector, and housing type, with a minimum of five listings per group.
  - The first dashboard release will be a For Sale comparison block, not a
    new global filter or history series.
- Implemented the current `New build vs resale` feature on 2026-07-31:
  - added `api_estate_housing_type_current`, an aggregated public table by
    snapshot date, municipality, city, sector, and `housing_type`;
  - added RLS, read-only public SELECT access, no public writes, and the
    `api_estate_housing_type_city_type_idx` lookup index;
  - updated `refresh_gold_estate()` and ran it successfully after deployment;
  - extended the public API documentation, SQL health-check, and local API
    smoke-check;
  - connected a compact `New build vs resale` comparison to the For Sale tab.
- Designed the next Silver-powered public feature: `Finish & condition`.
  - `apartment_condition` needs canonical mapping before publication because
    its raw values mix finish/condition with construction-stage statuses and
    contain a few Latin/Cyrillic lookalike typos.
  - The first release will publish five normalized groups in a current,
    aggregated-only `api_estate_condition_current` table.
  - The planned For Sale UI is one horizontal comparison chart; it will share
    city and minimum-listings filters but stay independent of Rooms/Area.
- Implemented `Finish & condition` on 2026-07-31:
  - added `api_estate_condition_current`, an aggregated public table by
    snapshot date, municipality, city, sector, and normalized condition group;
  - normalized five publishable groups while excluding construction-stage
    statuses from the first public release;
  - added RLS, read-only public SELECT access, no public writes, and the
    `api_estate_condition_city_group_idx` lookup index;
  - updated `refresh_gold_estate()`, ran it successfully, and verified 136
    current aggregates across all five groups;
  - extended the public API documentation, SQL health-check, and local API
    smoke-check;
  - connected one full-width `Finish & condition` comparison chart to For Sale.
- Implemented `Floor position` on 2026-07-31:
  - added `api_estate_floor_position_current`, an aggregated public table by
    snapshot date, municipality, city, sector, and floor position;
  - classified valid floor pairs into `Ground floor`, `Middle floor`, and
    `Top floor`, with one-floor buildings included in `Ground floor`;
  - added RLS, read-only public SELECT access, no public writes, and the
    `api_estate_floor_position_city_idx` lookup index;
  - updated `refresh_gold_estate()` without removing existing public API
    refresh blocks, then ran it successfully;
  - verified 158 current aggregates, all three groups, matching Gold freshness,
    public access rules, and fixed `search_path`;
  - extended the public API documentation, SQL health-check, local API
    smoke-check, and the For Sale dashboard.
- Accepted the current public API and For Sale product release on 2026-07-31:
  - the new housing type, finish/condition, and floor-position blocks were
    visually verified in a normal browser;
  - the changes were committed by the user;
  - the scheduled pipeline is considered healthy and current for this release.
- Supabase production verification on 2026-07-30:
  - `api_estate_segments_daily`: 279 rows, max date 2026-07-29.
  - `api_estate_segments_current`: 279 rows, max date 2026-07-29.
  - Public API table access model: all `api_*` tables returned `OK`.
  - Internal raw/bronze/silver/Gold objects returned `OK` for public access
    being closed.
  - `refresh_gold_estate()` now updates `api_estate_segments_current`,
    `api_estate_segments_daily`, and `api_rent_yield` with fixed
    `search_path=public, pg_temp`.
- Supabase production verification on 2026-07-31 for the new housing-type API:
  - `api_estate_housing_type_current`: 125 rows, snapshot date 2026-07-31;
  - public rows contain only `Новострой` and `Вторичный` aggregates;
  - `anon` and `authenticated` can read but cannot write;
  - `refresh_gold_estate()` has the new refresh block and fixed search path;
  - `sql/check_public_api_layer.sql` returned `OK` for refresh-function
    wiring; the local smoke-check returned `OK` for all 8 public API tables;
  - Security Advisor has no ERROR/WARN items. Existing performance warnings
    about duplicate indexes predate this feature; the new index is only an
    expected `unused_index` INFO notice immediately after creation.
- Codex could not visually load the new dashboard block because its isolated
  Streamlit process has no outbound Supabase socket access. The public API
  smoke-check passed; final visual confirmation belongs in the normal local
  terminal/browser environment where Supabase was previously user-verified.

## Database Inspection Snapshot

Read-only Supabase inspection on 2026-07-28 found:

- Project: `estate-md`, Postgres 17, active and healthy.
- Main public objects:
  - `raw_links`: 33,551 rows.
  - `bronze_estate`: 33,370 rows.
  - `silver_estate`: 33,370 rows.
  - `gold_estate_daily`: 3,080 rows, 2026-06-15 to 2026-07-28.
  - `gold_rent_daily`: 2,276 rows, 2026-06-15 to 2026-07-28.
  - `gold_estate_current`: materialized view, 91 rows for 2026-07-28.
  - `gold_rent_current`: materialized view, 55 rows for 2026-07-28.
  - `gold_rent_yield`: view, 74 rows.
  - `pipeline_runs`: 9 rows; latest runs show `gold_refreshed=true`.
- Silver already contains useful product fields: city, sector, street, rooms,
  total area, floor, total floors, housing type, condition, amenities, developer,
  layout, bathroom count, balcony/loggia, and parking.
- Strongest ready-to-use Silver fields by coverage:
  - city, sector, street, area, housing type, floor, total floors: about 99%.
  - rooms: about 97%.
  - apartment condition: about 77%.
  - bathroom count: about 70%.
  - balcony/loggia: about 58%.
  - parking: about 48%.
- Supabase advisors reported security items to review before making the app a
  broader public platform:
  - RLS enabled with no policies on several tables.
  - `gold_rent_yield` was flagged as a security-definer view; fixed on
    2026-07-28 by setting `security_invoker = true`.
  - `gold_estate_current` and `gold_rent_current` materialized views are exposed
    through the Data API.
  - `refresh_gold_estate` and `refresh_gold_rent` were flagged for mutable
    `search_path`; fixed on 2026-07-28 with `search_path=public, pg_temp`.
- Public API layer planning started on 2026-07-28:
  - SQL draft created at `sql/public_api_layer.sql`.
  - The draft exposes only aggregated `api_*` tables.
  - It keeps current dashboard safety by requiring app cutover before revoking
    public SELECT from internal Gold objects.
  - `api_*` tables were created and verified with expected row counts.
  - `app.py` now reads `api_estate_current`, `api_rent_current`,
    `api_rent_yield`, and `api_estate_daily`.
  - Streamlit dashboard was reported working after the `api_*` cutover.
  - `sql/revoke_internal_public_access.sql` was applied on 2026-07-29.
  - Public roles can now read only `api_*`; internal raw/bronze/silver/Gold
    objects are no longer selectable by `anon` or `authenticated`.
  - Security Advisor has no remaining ERROR/WARN items; only INFO notices remain
    for RLS-enabled internal tables with no policies.
  - Deployed Streamlit dashboard was reported working after the internal access
    revoke on 2026-07-29.
  - `sql/refresh_gold_updates_api_layer.sql` was added and applied on
    2026-07-29.
  - `refresh_gold_estate()` now refreshes `gold_estate_current`, upserts
    `gold_estate_daily`, refreshes `api_estate_current`, upserts
    `api_estate_daily`, and refreshes `api_rent_yield`.
  - `refresh_gold_rent()` now refreshes `gold_rent_current`, upserts
    `gold_rent_daily`, refreshes `api_rent_current`, upserts `api_rent_daily`,
    and refreshes `api_rent_yield`.
  - After running both refresh functions, `api_estate_current`,
    `api_estate_daily`, `api_rent_current`, and `api_rent_daily` were verified
    at snapshot date 2026-07-29.
  - Both refresh functions were also verified under `service_role`, matching
    the expected pipeline RPC role.
  - Supabase Security Advisor still has no ERROR/WARN items after the function
    update; only the same INFO notices remain for closed internal tables.
  - `docs/public_api_v1.md` documents the public API contract, exposed tables,
    field meanings, example REST requests, refresh contract, and access rules.
  - `sql/check_public_api_layer.sql` was added and verified against Supabase.
    It checks Gold/API freshness, row parity, public RLS/grants, closed
    internal objects, and refresh-function wiring.
  - `sql/add_estate_segments_api_layer.sql` was added and applied on
    2026-07-29.
  - `api_estate_segments_current` exposes aggregated sale metrics by
    `rooms_group` and `area_band`; it publishes only groups with at least 5
    listings.
  - The segment table was verified with 279 rows for snapshot date 2026-07-29,
    representing 21,918 sale listings.
  - `refresh_gold_estate()` was verified under `service_role` after adding the
    segment refresh block.
  - Supabase Security Advisor still has no ERROR/WARN items after adding the
    segment API table; only the same INFO notices remain for closed internal
    tables.
  - `app.py` now loads `api_estate_segments_current` and shows a For Sale
    "Prices by home profile" block with listing-weighted EUR/m2 charts by
    rooms and area band.
  - The segment charts were adjusted from default vertical blue bars to
    horizontal neutral bars with one sale-color accent, matching the existing
    dashboard chart style more closely.
  - `AGENTS.md` now includes dashboard UX/UI standards covering modern visual
    quality, consistency with existing charts/cards, muted colors, direct
    labels, mobile usability, and honest visual verification.
  - `app.py` now uses a shared Plotly chart renderer with modebar hidden and
    responsive config.
- Streamlit border containers, sidebar filter controls, metric cards, and
  small chart titles were lightly restyled for a more consistent dashboard
  surface.
- The For Sale profile block now has local `Rooms` and `Area` filters that
  affect only the room/area profile charts, preserving the existing global
  dashboard filters.
- Ran a small Ponytail/Data Visualization UI revision pass:
  - removed unused dashboard CSS;
  - kept Plotly charts on a quieter shared config;
  - made ranked chart hover values show clear business units;
  - made yield chart hover text match the rest of the dashboard;
  - made the profile-chart accent highlight independent of DataFrame index
    labels.
- Started a more memorable real-estate intelligence shell inspired by the
  Parcelia reference without copying its map-first structure:
  - upgraded the app header into a stronger product header;
  - added a compact active market lens bar above the main tabs;
  - restyled the Explore area as a control panel while preserving the existing
    filters and presets.
- Fixed the first visual feedback from that shell pass:
  - removed the heavy "Control panel" eyebrow from the Explore block;
  - added stable spacing between multi-row insight cards so cards do not touch
    or overlap.
- Normalized shared dashboard cards after visual review:
  - insight cards now use a consistent minimum height across a row;
  - KPI cards use a stronger fixed rhythm;
  - the daily-vs-monthly context callout has a clear gap before the cards below.
- Reworked the dashboard visual system and color palette for a calmer
  real-estate intelligence feel:
  - replaced the default blue/slate Streamlit feel with a sage, stone, and
    deep green-ink interface palette;
  - refreshed sale, rent, daily rent, yield, neutral, and trend chart colors
    with clearer semantic roles;
  - aligned Plotly fonts, hover labels, gridlines, tabs, controls, cards,
    header, workspace bar, and footer with the new palette.
- Cleaned up empty Insights sections:
  - removed the decorative "Insight center" group heading;
  - `Daily vs monthly break-even` now renders only when matching monthly and
    daily rent city-sector pairs exist;
  - yield opportunity notes now stay hidden when no yield card can be built.
- Polished the main tab control:
  - added breathing room below the tab toolbar;
  - removed the default Streamlit tab underline that made tabs feel stuck to
    the content divider.
- Reworked the tab toolbar from a floating compact pill into a full-width
  navigation row that belongs to the main dashboard workspace.
- Removed the redundant workspace summary bar (`Scope`, `Active lens`,
  `Liquidity`, `Snapshot`) because it duplicated the header, filters, and
  market summary while making the top layout feel crowded.
- Ran a final top-layout/card QA pass:
  - increased the gap between the Explore filter panel and the main dashboard;
  - tightened section rhythm after the header and tab toolbar changes;
  - unified dashboard card shadows and flex layout for KPI and insight cards.

## Current Work

- Added data-loader regression coverage for public API pagination and the
  intentional difference between required history errors and the optional
  profile-history fallback. Local unit tests, compilation, and Ruff pass.
- Completed browser QA of the restored Explore panel at desktop and 390px mobile
  widths. The panel remains visible, controls are reachable, and selected
  multi-select values now use the dashboard text colour instead of inheriting
  Streamlit's near-white default.
- Completed browser QA of the reduced Insights hierarchy: `Decision notes`,
  `Weekly market brief`, `Regional value comparison`, and a closed
  `Investment analysis` disclosure render without the previous extra sections.
- Added the native Streamlit light theme in `.streamlit/config.toml` using the
  existing dashboard palette. Selected multi-select tags now use the product
  green rather than Streamlit's default red, so a city selection does not look
  like an error state.
- Ran the read-only public API health check after the parser recovery on
  2026-08-17. All ten `api_*` tables were non-empty and current to 2026-08-17;
  the dashboard also rendered the same snapshot date from its public data.
- Ran a focused control-state QA after applying the native Streamlit theme:
  selected filters and active tabs use the product green rather than the
  default red, and the Explore controls, tabs, and current-market section stay
  reachable at a 390px mobile width. No behaviour change was needed.
- Reduced the initial density of the For Sale tab without removing analytics:
  `New build vs resale`, `Finish & condition`, `Floor position`, and `Prices by
  home profile` now live in one closed `Property characteristics` disclosure
  after the main market and ranking views.
- Reframed the For Sale tab so the existing `Chisinau price pulse` is the
  primary visual story after tab navigation; when a room or area profile is
  active, its matching profile trend appears in that position instead.
- Kept the same filters, public data, and calculations. The current-market
  summary, rankings, budget guide, city comparison, property characteristics,
  and sector table now follow as progressively more detailed analysis.
- Added a regression test for this order. Compilation, Ruff, and all 11 unit
  tests pass; the local Streamlit preview responds at `http://127.0.0.1:8503`.

## Next Small Steps

1. Parser-quality gate work in the pipeline repository is deferred at the
   user's request. Resume it before the next source-parser change.

2. Keep new product ideas in the parking lot until a real user question or a
   data-quality need justifies a single focused addition.

## Parking Lot

- Weekend house index.
- Suburban radar improvements.
- Ideal apartment portrait.
- Future parser fields: rooms, area, floor, house/dacha/land, amenities, distance from Chisinau.
