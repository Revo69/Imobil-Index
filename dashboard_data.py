from datetime import UTC, datetime, timedelta

import pandas as pd
import streamlit as st
from supabase import create_client

HISTORY_WINDOW_DAYS = 90
HISTORY_SALE_COLUMNS = "date,city,sector,avg_per_m2_eur"
HISTORY_SALE_SEGMENT_COLUMNS = (
    "date,city,sector,rooms_group,area_band,listings,avg_price_eur,avg_per_m2_eur"
)
ESTATE_SEGMENT_COLUMNS = (
    "date,city,sector,rooms_group,area_band,listings,avg_price_eur,avg_per_m2_eur"
)
ESTATE_HOUSING_TYPE_COLUMNS = (
    "date,city,sector,housing_type,listings,avg_price_eur,median_price_eur,avg_per_m2_eur"
)
ESTATE_CONDITION_COLUMNS = (
    "date,city,sector,condition_group,listings,avg_price_eur,median_price_eur,avg_per_m2_eur"
)
ESTATE_FLOOR_POSITION_COLUMNS = (
    "date,city,sector,floor_position,listings,avg_price_eur,median_price_eur,avg_per_m2_eur"
)


@st.cache_resource
def get_supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def fetch_paginated_rows(
    table_name: str,
    columns: str,
    cutoff: str,
    page_size: int = 1000,
) -> list[dict]:
    supabase = get_supabase_client()
    rows = []
    offset = 0

    while True:
        resp = (
            supabase.table(table_name)
            .select(columns)
            .gte("date", cutoff)
            .range(offset, offset + page_size - 1)
            .order("date", desc=False)
            .execute()
        )

        batch = resp.data
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    return rows


@st.cache_data(ttl=3600)
def load_historical_data() -> pd.DataFrame:
    """
    Loads only the last HISTORY_WINDOW_DAYS of sale history, filtered at the
    database level, since that's all the 90-day trend chart uses.
    """
    cutoff = (datetime.now(UTC) - timedelta(days=HISTORY_WINDOW_DAYS)).strftime(
        "%Y-%m-%d"
    )
    return pd.DataFrame(
        fetch_paginated_rows("api_estate_daily", HISTORY_SALE_COLUMNS, cutoff)
    )


@st.cache_data(ttl=3600)
def load_historical_segment_data() -> pd.DataFrame:
    """
    Loads profile-level sale history when the optional public API table exists.
    The dashboard keeps working while the table is being rolled out.
    """
    cutoff = (datetime.now(UTC) - timedelta(days=HISTORY_WINDOW_DAYS)).strftime(
        "%Y-%m-%d"
    )
    try:
        rows = fetch_paginated_rows(
            "api_estate_segments_daily", HISTORY_SALE_SEGMENT_COLUMNS, cutoff
        )
    except Exception:  # noqa: BLE001
        return pd.DataFrame()
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    supabase = get_supabase_client()
    sales = pd.DataFrame(
        supabase.table("api_estate_current").select("*").execute().data
    )
    sale_segments = pd.DataFrame(
        supabase.table("api_estate_segments_current")
        .select(ESTATE_SEGMENT_COLUMNS)
        .execute()
        .data
    )
    sale_housing_types = pd.DataFrame(
        supabase.table("api_estate_housing_type_current")
        .select(ESTATE_HOUSING_TYPE_COLUMNS)
        .execute()
        .data
    )
    sale_conditions = pd.DataFrame(
        supabase.table("api_estate_condition_current")
        .select(ESTATE_CONDITION_COLUMNS)
        .execute()
        .data
    )
    sale_floor_positions = pd.DataFrame(
        supabase.table("api_estate_floor_position_current")
        .select(ESTATE_FLOOR_POSITION_COLUMNS)
        .execute()
        .data
    )
    rent = pd.DataFrame(supabase.table("api_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(
        supabase.table("api_rent_yield").select("*").execute().data
    )
    return (
        sales,
        sale_segments,
        sale_housing_types,
        sale_conditions,
        sale_floor_positions,
        rent,
        yield_data,
    )
