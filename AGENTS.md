# AGENTS.md

Project guide for AI-assisted work on Imobil.Index.

## Project Snapshot

- App: Streamlit dashboard for Moldova real estate analytics.
- Main file: `app.py`.
- Data source: the public, aggregated Supabase `api_*` contract loaded by
  `dashboard_data.py`; the dashboard never reads internal Gold objects.
- Runtime stack: Python, Streamlit, Plotly, Supabase Python client.

## Repository Ownership

- This repository owns Streamlit presentation, filters, charts, display
  transformations, consumer-side API checks, and uptime automation.
- `real-estate-analytics-md` owns acquisition, Bronze/Silver/Gold, refresh
  functions, producer SQL, and the canonical `api_*` contract:
  <https://github.com/Revo69/real-estate-analytics-md/blob/main/docs/public_api_v1.md>
- Do not add or maintain producer SQL in this repository. Propose database/API
  changes upstream first, then update this consumer after the contract exists.

## Working Style

- Keep changes small and easy to review.
- Inspect the current file before editing.
- Check `git status` before and after changes.
- Do not rewrite the app structure unless the user explicitly asks.
- Prefer one focused improvement at a time.
- Explain changes in beginner-friendly language.
- Be concise and practical.

## Product Rules

- Keep the left filter panel.
- Do not remove existing tabs or filters.
- Do not break existing business logic.
- Keep the dashboard quiet, clean, and analytics-focused.
- Avoid technical wording in visible UI when a business-friendly phrase works.
- Keep yield wording indicative because it is gross yield before full operating costs.

## Dashboard UX/UI Standards

- The dashboard should feel modern, polished, calm, and analytics-focused.
- New UI blocks must match the existing visual language before they are
  considered done.
- Avoid default-looking Streamlit or Plotly output when it clashes with the app
  style.
- Keep charts visually consistent: spacing, card borders, typography, muted
  colors, and one clear accent.
- Prefer horizontal bar charts for rankings and comparisons when labels are
  long or categorical.
- Use direct labels and visible values where possible; do not rely only on hover.
- Keep layouts scannable on desktop and usable on mobile.
- Do not add a new design style, color system, or chart style for one isolated
  feature.
- Do not simplify or change business logic just to make the UI easier to draw.
- Before finishing a UI change, ask: can a real-estate user understand this in
  about 5 seconds?
- If Streamlit visual verification is unavailable, say so clearly and do not
  claim the UI was visually checked.

## Data Semantics

- `Data as of` must come from the latest public API snapshot date, not the
  current clock time.
- Average market price per m2 must be weighted by `listings`.
- Do not average city-sector aggregates equally when the UI claims to show market average.
- Do not expose Supabase service keys or secrets.

## New Feature Standard

Before adding a feature to the UI, Python backend, or public data contract:

1. Check current syntax and official documentation for the installed runtime,
   Streamlit, Plotly, Supabase, and PostgreSQL features being used. Do not rely
   only on remembered APIs or deprecated examples.
2. Inspect the existing app patterns, data grain, `dashboard_data.py` column
   contracts, and the canonical upstream public API contract before designing
   the change.
3. Keep the design small: state the user goal, scope of each control, data
   source, and the intended empty/error state before implementation.
4. For UI, follow the existing design system, keep controls in a consistent
   control area, make values readable without hover, and verify desktop and
   mobile layouts when possible.
5. Make database, RLS, refresh-function, and producer SQL changes in
   `real-estate-analytics-md`. Define and verify the grain, thresholds, access
   rules, refresh wiring, and compatibility there before changing this app.
6. Do not copy an upstream migration into this repository as a workaround for
   a missing public API field.
7. Run focused checks for the changed surface. Do not claim syntax, schema,
   security, or visual verification unless it was actually performed.
8. Use the applicable skill before implementation:
   - use `supabase:supabase` for every Supabase, PostgreSQL schema, RLS,
     migration, function, or public API change;
   - use `developing-with-streamlit` for every Streamlit UI, layout, widget,
     styling, performance, or deployment change;
   - use a focused design, visualization, testing, or code-review skill when
     the change needs that expertise.
9. If no available skill covers an important part of the task, explain the gap
   and ask the user to connect or install the appropriate skill before taking
   a risky implementation shortcut.
10. Explain the selected approach, trade-offs, and verification in practical
    beginner-friendly language so each change is a learning opportunity.

## Preferred Checks

Run the smallest useful checks after each change:

```powershell
python -m py_compile app.py
python -m ruff check app.py
streamlit run app.py
```

If local Python, Ruff, Streamlit, or Supabase secrets are unavailable, say that clearly.
Do not claim visual verification unless the app was actually opened and checked.

## AI Workflow

1. Read `AGENTS.md`, `PROGRESS.md`, and the relevant part of `app.py`.
2. Identify the next small change.
3. Patch only the files needed for that change.
4. Run available checks.
5. Update `PROGRESS.md` when the status meaningfully changes.
