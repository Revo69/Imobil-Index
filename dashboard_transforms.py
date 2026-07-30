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
