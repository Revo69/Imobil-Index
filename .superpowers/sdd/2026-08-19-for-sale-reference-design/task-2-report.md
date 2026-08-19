# Task 2 report: scoped For Sale visual system

## Outcome

Defined a reusable visual-system contract for the upcoming For Sale reference
layout without rendering or rearranging any dashboard content. The existing
green, off-white, and muted-border design language remains the source of the
new styles.

## Changed files

- `dashboard_theme.py`
  - Added semantic tokens for the dark sale hero, quiet signal rail, shared
    section rhythm, and mobile stack spacing.
  - Exposed those values through `theme_css_vars()` as CSS variables. The new
    colors reuse the existing dark green, white, off-white, and muted-border
    family; no independent palette was introduced.
- `app.py`
  - Replaced the existing section padding literals with the new section-rhythm
    variables.
  - Added an intentionally unused, For Sale-only CSS class contract for Task 3:
    - `.sale-hero`, `.sale-hero-eyebrow`, `.sale-hero-title`,
      `.sale-hero-copy`
    - `.sale-signal-rail`, `.sale-signal`, `.sale-signal-label`,
      `.sale-signal-value`, `.sale-signal-note`
    - `.sale-metric-grid`, `.sale-metric-cell`, `.sale-metric-label`,
      `.sale-metric-value`, `.sale-metric-note`
    - `.sale-section`
  - The signal rail and metric grid stack to one column at the existing
    `760px` mobile breakpoint. Existing Streamlit widget and selected-tab
    styles were left unchanged.

## Scope and compatibility review

- No For Sale markup, tab ordering, visible copy, data variables, filter keys,
  callbacks, loaders, API calls, transformations, or calculations changed.
- No dark styling was applied to Monthly Rent, Daily Rent, or Insights; every
  new presentation selector is `sale-*` scoped.
- The left `Explore market` control area remains untouched.
- The CSS uses no external font, package, or JavaScript.
- A source-level CSS test was deliberately not added: it would only assert
  selector names or color literals and would be a brittle change detector,
  rather than exercising user-visible behavior. The next task will consume the
  class contract through real For Sale markup.

## Verification

Commands run from the project root with the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_reference_design_contract -v
```

Result: `Ran 4 tests ... OK`.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Result: `Ran 19 tests ... OK`. Streamlit emitted normal bare-mode cache and
missing-script-context warnings while data-loader tests ran; no test failed.

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py dashboard_theme.py
.\.venv\Scripts\python.exe -m ruff check app.py dashboard_theme.py
git diff --check
```

Result: compilation, Ruff, and whitespace checks passed.

## Visual verification

No Streamlit server or browser was opened for this task. The new For Sale
selectors have no consuming markup yet, so a visual change is not expected
until Task 3. Desktop and mobile screenshot verification remains required
after that integration.

## Self-review

- Confirmed the production diff is limited to `app.py` CSS and
  `dashboard_theme.py` tokens.
- Confirmed no `load_*`, `filter_*`, `build_*`, or `weighted_average` code was
  modified.
- Confirmed the new class names are semantic and scoped, so Task 3 does not
  need to couple its markup to Streamlit internal selectors.
