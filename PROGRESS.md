# PROGRESS.md

Simple project progress log for Imobil.Index.

## Last Updated

2026-07-29

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
- Added local room and area filters to the For Sale "Prices by home profile"
  block.

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
- For Sale shows the "Prices by home profile" segment block.
- Rooms and Area filters inside "Prices by home profile" affect only that
  block.
- Left filters affect all tabs.
- Sector details table has no horizontal overflow.
- Header, tabs, and cards look clean on desktop.

3. Watch the next scheduled pipeline run once:

- confirm `api_estate_current` and `api_rent_current` advance together with
  Gold;
- confirm `api_estate_segments_current` advances with the sale refresh;
- confirm the Streamlit header shows the newest snapshot date.
- run `sql/check_public_api_layer.sql` and confirm every status is `OK`.

4. After that, choose only one next improvement:

- polish Insights wording;
- improve mobile layout;
- improve error states;
- add SQL-side filtering for history;
- add new parser/database fields in the upstream project later.
- design the first Silver-powered dashboard feature, such as room filters,
  area bands, floor/condition filters, or amenity premiums.
- choose the first product feature built on the public API or a new aggregated
  Silver-powered API table.

## Parking Lot

- Daily vs monthly rent calculator.
- Weekend house index.
- Suburban radar improvements.
- Ideal apartment portrait.
- Rule-based weekly market notes.
- Future parser fields: rooms, area, floor, house/dacha/land, amenities, distance from Chisinau.
