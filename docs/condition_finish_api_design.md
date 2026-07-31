# Finish & Condition: API Design

**Status:** Implemented in production on 2026-07-31.

## Goal

Add a current sale-market comparison by finish quality and apartment condition.
The feature helps a buyer understand the visible price range between a finished
home, a white-finish unit, and a property that needs renovation. It is a
comparison signal, not a claim that condition alone causes a price difference.

## Data Readiness

Read-only inspection on 2026-07-31 used the same quality filters as the
existing public sale-profile API: successful sale listings, price at least
EUR 1,000, area from 20 to 400 m2, recent publication date, and a plausible
EUR/m2 range.

`silver_estate.apartment_condition` is populated for 19,565 of 23,579 eligible
listings. The raw field also contains construction-stage statuses and a few
Latin/Cyrillic lookalike typos, so it must not be exposed directly.

The first release publishes these normalized groups only:

| Public group | Source values | Publishable listings | City-sector groups |
|---|---|---:|---:|
| `Euro renovation` | `Евроремонт` | 10,566 | 44 |
| `White finish` | `Белый вариант` | 4,841 | 31 |
| `Cosmetic renovation` | `Косметический ремонт` | 1,820 | 28 |
| `Individual design` | `Индивидуальный дизайн` | 590 | 16 |
| `Needs renovation` | `Без ремонта`, `Нуждается в ремонте` | 518 | 17 |

The groups retain 18,887 eligible listings before the city-sector threshold.
Statuses such as incomplete construction, commissioned, and grey finish are
not part of this first comparison because they describe a different stage of a
property or have too little stable supply.

## Public Contract

`public.api_estate_condition_current` uses this grain:

`date + municipality + city + sector + condition_group`

Columns:

| Column | Meaning |
|---|---|
| `date` | Gold/API snapshot date. |
| `municipality`, `city`, `sector` | Market location. |
| `condition_group` | One of the five normalized public groups above. |
| `listings` | Number of qualifying listings in the group. |
| `avg_price_eur`, `median_price_eur` | Sale-price level in EUR. |
| `avg_per_m2_eur` | Average sale price per m2 in EUR. |
| `refreshed_at` | API refresh timestamp. |

Only city-sector groups with at least five listings are published. The table
contains aggregates only, with RLS, public SELECT access for `anon` and
`authenticated`, and no public writes.

## Dashboard Scope

Add one full-width `Finish & condition` horizontal bar chart to the `For Sale`
tab. It uses the existing city and minimum-listings filters, shows direct
EUR/m2 labels, and does not change Rooms/Area filters or their trend logic.

The chart caption must state that visible price differences also reflect
location, area, housing type, and the listing mix.

## Verification

- The table contains 136 city-sector aggregates for the 2026-07-31 snapshot.
- All five normalized groups are present.
- `refresh_gold_estate()` refreshes the table with a fixed search path.
- RLS is enabled; `anon` and `authenticated` can read but cannot write.
- Supabase Security Advisor has no ERROR or WARN findings after the change;
  only existing INFO notices for closed internal tables remain.
