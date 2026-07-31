# New Build vs Resale: API Design

## Goal

Add a small, public sale-market comparison between new builds (`Новострой`)
and resale homes (`Вторичный`). The first release is a current snapshot only.
It should help a buyer or investor see price and supply differences without
exposing individual listings.

## Data Readiness

Read-only inspection of `silver_estate` on 2026-07-31 used the same sale
quality rules as the existing segment API: successful sale listings, price at
least EUR 1,000, area from 20 to 400 m2, a recent publication date, and a
plausible EUR/m2 range.

| Segment | Eligible listings | Average EUR/m2 |
|---|---:|---:|
| `Новострой` | 15,460 | 2,031 |
| `Вторичный` | 8,091 | 1,643 |

`housing_type` is populated for 23,551 of 23,579 eligible listings (99.9%).
There are only these two meaningful values, so no normalization layer is
needed for this release.

## Public Contract

Create `public.api_estate_housing_type_current` at this grain:

`date + municipality + city + sector + housing_type`

Columns:

| Column | Meaning |
|---|---|
| `date` | Gold/API snapshot date. |
| `municipality`, `city`, `sector` | Market location. |
| `housing_type` | `Новострой` or `Вторичный`. |
| `listings` | Number of qualifying listings in the group. |
| `avg_price_eur`, `median_price_eur` | Sale-price level in EUR. |
| `avg_per_m2_eur` | Average sale price per m2 in EUR. |
| `refreshed_at` | API refresh timestamp. |

Only groups with at least five listings are published. At the inspected
snapshot this keeps 125 stable city-sector groups and 23,253 of 23,551 typed
listings (98.7%).

The table is aggregated-only. It receives RLS, read-only `anon` and
`authenticated` SELECT policies, and no public write permissions, matching the
existing `api_*` layer.

## Dashboard Scope

Add one compact `New build vs resale` comparison in the `For Sale` tab. It
uses the existing city and minimum-listings filters, shows direct values, and
does not change the current Rooms/Area profile filters.

The first release is deliberately a comparison, not another global filter.
Combining housing type with Rooms and Area would require a new multi-dimensional
API contract and would create too many small groups in less liquid cities.

## Implementation Order

1. Add the current aggregate table, index, RLS policy, grants, and refresh
   block to `refresh_gold_estate()`.
2. Extend `sql/check_public_api_layer.sql`, `scripts/check_api_health.py`, and
   `docs/public_api_v1.md`.
3. Verify row count, freshness, public read-only access, internal access
   closure, function wiring, and Supabase advisors.
4. Load the table in the dashboard and add the comparison block.
5. Consider a daily-history table only after enough new snapshots accumulate.
