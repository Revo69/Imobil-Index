# AGENTS.md

Project guide for AI-assisted work on Imobil.Index.

## Project Snapshot

- App: Streamlit dashboard for Moldova real estate analytics.
- Main file: `app.py`.
- Data source: Supabase Gold tables:
  - `gold_estate_current`
  - `gold_rent_current`
  - `gold_rent_yield`
  - `gold_estate_daily`
- Runtime stack: Python, Streamlit, Plotly, Supabase Python client.

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

- `Data as of` must come from the latest Gold snapshot date, not the current clock time.
- Average market price per m2 must be weighted by `listings`.
- Do not average city-sector aggregates equally when the UI claims to show market average.
- Do not expose Supabase service keys or secrets.

## New Feature Standard

Before adding a feature to the UI, Python backend, or Supabase schema:

1. Check current syntax and official documentation for the installed runtime,
   Streamlit, Plotly, Supabase, and PostgreSQL features being used. Do not rely
   only on remembered APIs or deprecated examples.
2. Inspect the existing app patterns, data grain, public API contract, and
   database schema before designing the change.
3. Keep the design small: state the user goal, scope of each control, data
   source, and the intended empty/error state before implementation.
4. For UI, follow the existing design system, keep controls in a consistent
   control area, make values readable without hover, and verify desktop and
   mobile layouts when possible.
5. For database changes, use the Supabase skill and current PostgreSQL/Supabase
   guidance. Define the grain, minimum privacy threshold, indexes, constraints,
   RLS, public access rules, refresh wiring, and rollback-safe migration path.
6. In PostgreSQL functions, write `DELETE ... WHERE TRUE` when an intentional
   full-table delete is required. Keep a specific predicate for conditional
   deletes.
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
