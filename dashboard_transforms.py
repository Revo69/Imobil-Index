from collections.abc import Iterable

import pandas as pd


def sector_label(df: pd.DataFrame) -> pd.Series:
    return df["city"].astype(str) + " -> " + df["sector"].fillna("Center").astype(str)


def place_label(row: pd.Series) -> str:
    sector = row.get("sector")
    sector = sector if pd.notna(sector) and str(sector).strip() else "Center"
    return f"{row['city']} -> {sector}"


def weighted_average(df: pd.DataFrame, price_col: str) -> float:
    total_listings = df["listings"].sum()
    if total_listings <= 0:
        return 0.0
    return float((df[price_col] * df["listings"]).sum() / total_listings)


def latest_data_date(df: pd.DataFrame) -> pd.Timestamp | None:
    if df.empty or "date" not in df.columns:
        return None
    data_date = pd.to_datetime(df["date"], errors="coerce").max()
    if pd.isna(data_date):
        return None
    return data_date


def data_freshness(df: pd.DataFrame) -> str:
    data_date = latest_data_date(df)
    if data_date is None:
        return "No snapshot"
    return f"Data as of {data_date:%d %B %Y}"


def build_segment_summary(
    df_segments: pd.DataFrame,
    group_col: str,
    category_order: list[str],
) -> pd.DataFrame:
    required = {group_col, "listings", "avg_per_m2_eur"}
    if df_segments.empty or not required.issubset(df_segments.columns):
        return pd.DataFrame()

    work = df_segments.dropna(subset=[group_col, "listings", "avg_per_m2_eur"]).copy()
    if work.empty:
        return work

    work["listings"] = pd.to_numeric(work["listings"], errors="coerce")
    work["avg_per_m2_eur"] = pd.to_numeric(work["avg_per_m2_eur"], errors="coerce")
    work = work.dropna(subset=["listings", "avg_per_m2_eur"])
    work = work[work["listings"] > 0]
    if work.empty:
        return work

    work["weighted_per_m2"] = work["avg_per_m2_eur"] * work["listings"]
    grouped = (
        work.groupby(group_col, as_index=False, observed=True)
        .agg(listings=("listings", "sum"), weighted_per_m2=("weighted_per_m2", "sum"))
        .copy()
    )
    grouped["avg_per_m2_eur"] = grouped["weighted_per_m2"] / grouped["listings"]
    grouped[group_col] = pd.Categorical(
        grouped[group_col].astype(str),
        categories=category_order,
        ordered=True,
    )
    return grouped.sort_values(group_col).drop(columns=["weighted_per_m2"])


def build_city_market_summary(df: pd.DataFrame) -> pd.DataFrame:
    required = {"city", "listings", "avg_price_eur", "avg_per_m2_eur"}
    if df.empty or not required.issubset(df.columns):
        return pd.DataFrame()

    work = df.copy()
    for column in ("listings", "avg_price_eur", "avg_per_m2_eur"):
        work[column] = pd.to_numeric(work[column], errors="coerce")
    work = work.dropna(subset=["city", "listings", "avg_price_eur", "avg_per_m2_eur"])
    work = work[work["listings"] > 0]
    if work.empty:
        return pd.DataFrame()

    work["weighted_price"] = work["avg_price_eur"] * work["listings"]
    work["weighted_per_m2"] = work["avg_per_m2_eur"] * work["listings"]
    grouped = (
        work.groupby("city", as_index=False, observed=True)
        .agg(
            listings=("listings", "sum"),
            weighted_price=("weighted_price", "sum"),
            weighted_per_m2=("weighted_per_m2", "sum"),
        )
        .copy()
    )
    grouped["avg_price_eur"] = grouped["weighted_price"] / grouped["listings"]
    grouped["avg_per_m2_eur"] = grouped["weighted_per_m2"] / grouped["listings"]
    return grouped.drop(columns=["weighted_price", "weighted_per_m2"])


def ordered_segment_options(
    df_segments: pd.DataFrame,
    column: str,
    category_order: list[str],
) -> list[str]:
    if df_segments.empty or column not in df_segments.columns:
        return []

    available = set(df_segments[column].dropna().astype(str).unique())
    ordered = [value for value in category_order if value in available]
    extra = sorted(available - set(ordered))
    return ordered + extra


def has_sale_profile_filters(
    selected_rooms: Iterable[str],
    selected_area_bands: Iterable[str],
) -> bool:
    return bool(list(selected_rooms) or list(selected_area_bands))


def filter_by_city(
    df: pd.DataFrame,
    selected_cities: Iterable[str],
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    selected_cities = list(selected_cities)
    if selected_cities and "city" in filtered.columns:
        filtered = filtered[filtered["city"].isin(selected_cities)]
    return filtered


def filter_sale_profile_segments(
    df_segments: pd.DataFrame,
    selected_rooms: Iterable[str],
    selected_area_bands: Iterable[str],
) -> pd.DataFrame:
    if df_segments.empty:
        return df_segments

    filtered = df_segments.copy()
    selected_rooms = [str(value) for value in selected_rooms]
    selected_area_bands = [str(value) for value in selected_area_bands]

    if selected_rooms and "rooms_group" in filtered.columns:
        filtered = filtered[filtered["rooms_group"].astype(str).isin(selected_rooms)]
    if selected_area_bands and "area_band" in filtered.columns:
        filtered = filtered[
            filtered["area_band"].astype(str).isin(selected_area_bands)
        ]
    return filtered


def build_sale_market_from_segments(df_segments: pd.DataFrame) -> pd.DataFrame:
    required = {
        "date",
        "city",
        "sector",
        "listings",
        "avg_price_eur",
        "avg_per_m2_eur",
    }
    if df_segments.empty or not required.issubset(df_segments.columns):
        return pd.DataFrame()

    work = df_segments.copy()
    work["listings"] = pd.to_numeric(work["listings"], errors="coerce")
    work["avg_price_eur"] = pd.to_numeric(work["avg_price_eur"], errors="coerce")
    work["avg_per_m2_eur"] = pd.to_numeric(
        work["avg_per_m2_eur"], errors="coerce"
    )
    work = work.dropna(
        subset=["date", "city", "listings", "avg_price_eur", "avg_per_m2_eur"]
    )
    work = work[work["listings"] > 0]
    if work.empty:
        return work

    work["weighted_price"] = work["avg_price_eur"] * work["listings"]
    work["weighted_per_m2"] = work["avg_per_m2_eur"] * work["listings"]
    grouped = (
        work.groupby(["date", "city", "sector"], as_index=False, dropna=False)
        .agg(
            listings=("listings", "sum"),
            weighted_price=("weighted_price", "sum"),
            weighted_per_m2=("weighted_per_m2", "sum"),
        )
        .copy()
    )
    grouped["avg_price_eur"] = grouped["weighted_price"] / grouped["listings"]
    grouped["avg_per_m2_eur"] = grouped["weighted_per_m2"] / grouped["listings"]
    return grouped.drop(columns=["weighted_price", "weighted_per_m2"])


def filter_segments_to_market(
    df_segments: pd.DataFrame,
    df_market: pd.DataFrame,
) -> pd.DataFrame:
    key_cols = ["date", "city", "sector"]
    if (
        df_segments.empty
        or df_market.empty
        or not set(key_cols).issubset(df_segments.columns)
        or not set(key_cols).issubset(df_market.columns)
    ):
        return pd.DataFrame()

    market_keys = df_market[key_cols].drop_duplicates()
    return df_segments.merge(market_keys, on=key_cols, how="inner")


def filter_by_city_and_listings(
    df: pd.DataFrame,
    selected_cities: Iterable[str],
    min_listings: int,
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = filter_by_city(df, selected_cities)
    if "listings" in filtered.columns:
        filtered = filtered[filtered["listings"] >= min_listings]
    return filtered


def build_weekly_price_movement(
    historical_data: pd.DataFrame,
    visible_markets: pd.DataFrame,
) -> pd.DataFrame:
    """Compare the latest sale snapshot with a comparable earlier snapshot."""
    history_required = {"date", "city", "sector", "avg_per_m2_eur"}
    market_required = {"city", "sector"}
    if (
        historical_data.empty
        or visible_markets.empty
        or not history_required.issubset(historical_data.columns)
        or not market_required.issubset(visible_markets.columns)
    ):
        return pd.DataFrame()

    markets = visible_markets[["city", "sector"]].drop_duplicates()
    history = historical_data.copy()
    history["date"] = pd.to_datetime(history["date"], errors="coerce")
    history["avg_per_m2_eur"] = pd.to_numeric(
        history["avg_per_m2_eur"], errors="coerce"
    )
    history = history.dropna(subset=["date", "city", "avg_per_m2_eur"])
    history = history.merge(markets, on=["city", "sector"], how="inner")
    if history.empty:
        return pd.DataFrame()

    history = (
        history.sort_values(["date", "city", "sector"])
        .drop_duplicates(["date", "city", "sector"], keep="last")
        .copy()
    )
    latest_date = history["date"].max()
    baseline_candidates = history[history["date"] <= latest_date - pd.Timedelta(days=7)]
    if baseline_candidates.empty:
        return pd.DataFrame()
    baseline_date = baseline_candidates["date"].max()

    latest = history[history["date"] == latest_date][
        ["city", "sector", "avg_per_m2_eur"]
    ].rename(columns={"avg_per_m2_eur": "latest_avg_per_m2_eur"})
    baseline = history[history["date"] == baseline_date][
        ["city", "sector", "avg_per_m2_eur"]
    ].rename(columns={"avg_per_m2_eur": "baseline_avg_per_m2_eur"})
    movement = latest.merge(baseline, on=["city", "sector"], how="inner")
    movement = movement[movement["baseline_avg_per_m2_eur"] > 0].copy()
    if movement.empty:
        return movement

    movement["change_percent"] = (
        (movement["latest_avg_per_m2_eur"] - movement["baseline_avg_per_m2_eur"])
        / movement["baseline_avg_per_m2_eur"]
        * 100
    )
    movement["latest_date"] = latest_date
    movement["baseline_date"] = baseline_date
    movement["days_between"] = (latest_date - baseline_date).days
    return movement.sort_values("change_percent")


def apply_daily_occupancy_assumption(
    yield_data: pd.DataFrame,
    daily_occupancy_percent: int,
) -> pd.DataFrame:
    """Apply the selected occupancy to daily-rent yield metrics."""
    required = {
        "annual_rent_daily_60pct",
        "avg_sale_price_eur",
        "yield_daily_percent",
    }
    if (
        yield_data.empty
        or not required.issubset(yield_data.columns)
        or not 0 < daily_occupancy_percent <= 100
    ):
        return yield_data.copy()

    data = yield_data.copy()
    for column in required:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    valid = (data["annual_rent_daily_60pct"] > 0) & (
        data["avg_sale_price_eur"] > 0
    )
    data["annual_rent_daily_eur"] = pd.NA
    data["yield_daily_percent"] = pd.NA
    data.loc[valid, "annual_rent_daily_eur"] = (
        data.loc[valid, "annual_rent_daily_60pct"]
        / 0.60
        * daily_occupancy_percent
        / 100
    )
    data.loc[valid, "yield_daily_percent"] = (
        data.loc[valid, "annual_rent_daily_eur"]
        / data.loc[valid, "avg_sale_price_eur"]
        * 100
    )
    return data


def build_daily_vs_monthly_return(
    yield_data: pd.DataFrame,
    daily_occupancy_percent: int,
) -> pd.DataFrame:
    """Recalculate daily gross return from the public 60% occupancy model."""
    required = {
        "city",
        "sector",
        "annual_rent_monthly",
        "annual_rent_daily_60pct",
        "avg_sale_price_eur",
        "sale_listings",
        "total_rent_listings",
    }
    if (
        yield_data.empty
        or not required.issubset(yield_data.columns)
        or not 0 < daily_occupancy_percent <= 100
    ):
        return pd.DataFrame()

    data = apply_daily_occupancy_assumption(yield_data, daily_occupancy_percent)
    numeric_columns = [
        "annual_rent_monthly",
        "annual_rent_daily_60pct",
        "avg_sale_price_eur",
        "sale_listings",
        "total_rent_listings",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["city", "sector", *numeric_columns])
    data = data[
        (data["annual_rent_monthly"] > 0)
        & (data["annual_rent_daily_60pct"] > 0)
        & (data["avg_sale_price_eur"] > 0)
    ].copy()
    if data.empty:
        return data

    data["monthly_gross_yield_percent"] = (
        data["annual_rent_monthly"] / data["avg_sale_price_eur"] * 100
    )
    data["daily_gross_yield_percent"] = data["yield_daily_percent"]
    data["daily_advantage_pp"] = (
        data["daily_gross_yield_percent"] - data["monthly_gross_yield_percent"]
    )
    data["occupancy_to_match_monthly_percent"] = (
        data["annual_rent_monthly"]
        / (data["annual_rent_daily_60pct"] / 0.60)
        * 100
    )
    return data.sort_values("daily_advantage_pp", ascending=False)
