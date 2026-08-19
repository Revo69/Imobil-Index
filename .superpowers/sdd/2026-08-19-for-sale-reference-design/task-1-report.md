# Task 1 report: visual and semantic baseline

## Changed files

- `tests/test_reference_design_contract.py`
  - Added a source-level contract that `render_app_header(latest_snapshot)`
    occurs exactly once.
  - Added an explicit source-level contract that both For Sale trend paths
    precede `render_market_highlights`.
  - Added snapshot-data coverage for `latest_data_date`, including invalid and
    missing dates.
- No production files, formulas, API/data-loading code, or existing tests were
  changed.

## Verification commands and results

All commands were run from the project root with the project virtual
environment:

```powershell
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m unittest tests.test_reference_design_contract -v
```

Result: `Ran 4 tests ... OK`.

```powershell
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Result: `Ran 19 tests ... OK`. Streamlit emitted its normal bare-mode cache
and missing-script-context warnings while testing data-loader code; no test
failed.

```powershell
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m py_compile tests/test_reference_design_contract.py
C:\Users\123\Documents\Projects\Python\Imobil-Index\.venv\Scripts\python.exe -m ruff check tests/test_reference_design_contract.py
git diff --check
```

Result: all checks passed.

Streamlit and browser screenshots were not run in this task, per the brief;
the controller owns screenshot capture.

## TDD evidence

This task is baseline characterization only. The new tests assert behavior
already present in `app.py` and `dashboard_transforms.py`, so they correctly
pass on their first run; no future/missing behavior was encoded and no
production implementation was added.

## Self-review

- Confirmed the existing weighted-average test was not duplicated.
- Kept assertions source-level and narrow, matching the requested layout
  contracts rather than coupling to rendered Streamlit internals.
- Confirmed UTF-8 source reading for the existing app.
- Confirmed no changes to `app.py`, dashboard modules, API contracts, or
  calculations.
