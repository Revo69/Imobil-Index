# Imobil.Index Public API v1

This document describes the first public data contract for Imobil.Index.

The API exposes only aggregated real estate analytics from Moldova. It does not
expose raw listings, source links, seller data, phone numbers, or internal
Bronze/Silver/Gold tables.

## Base URL

Supabase REST API:

```text
https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1
```

Use the public anon key in the `apikey` and `Authorization` headers. Never use
or publish the `service_role` key in client-side code.

Example headers:

```text
apikey: <SUPABASE_ANON_KEY>
Authorization: Bearer <SUPABASE_ANON_KEY>
```

## Public Tables

| Table | Purpose | Grain |
|---|---|---|
| `api_estate_current` | Current sale market metrics | date + municipality + city + sector |
| `api_estate_daily` | Historical sale market metrics | date + municipality + city + sector |
| `api_estate_segments_current` | Current sale metrics by rooms and area band | date + municipality + city + sector + rooms_group + area_band |
| `api_estate_segments_daily` | Historical sale metrics by rooms and area band | date + municipality + city + sector + rooms_group + area_band |
| `api_estate_housing_type_current` | Current sale metrics by new-build versus resale segment | date + municipality + city + sector + housing_type |
| `api_rent_current` | Current monthly/daily rent metrics | date + municipality + city + sector + deal_type |
| `api_rent_daily` | Historical monthly/daily rent metrics | date + municipality + city + sector + deal_type |
| `api_rent_yield` | Indicative gross rent-yield metrics | city + sector |

## Shared Fields

| Field | Meaning |
|---|---|
| `date` | Market snapshot date. This is the data date, not the request time. |
| `municipality` | Municipality name. Missing source values are published as `Unknown`. |
| `city` | City name. Missing source values are published as `Unknown`. |
| `sector` | City sector/district. Missing source values are published as `Center`. |
| `listings` | Number of listings included in the aggregate. |
| `refreshed_at` | Timestamp when the public API row was refreshed from the internal source layer. |

## Segment Fields

| Field | Meaning |
|---|---|
| `rooms_group` | Room-count group. Current values are `1`, `2`, `3`, and `4+`. |
| `area_band` | Total-area group. Current values are `<40 m2`, `40-59 m2`, `60-79 m2`, `80-119 m2`, and `120+ m2`. |
| `housing_type` | Sale-market segment. Current values are `Новострой` and `Вторичный`. |

## `api_estate_current`

Current sale-market aggregate by date, municipality, city, and sector.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `listings` | bigint | no | Sale listings in this group. |
| `avg_price_eur` | numeric | yes | Average sale listing price in EUR. |
| `median_price_eur` | double precision | yes | Median sale listing price in EUR. |
| `avg_per_m2_eur` | numeric | yes | Average sale price per square meter in EUR. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_estate_daily`

Historical sale-market aggregate with the same business meaning as
`api_estate_current`.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `listings` | integer | yes | Sale listings in this group. |
| `avg_price_eur` | numeric | yes | Average sale listing price in EUR. |
| `median_price_eur` | numeric | yes | Median sale listing price in EUR. |
| `avg_per_m2_eur` | numeric | yes | Average sale price per square meter in EUR. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_estate_segments_current`

Current sale-market aggregate by rooms and area band. It uses the same sale
market filters as `gold_estate_current`, plus `number_of_rooms is not null`.
Only groups with at least 5 listings are published.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `rooms_group` | text | no | Room-count group. |
| `area_band` | text | no | Total-area group. |
| `listings` | bigint | no | Sale listings in this segment. |
| `avg_price_eur` | numeric | yes | Average sale listing price in EUR. |
| `median_price_eur` | numeric | yes | Median sale listing price in EUR. |
| `avg_per_m2_eur` | numeric | yes | Average sale price per square meter in EUR. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_estate_segments_daily`

Historical sale-market snapshots by rooms and area band. It uses the same
business meaning as `api_estate_segments_current`, but stores one row per
snapshot date so profile-level trends can be queried over time.

This history starts when `sql/add_estate_segments_daily_api_layer.sql` is
applied. Older profile snapshots are not backfilled from `publication_date`
because that would change the meaning from market snapshot history to listing
publication history.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `rooms_group` | text | no | Room-count group. |
| `area_band` | text | no | Total-area group. |
| `listings` | bigint | no | Sale listings in this segment. |
| `avg_price_eur` | numeric | yes | Average sale listing price in EUR. |
| `median_price_eur` | numeric | yes | Median sale listing price in EUR. |
| `avg_per_m2_eur` | numeric | yes | Average sale price per square meter in EUR. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_estate_housing_type_current`

Current sale-market aggregate by new-build versus resale segment. It uses the
same sale-market quality filters as the existing public sale-profile API.
Only groups with at least 5 listings are published.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `housing_type` | text | no | `Новострой` or `Вторичный`. |
| `listings` | bigint | no | Sale listings in this segment. |
| `avg_price_eur` | numeric | yes | Average sale listing price in EUR. |
| `median_price_eur` | numeric | yes | Median sale listing price in EUR. |
| `avg_per_m2_eur` | numeric | yes | Average sale price per square meter in EUR. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_rent_current`

Current rent-market aggregate by date, municipality, city, sector, and deal
type.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `deal_type` | text | no | Rent market type, for example monthly or daily rent. |
| `listings` | bigint | no | Rent listings in this group. |
| `avg_price_eur` | numeric | yes | Average rent price in EUR. |
| `median_price_eur` | numeric | yes | Median rent price in EUR. |
| `avg_price_per_m2_eur` | numeric | yes | Average rent price per square meter in EUR. |
| `median_price_per_m2_eur` | numeric | yes | Median rent price per square meter in EUR. |
| `avg_area_m2` | numeric | yes | Average listing area in square meters. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_rent_daily`

Historical rent-market aggregate with the same business meaning as
`api_rent_current`.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `date` | date | no | Snapshot date. |
| `municipality` | text | no | Municipality. |
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `deal_type` | text | no | Rent market type. |
| `listings` | integer | yes | Rent listings in this group. |
| `avg_price_eur` | numeric | yes | Average rent price in EUR. |
| `median_price_eur` | numeric | yes | Median rent price in EUR. |
| `avg_price_per_m2_eur` | numeric | yes | Average rent price per square meter in EUR. |
| `median_price_per_m2_eur` | numeric | yes | Median rent price per square meter in EUR. |
| `avg_area_m2` | numeric | yes | Average listing area in square meters. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## `api_rent_yield`

Indicative gross yield by city and sector. Yield values are calculated before
full operating costs such as utilities, maintenance, vacancy, cleaning, taxes,
platform fees, and management costs.

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `city` | text | no | City. |
| `sector` | text | no | Sector or district. |
| `yield_monthly_percent` | numeric | yes | Indicative gross annual yield from monthly rent. |
| `yield_daily_percent` | numeric | yes | Indicative gross annual yield from daily rent at the current model assumption. |
| `annual_rent_monthly` | numeric | yes | Estimated annual rent from monthly rent. |
| `annual_rent_daily_60pct` | numeric | yes | Estimated annual rent from daily rent at 60% occupancy. |
| `avg_sale_price_eur` | numeric | yes | Average sale price used in the yield calculation. |
| `total_rent_listings` | numeric | yes | Rent listing count used in the calculation. |
| `sale_listings` | numeric | yes | Sale listing count used in the calculation. |
| `refreshed_at` | timestamptz | no | API refresh timestamp. |

## Example Requests

Current sale metrics for Chisinau:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_estate_current?city=eq.%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D1%91%D0%B2&select=date,city,sector,listings,avg_per_m2_eur" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

Top daily-rent yield sectors:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_rent_yield?select=city,sector,yield_daily_percent,sale_listings,total_rent_listings&order=yield_daily_percent.desc.nullslast&limit=10" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

Current sale prices by rooms and area band:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_estate_segments_current?city=eq.%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D1%91%D0%B2&rooms_group=eq.2&select=date,city,sector,rooms_group,area_band,listings,avg_per_m2_eur&order=listings.desc" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

Current new-build versus resale sale metrics:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_estate_housing_type_current?city=eq.%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D1%91%D0%B2&select=date,city,sector,housing_type,listings,avg_per_m2_eur&order=listings.desc" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

90-day sale price history for one city:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_estate_daily?city=eq.%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D1%91%D0%B2&select=date,sector,avg_per_m2_eur,listings&order=date.asc" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

90-day sale price history for one room/area profile:

```bash
curl "https://tfwfvdbatsdncyoibzxp.supabase.co/rest/v1/api_estate_segments_daily?city=eq.%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D1%91%D0%B2&rooms_group=eq.2&area_band=eq.60-79%20m2&select=date,sector,rooms_group,area_band,listings,avg_per_m2_eur&order=date.asc" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```

## Refresh Contract

Gold remains the source of truth. The public API layer is refreshed by the same
database functions used by the upstream pipeline:

| Function | Public tables maintained |
|---|---|
| `refresh_gold_estate()` | `api_estate_current`, `api_estate_daily`, `api_estate_segments_current`, `api_estate_segments_daily`, `api_estate_housing_type_current`, `api_rent_yield` |
| `refresh_gold_rent()` | `api_rent_current`, `api_rent_daily`, `api_rent_yield` |

After a normal pipeline run, `api_estate_current`, `api_estate_daily`,
`api_estate_segments_current`, `api_estate_segments_daily`,
`api_estate_housing_type_current`, `api_rent_current`, and `api_rent_daily`
should have the latest snapshot date.

## Access Rules

- `anon` and `authenticated` can only read the `api_*` tables.
- Public roles cannot insert, update, delete, or truncate API tables.
- Internal `raw_*`, `bronze_*`, `silver_*`, and Gold objects stay private.
- Row-level security is enabled on public API tables, with read-only SELECT
  policies for `anon` and `authenticated`.

Run `sql/check_public_api_layer.sql` after pipeline or security changes.
