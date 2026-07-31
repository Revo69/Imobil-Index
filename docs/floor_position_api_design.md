# Floor Position: API Design

**Status:** Implemented in production on 2026-07-31.

## Goal

Add a current sale-market comparison by an apartment's position in its building.
It helps a buyer compare the visible price level of ground, middle, and top
floors. It is a comparison signal, not a claim that floor position alone causes
a price difference.

## Data Readiness

Read-only inspection on 2026-07-31 used the existing sale-quality filters.
`floor` and `total_floors` are integer fields, and 23,379 of 23,579 eligible
listings (99.2%) contain a valid positive pair where `total_floors >= floor`.

| Public group | Rule |
|---|---|
| `Ground floor` | `floor = 1` |
| `Middle floor` | `floor >= 2` and `floor < total_floors` |
| `Top floor` | `floor = total_floors` and `floor > 1` |

One-floor buildings are deliberately included in `Ground floor`, keeping the
groups mutually exclusive and the public rule easy to explain.

## Public Contract

`public.api_estate_floor_position_current` uses this grain:

`date + municipality + city + sector + floor_position`

Only city-sector groups with at least five listings are published. The table
contains aggregates only, with RLS, public SELECT access for `anon` and
`authenticated`, and no public writes.

## Dashboard Scope

Add one full-width `Floor position` horizontal bar chart to `For Sale`. It uses
the existing city and minimum-listings filters and stays independent of the
Rooms/Area profile filters and history logic.

The chart caption must state that building height, location, condition, housing
type, and listing mix also affect the visible price differences.

## Verification

- The table contains 158 city-sector aggregates for the 2026-07-31 snapshot.
- All three floor-position groups are present.
- `refresh_gold_estate()` refreshes the table and retains every earlier public
  API refresh block with a fixed search path.
- RLS is enabled; `anon` and `authenticated` can read but cannot write.
- Supabase Security Advisor has no ERROR or WARN findings after the change;
  only existing INFO notices for closed internal tables remain.
