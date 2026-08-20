# app.py - Imobil.Index 2026 - For Sale + Monthly Rent + Daily Rent
import os
from collections.abc import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_charts import (
    apply_common_chart_style,
    render_listing_sections,
    render_plotly_chart,
    render_price_sections,
)
from dashboard_components import (
    format_int,
    format_number,
    format_percent,
    format_price,
    render_app_header,
    render_chart_title,
    render_empty_state,
    render_insight_card_row,
    render_insight_cards,
    render_kpi_card,
    render_section,
)
from dashboard_data import (
    HISTORY_WINDOW_DAYS,
    load_data,
    load_historical_data,
    load_historical_segment_data,
)
from dashboard_theme import (
    CHART_NEUTRAL,
    DAILY_COLOR_SCALE,
    HIGH_DAILY_RENT_COLOR_SCALE,
    HIGH_PRICE_COLOR_SCALE,
    RENT_COLOR_SCALE,
    SALE_COLOR_SCALE,
    THEME,
    YIELD_COLOR_SCALE,
    theme_css_vars,
)
from dashboard_transforms import (
    apply_daily_occupancy_assumption,
    build_city_market_summary,
    build_city_price_gap_summary,
    build_daily_vs_monthly_return,
    build_sale_market_from_segments,
    build_segment_summary,
    build_weekly_city_price_movement,
    build_weekly_price_movement,
    data_freshness,
    filter_by_city,
    filter_by_city_and_listings,
    filter_sale_profile_segments,
    filter_segments_to_market,
    has_sale_profile_filters,
    latest_data_date,
    ordered_segment_options,
    place_label,
    sector_label,
    weighted_average,
)

# =========================
# Config
# =========================
st.set_page_config(
    page_title="Imobil.Index | Moldova Real Estate Analytics",
    page_icon=":material/home_work:",
    layout="wide",
    initial_sidebar_state="expanded",
)

MONTHLY_RENT_DEAL = (
    "\u0421\u0434\u0430\u044e \u043f\u043e\u043c\u0435\u0441\u044f\u0447\u043d\u043e"
)
DAILY_RENT_DEAL = (
    "\u0421\u0434\u0430\u044e \u043f\u043e\u0441\u0443\u0442\u043e\u0447\u043d\u043e"
)
CHISINAU_CITY = "\u041a\u0438\u0448\u0438\u043d\u0451\u0432"
BALTI_CITY = "\u0411\u0435\u043b\u044c\u0446\u044b"

ROOM_GROUP_ORDER = ["1", "2", "3", "4+"]
AREA_BAND_ORDER = ["<40 m2", "40-59 m2", "60-79 m2", "80-119 m2", "120+ m2"]
HOUSING_TYPE_ORDER = ["Новострой", "Вторичный"]
HOUSING_TYPE_LABELS = {
    "Новострой": "New build",
    "Вторичный": "Resale",
}
CONDITION_GROUP_ORDER = [
    "Euro renovation",
    "Individual design",
    "White finish",
    "Cosmetic renovation",
    "Needs renovation",
]
FLOOR_POSITION_ORDER = ["Ground floor", "Middle floor", "Top floor"]


# =========================
# Style
# =========================
st.markdown(
    """
    <style>
        :root {
__THEME_CSS_VARS__
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            display: none;
        }

        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: var(--surface-muted);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--text);
        }

        div[data-testid="stTabs"] [role="tablist"] {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            width: 100%;
            box-sizing: border-box;
            margin: 0 0 1.35rem;
            padding: 0.35rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface-muted);
            box-shadow: var(--shadow-card);
        }

        div[data-testid="stTabs"] button {
            flex: 1 1 8rem;
            justify-content: center;
            min-height: 2.35rem;
            padding: 0.45rem 0.9rem;
            border-radius: 6px;
            border-bottom: 0 !important;
            font-weight: 650;
            color: #4f625a;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: var(--ink);
            color: #ffffff;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-border"] {
            display: none;
        }

        .app-header {
            margin: 0 0 1.15rem;
            padding: 1.05rem 1.15rem;
            border: 1px solid var(--border);
            border-left: 5px solid var(--green);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: var(--shadow);
        }

        .brand-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }

        .brand-kicker {
            margin-bottom: 0.45rem;
            color: var(--green);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .brand-title {
            font-size: clamp(2.15rem, 4vw, 2.85rem);
            line-height: 1;
            font-weight: 760;
            color: var(--ink);
        }

        .brand-dot {
            color: var(--cyan);
        }

        .brand-copy {
            max-width: 760px;
            margin-top: 0.65rem;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.55rem 0.8rem;
            border: 1px solid #c9d9d2;
            border-radius: 999px;
            background: var(--surface-soft);
            color: var(--ink);
            font-size: 0.86rem;
            white-space: nowrap;
        }

        .panel-title {
            margin: 0;
            color: var(--text);
            font-size: 1.55rem;
            line-height: 1.12;
            font-weight: 760;
        }

        .panel-copy {
            margin: 0.6rem 0 1.15rem;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .section {
            padding: 1rem 0 0.3rem;
        }

        .section-title {
            margin: 0 0 0.18rem;
            font-size: clamp(1.35rem, 2vw, 1.9rem);
            line-height: 1.15;
            font-weight: 760;
            color: var(--text);
        }

        .section-caption {
            margin: 0 0 0.7rem;
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.45;
        }

        .kpi-card {
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            min-height: 138px;
            padding: 0.9rem 0.95rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: var(--shadow-card);
        }

        .kpi-label {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .kpi-value {
            margin-top: 0.38rem;
            color: var(--text);
            font-size: clamp(1.35rem, 2vw, 1.72rem);
            line-height: 1.08;
            font-weight: 780;
        }

        .kpi-note {
            margin-top: 0.45rem;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.35;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: var(--shadow-card);
        }

        .chart-title {
            margin: 0.05rem 0 0.45rem;
            color: #31443b;
            font-size: 0.82rem;
            font-weight: 760;
            letter-spacing: 0;
        }

        .insight-strip {
            margin-bottom: 0.85rem;
            padding: 1rem;
            border-left: 4px solid var(--cyan);
            border-radius: 8px;
            background: #eaf8f6;
            color: #0b5f63;
            line-height: 1.55;
        }

        .insight-card {
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            min-height: 160px;
            margin-bottom: 0.85rem;
            padding: 0.95rem 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: var(--shadow-card);
        }

        .insight-card-label {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .insight-card-value {
            margin-top: 0.4rem;
            color: var(--text);
            font-size: clamp(1.15rem, 1.7vw, 1.45rem);
            line-height: 1.16;
            font-weight: 760;
            overflow-wrap: anywhere;
        }

        .insight-card-note {
            margin-top: 0.45rem;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.38;
            overflow-wrap: anywhere;
        }

        .empty-state {
            padding: 1.25rem;
            border: 1px dashed #bccbc4;
            border-radius: 8px;
            background: var(--surface);
            color: var(--muted);
        }

        .data-error-card {
            margin: 1rem 0;
            padding: 1rem 1.1rem;
            border: 1px solid #dfc9b9;
            border-left: 4px solid var(--amber);
            border-radius: 8px;
            background: #fff8f0;
            box-shadow: var(--shadow-card);
        }

        .data-error-label {
            color: var(--amber);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .data-error-title {
            margin-top: 0.35rem;
            color: var(--text);
            font-size: 1.25rem;
            line-height: 1.2;
            font-weight: 760;
        }

        .data-error-copy {
            max-width: 760px;
            margin-top: 0.45rem;
            color: var(--muted);
            line-height: 1.5;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {
            border-radius: 8px;
            background: var(--surface-muted);
            border-color: var(--border);
        }

        div[data-testid="stMetric"] {
            padding: 0.75rem 0.8rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
        }

        div[data-testid="stMetricValue"] {
            color: var(--text);
            font-size: 1.28rem;
            font-weight: 760;
        }

        div[data-testid="stButton"] button {
            min-height: 2.25rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            color: #31443b;
            font-weight: 650;
        }

        div[data-testid="stButton"] button:hover {
            border-color: var(--green);
            color: var(--green);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            background: var(--surface);
        }

        @media (max-width: 760px) {
            .block-container {
                padding: 0.75rem 0.85rem 2.25rem;
            }

            div[data-testid="stHorizontalBlock"] {
                flex-direction: column;
                gap: 0.75rem;
            }

            div[data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                flex: 1 1 auto !important;
                min-width: 0 !important;
            }

            div[data-testid="stTabs"] [role="tablist"] {
                gap: 0.3rem;
                margin-bottom: 1rem;
                padding: 0.3rem;
            }

            div[data-testid="stTabs"] button {
                flex: 1 1 calc(50% - 0.3rem);
                min-height: 2.45rem;
                padding: 0.45rem 0.35rem;
                font-size: 0.9rem;
            }

            .app-header {
                margin-bottom: 0.85rem;
                padding: 0.9rem 0.95rem;
            }

            .brand-row {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.75rem;
            }

            .brand-kicker {
                font-size: 0.68rem;
            }

            .brand-title {
                font-size: 2rem;
            }

            .brand-copy {
                margin-top: 0.55rem;
                font-size: 0.92rem;
                line-height: 1.5;
            }

            .status-pill {
                white-space: normal;
            }

            .section {
                padding-top: 0.7rem;
            }

            .kpi-card {
                min-height: auto;
                padding: 0.85rem 0.9rem;
            }

            .insight-card {
                min-height: auto;
            }

            .insight-strip,
            .data-error-card,
            .empty-state {
                padding: 0.85rem 0.9rem;
            }

            .data-error-title {
                font-size: 1.08rem;
            }
        }
    </style>
    """.replace("__THEME_CSS_VARS__", theme_css_vars()),
    unsafe_allow_html=True,
)


def render_data_load_error(details: str, show_details: bool = False) -> None:
    st.markdown(
        """
        <div class="data-error-card">
            <div class="data-error-label">Data connection</div>
            <div class="data-error-title">Market data is temporarily unavailable</div>
            <div class="data-error-copy">
                The dashboard could not load the latest public API data.
                Please refresh the page in a moment. If the issue remains, check
                the Streamlit app logs and Supabase API status.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_details:
        with st.expander("Technical details", icon=":material/code:"):
            st.code(details)


def render_tab_header(
    df: pd.DataFrame,
    price_col: str,
    empty_message: str,
    price_decimals: int = 0,
    price_suffix: str = "",
    context_note: str | None = None,
) -> bool:
    if df.empty:
        render_empty_state(empty_message)
        return False

    listings = int(df["listings"].sum())
    lowest = df.loc[df[price_col].idxmin()]
    highest = df.loc[df[price_col].idxmax()]
    avg_price = format_price(weighted_average(df, price_col), price_decimals, price_suffix)

    caption = f"{data_freshness(df)} | {format_int(listings)} listings after filters"
    if context_note:
        caption = f"{caption} | {context_note}"
    render_section("Current market view", caption)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Sectors", format_int(len(df)), "Active city-sector groups")
    with col2:
        render_kpi_card(
            "Avg price per m2",
            avg_price,
            "Weighted by listings",
        )
    with col3:
        render_kpi_card(
            "Lowest price",
            format_price(lowest[price_col], price_decimals, price_suffix),
            place_label(lowest),
        )
    with col4:
        render_kpi_card(
            "Highest price",
            format_price(highest[price_col], price_decimals, price_suffix),
            place_label(highest),
        )

    return True


def sale_profile_context_note(
    selected_rooms: Iterable[str],
    selected_area_bands: Iterable[str],
) -> str | None:
    selected_rooms = list(selected_rooms)
    selected_area_bands = list(selected_area_bands)
    if selected_rooms and selected_area_bands:
        return "Room and area profile applied"
    if selected_rooms:
        return "Room profile applied"
    if selected_area_bands:
        return "Area profile applied"
    return None


def render_segment_chart(
    summary: pd.DataFrame,
    group_col: str,
    title: str,
    y_label: str,
    category_order: list[str],
) -> None:
    if summary.empty:
        render_empty_state("Not enough segment data for the current filters.")
        return

    plot = summary.copy()
    plot[group_col] = plot[group_col].astype(str)
    plot["Label"] = plot["avg_per_m2_eur"].map(format_number)
    plot["PriceLabel"] = plot["avg_per_m2_eur"].map(format_number)
    plot["ListingsLabel"] = plot["listings"].map(format_int)
    plot["Profile"] = pd.Categorical(
        plot[group_col],
        categories=category_order,
        ordered=True,
    )
    plot = plot.sort_values("Profile", ascending=True)

    colors = [CHART_NEUTRAL] * len(plot)
    if colors:
        highlight_position = int(plot["avg_per_m2_eur"].reset_index(drop=True).idxmax())
        colors[highlight_position] = SALE_COLOR_SCALE[-1]

    fig = px.bar(
        plot,
        x="avg_per_m2_eur",
        y=group_col,
        orientation="h",
        text="Label",
        labels={group_col: "", "avg_per_m2_eur": y_label},
        custom_data=["PriceLabel", "ListingsLabel"],
        category_orders={group_col: category_order},
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]} EUR/m2<br>"
            "%{customdata[1]} listings<extra></extra>"
        ),
    )
    fig = apply_common_chart_style(fig, height=max(280, 120 + len(plot) * 42))
    fig.update_layout(margin={"l": 4, "r": 58, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(
        title_text="",
        showgrid=True,
        showticklabels=False,
        ticks="",
        zeroline=False,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=plot[group_col].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_chart_title(title)
        render_plotly_chart(fig)


def render_sale_segments(
    df_segments: pd.DataFrame,
    selected_rooms: Iterable[str],
    selected_area_bands: Iterable[str],
) -> None:
    profile_caption = (
        "Sale prices inside the current room and area profile, weighted by listings."
        if has_sale_profile_filters(selected_rooms, selected_area_bands)
        else "Sale prices by room count and total area, weighted by listings."
    )
    render_section(
        "Prices by home profile",
        profile_caption,
    )
    if df_segments.empty:
        render_empty_state("No sale segment data matches the current filters.")
        return

    room_summary = build_segment_summary(
        df_segments, "rooms_group", ROOM_GROUP_ORDER
    )
    area_summary = build_segment_summary(
        df_segments, "area_band", AREA_BAND_ORDER
    )

    col_rooms, col_area = st.columns(2)
    with col_rooms:
        render_segment_chart(
            room_summary,
            "rooms_group",
            "By rooms",
            "EUR/m2",
            ROOM_GROUP_ORDER,
        )
    with col_area:
        render_segment_chart(
            area_summary,
            "area_band",
            "By area",
            "EUR/m2",
            AREA_BAND_ORDER,
        )


def render_housing_type_comparison(df_housing_types: pd.DataFrame) -> None:
    render_section(
        "New build vs resale",
        "Price per m2 and available supply in the current city selection.",
    )

    columns = st.columns(2)
    for column, housing_type in zip(columns, HOUSING_TYPE_ORDER, strict=True):
        subset = df_housing_types[
            df_housing_types["housing_type"] == housing_type
        ].copy()
        with column:
            if subset.empty:
                render_kpi_card(
                    HOUSING_TYPE_LABELS[housing_type],
                    "No reliable data",
                    "No city-sector group meets the listing threshold.",
                )
                continue

            listings = int(subset["listings"].sum())
            avg_per_m2 = weighted_average(subset, "avg_per_m2_eur")
            render_kpi_card(
                HOUSING_TYPE_LABELS[housing_type],
                format_price(avg_per_m2, suffix="/m2"),
                f"{format_int(listings)} listings across visible sectors",
            )


def render_condition_comparison(df_conditions: pd.DataFrame) -> None:
    render_section(
        "Finish & condition",
        "Current asking price per m2 by normalized finish and condition group.",
    )
    summary = build_segment_summary(
        df_conditions, "condition_group", CONDITION_GROUP_ORDER
    )
    render_segment_chart(
        summary,
        "condition_group",
        "Price comparison",
        "EUR/m2",
        CONDITION_GROUP_ORDER,
    )
    st.caption(
        "Differences also reflect location, area, housing type, and listing mix; "
        "they are not a causal renovation premium."
    )


def render_floor_position_comparison(df_floor_positions: pd.DataFrame) -> None:
    render_section(
        "Floor position",
        "Current asking price per m2 by position within the building.",
    )
    summary = build_segment_summary(
        df_floor_positions, "floor_position", FLOOR_POSITION_ORDER
    )
    render_segment_chart(
        summary,
        "floor_position",
        "Price comparison",
        "EUR/m2",
        FLOOR_POSITION_ORDER,
    )
    st.caption(
        "Differences also reflect location, building height, condition, housing "
        "type, and listing mix; they are not a causal floor premium."
    )


def render_city_comparison_chart(
    summary: pd.DataFrame,
    value_col: str,
    title: str,
) -> None:
    plot = summary.nlargest(10, value_col).sort_values(value_col).copy()
    if plot.empty:
        render_empty_state("Not enough city data for the current filters.")
        return

    is_price_chart = value_col == "avg_per_m2_eur"
    plot["Label"] = plot[value_col].map(
        lambda value: format_number(value) if is_price_chart else format_int(value)
    )
    plot["PriceLabel"] = plot["avg_per_m2_eur"].map(format_number)
    plot["ListingsLabel"] = plot["listings"].map(format_int)

    colors = [CHART_NEUTRAL] * len(plot)
    if colors:
        colors[-1] = SALE_COLOR_SCALE[-1]

    fig = px.bar(
        plot,
        x=value_col,
        y="city",
        orientation="h",
        text="Label",
        labels={value_col: "", "city": ""},
        custom_data=["PriceLabel", "ListingsLabel"],
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]} EUR/m2<br>"
            "%{customdata[1]} visible listings<extra></extra>"
        ),
    )
    fig = apply_common_chart_style(fig, height=max(300, 120 + len(plot) * 36))
    fig.update_layout(margin={"l": 4, "r": 58, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(
        title_text="",
        showgrid=True,
        showticklabels=False,
        ticks="",
        zeroline=False,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=plot["city"].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_chart_title(title)
        render_plotly_chart(fig)


def render_city_comparison(df: pd.DataFrame) -> None:
    summary = build_city_market_summary(df)
    if summary.empty or summary["city"].nunique() < 2:
        return

    render_section(
        "Compare cities",
        "Price per m2 and visible supply across the current city selection.",
    )
    price_col, supply_col = st.columns(2)
    with price_col:
        render_city_comparison_chart(
            summary,
            "avg_per_m2_eur",
            "Highest priced cities",
        )
    with supply_col:
        render_city_comparison_chart(
            summary,
            "listings",
            "Most visible supply",
        )


def render_budget_guide(df: pd.DataFrame, buyer_budget: int) -> None:
    required = {"city", "sector", "listings", "avg_price_eur", "avg_per_m2_eur"}
    if df.empty or not required.issubset(df.columns):
        return

    render_section(
        "Budget guide",
        "City-sector averages that fit the buyer budget, ranked by visible supply.",
    )

    markets = df.copy()
    for column in ("listings", "avg_price_eur", "avg_per_m2_eur"):
        markets[column] = pd.to_numeric(markets[column], errors="coerce")
    markets = markets.dropna(subset=required)
    markets = markets[markets["listings"] > 0]
    within_budget = markets[markets["avg_price_eur"] <= buyer_budget].copy()

    if within_budget.empty:
        render_empty_state(
            "No city-sector average is within this budget for the current filters."
        )
        return

    visible_supply = int(within_budget["listings"].sum())
    col_budget, col_markets, col_supply = st.columns(3)
    with col_budget:
        render_kpi_card(
            "Budget cap",
            format_price(buyer_budget),
            "For the current For Sale selection",
        )
    with col_markets:
        render_kpi_card(
            "Markets in range",
            format_int(len(within_budget)),
            "City-sector averages at or below budget",
        )
    with col_supply:
        render_kpi_card(
            "Visible supply",
            format_int(visible_supply),
            "Listings in markets within budget",
        )

    shortlist = within_budget.nlargest(10, "listings").copy()
    shortlist["Market"] = sector_label(shortlist)
    shortlist = shortlist[
        ["Market", "avg_price_eur", "avg_per_m2_eur", "listings"]
    ].rename(
        columns={
            "avg_price_eur": "Avg price, EUR",
            "avg_per_m2_eur": "Price, EUR/m2",
            "listings": "Listings",
        }
    )
    shortlist["Avg price, EUR"] = shortlist["Avg price, EUR"].map(format_number)
    shortlist["Price, EUR/m2"] = shortlist["Price, EUR/m2"].map(format_number)
    shortlist["Listings"] = shortlist["Listings"].map(format_int)

    with st.container(border=True):
        st.dataframe(
            shortlist,
            width="stretch",
            hide_index=True,
            height=min(420, 48 + len(shortlist) * 36),
            column_config={
                "Market": st.column_config.TextColumn("Market", width="medium"),
                "Avg price, EUR": st.column_config.TextColumn(
                    "Avg price, EUR", width="small"
                ),
                "Price, EUR/m2": st.column_config.TextColumn(
                    "Price, EUR/m2", width="small"
                ),
                "Listings": st.column_config.TextColumn("Listings", width="small"),
            },
        )
    st.caption(
        "Prices are listing-weighted city-sector averages. Individual listings may "
        "be above or below the selected budget."
    )


def render_market_highlights(
    df: pd.DataFrame, price_col: str, price_decimals: int = 0, price_suffix: str = ""
) -> None:
    if df.empty:
        return

    most_listings = df.loc[df["listings"].idxmax()]
    lowest = df.loc[df[price_col].idxmin()]
    highest = df.loc[df[price_col].idxmax()]
    spread = highest[price_col] - lowest[price_col]

    render_section("Market pulse", "Three quick signals from the current market.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Most active sector", format_int(most_listings["listings"]))
        st.caption(place_label(most_listings))
    with col2:
        st.metric("Price range", format_price(spread, price_decimals, price_suffix))
        st.caption(f"{place_label(lowest)} to {place_label(highest)}")
    with col3:
        st.metric(
            "Median sector price",
            format_price(df[price_col].median(), price_decimals, price_suffix),
        )
        st.caption("Median across visible sectors")


def render_decision_notes(
    df: pd.DataFrame,
    price_col: str,
    price_decimals: int = 0,
    price_suffix: str = "",
) -> None:
    if df.empty:
        return

    total_listings = df["listings"].sum()
    if total_listings <= 0:
        return

    lowest = df.loc[df[price_col].idxmin()]
    highest = df.loc[df[price_col].idxmax()]
    most_listings = df.loc[df["listings"].idxmax()]
    weighted_price = weighted_average(df, price_col)
    median_price = float(df[price_col].median())
    spread_pct = (
        ((highest[price_col] - lowest[price_col]) / lowest[price_col]) * 100
        if lowest[price_col] > 0
        else 0
    )
    inventory_share = most_listings["listings"] / total_listings * 100
    premium_or_discount = weighted_price - median_price
    direction = "above" if premium_or_discount >= 0 else "below"
    unit_suffix = "/m2" if price_col.endswith("_per_m2_eur") else price_suffix

    cards = [
        (
            "Entry point",
            format_price(lowest[price_col], price_decimals, unit_suffix),
            f"Lowest visible value: {place_label(lowest)}.",
        ),
        (
            "Liquidity hub",
            f"{format_percent(inventory_share)} of listings",
            f"Most active visible sector: {place_label(most_listings)}.",
        ),
        (
            "Market spread",
            format_percent(spread_pct, decimals=0),
            f"From {place_label(lowest)} to {place_label(highest)}.",
        ),
        (
            "Weighted vs median",
            f"{format_number(abs(premium_or_discount), 1)} EUR{unit_suffix} {direction}",
            "Shows whether larger listing pools are priced above or below the middle sector.",
        ),
    ]
    render_insight_cards(
        "Decision notes",
        "Plain-language signals from the current filtered market.",
        cards,
    )


def render_weekly_market_brief(
    historical_sales: pd.DataFrame,
    visible_markets: pd.DataFrame,
) -> None:
    movement = build_weekly_city_price_movement(historical_sales, visible_markets)
    is_city_brief = len(movement) >= 3
    if not is_city_brief:
        movement = build_weekly_price_movement(historical_sales, visible_markets)
        if len(movement) < 3:
            return

    median_change = float(movement["change_percent"].median())
    largest_increase = movement.loc[movement["change_percent"].idxmax()]
    lowest_movement = movement.loc[movement["change_percent"].idxmin()]
    baseline_date = movement["baseline_date"].iloc[0]
    latest_date = movement["latest_date"].iloc[0]
    days_between = int(movement["days_between"].iloc[0])

    def signed_percent(value: float) -> str:
        prefix = "+" if value > 0 else ""
        return f"{prefix}{format_percent(value)}"

    def city_note(row: pd.Series) -> str:
        return (
            f"{row['city']}: {format_int(row['comparable_sectors'])} comparable "
            f"sectors and {format_int(row['latest_listings'])} listings."
        )

    if is_city_brief:
        cards = [
            (
                "Median city movement",
                signed_percent(median_change),
                f"Across {format_int(len(movement))} comparable cities.",
            ),
            (
                "Largest city increase",
                signed_percent(largest_increase["change_percent"]),
                city_note(largest_increase),
            ),
            (
                "Lowest city movement",
                signed_percent(lowest_movement["change_percent"]),
                city_note(lowest_movement),
            ),
        ]
        caption = (
            "Listing-weighted asking-price movement over "
            f"{days_between} days: {baseline_date:%d %b %Y} to {latest_date:%d %b %Y}."
        )
        caveat = (
            "Changes can reflect both asking prices and the mix of visible listings; "
            "they are not transaction-price changes."
        )
    else:
        cards = [
            (
                "Median movement",
                signed_percent(median_change),
                f"Across {format_int(len(movement))} comparable markets.",
            ),
            (
                "Largest increase",
                signed_percent(largest_increase["change_percent"]),
                place_label(largest_increase),
            ),
            (
                "Lowest movement",
                signed_percent(lowest_movement["change_percent"]),
                place_label(lowest_movement),
            ),
        ]
        caption = (
            "Average asking-price movement over "
            f"{days_between} days: {baseline_date:%d %b %Y} to {latest_date:%d %b %Y}."
        )
        caveat = (
            "Showing city-sector detail because fewer than three cities are comparable. "
            "These are average asking prices per m2, not transaction prices."
        )

    render_insight_cards("Weekly market brief", caption, cards)
    st.caption(caveat)


def build_break_even_table(
    df_rent: pd.DataFrame,
    selected_cities: Iterable[str],
    min_listings: int,
) -> pd.DataFrame:
    required = {"city", "sector", "deal_type", "avg_price_per_m2_eur", "listings"}
    if df_rent.empty or not required.issubset(df_rent.columns):
        return pd.DataFrame()

    monthly = df_rent[df_rent["deal_type"] == MONTHLY_RENT_DEAL].copy()
    daily = df_rent[df_rent["deal_type"] == DAILY_RENT_DEAL].copy()
    monthly = filter_by_city_and_listings(monthly, selected_cities, min_listings)
    daily = filter_by_city_and_listings(daily, selected_cities, min_listings)
    if monthly.empty or daily.empty:
        return pd.DataFrame()

    merged = monthly.merge(
        daily,
        on=["city", "sector"],
        suffixes=("_monthly", "_daily"),
    )
    merged = merged[
        (merged["avg_price_per_m2_eur_monthly"] > 0)
        & (merged["avg_price_per_m2_eur_daily"] > 0)
    ].copy()
    if merged.empty:
        return merged

    merged["break_even_days"] = (
        merged["avg_price_per_m2_eur_monthly"]
        / merged["avg_price_per_m2_eur_daily"]
    )
    merged["Sector"] = sector_label(merged)
    return merged.sort_values("break_even_days")


def render_break_even_analysis(df_break_even: pd.DataFrame) -> None:
    if df_break_even.empty:
        return

    fastest = df_break_even.iloc[0]
    slowest = df_break_even.iloc[-1]
    median_days = df_break_even["break_even_days"].median()
    cards = [
        (
            "Fastest switch point",
            f"{format_number(fastest['break_even_days'])} days",
            f"After this, monthly rent can be cheaper in {fastest['Sector']}.",
        ),
        (
            "Median switch point",
            f"{format_number(median_days)} days",
            "Middle value across visible sectors with both rent modes.",
        ),
        (
            "Longest daily window",
            f"{format_number(slowest['break_even_days'])} days",
            f"Daily rent stays competitive longest in {slowest['Sector']}.",
        ),
    ]
    render_insight_cards(
        "Daily vs monthly break-even",
        "Estimated daily-rent days that equal one month of rent per m2.",
        cards,
    )

    top = df_break_even.nsmallest(10, "break_even_days").copy()
    top["ChartLabel"] = top["Sector"].str.replace(" -> ", " - ", regex=False)
    top = top.sort_values("break_even_days", ascending=True)
    top["Label"] = top["break_even_days"].map(
        lambda value: f"{format_number(value)} days"
    )
    top["HoverLabel"] = top["break_even_days"].map(
        lambda value: f"{format_number(value, 1)} days"
    )

    fig = px.bar(
        top,
        x="break_even_days",
        y="ChartLabel",
        orientation="h",
        text="Label",
        labels={"break_even_days": "Days", "ChartLabel": ""},
        custom_data=["Sector", "HoverLabel"],
    )
    colors = [CHART_NEUTRAL] * len(top)
    if colors:
        colors[0] = DAILY_COLOR_SCALE[2]
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
    )
    fig = apply_common_chart_style(fig, height=max(320, min(460, 120 + len(top) * 34)))
    fig.update_layout(margin={"l": 4, "r": 68, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(title_text="", showticklabels=False, ticks="")
    fig.update_yaxes(tickangle=0, automargin=True, title_text="")
    with st.container(border=True):
        render_plotly_chart(fig)

    st.markdown(
        """
        <div class="insight-strip">
            This is a price-only comparison from current listings. It does not
            include utilities, cleaning, service fees, vacancy, or seasonality.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_outside_chisinau_radar(df_sales: pd.DataFrame) -> None:
    price_col = "avg_per_m2_eur"
    if df_sales.empty or "city" not in df_sales.columns or price_col not in df_sales:
        return

    outside = df_sales[df_sales["city"] != CHISINAU_CITY].copy()
    if outside.empty:
        return

    outside["weighted_value"] = outside[price_col] * outside["listings"]
    city_stats = outside.groupby("city", as_index=False).agg(
        listings=("listings", "sum"),
        weighted_value=("weighted_value", "sum"),
    )
    city_stats = city_stats[city_stats["listings"] > 0].copy()
    if city_stats.empty:
        return

    city_stats["avg_per_m2_eur"] = (
        city_stats["weighted_value"] / city_stats["listings"]
    )
    most_active = city_stats.loc[city_stats["listings"].idxmax()]
    lowest_city = city_stats.loc[city_stats[price_col].idxmin()]
    outside_avg = (
        city_stats["weighted_value"].sum() / city_stats["listings"].sum()
        if city_stats["listings"].sum() > 0
        else 0
    )

    chisinau = df_sales[df_sales["city"] == CHISINAU_CITY]
    if chisinau.empty:
        comparison = "Chisinau is outside the current view."
    else:
        chisinau_avg = weighted_average(chisinau, price_col)
        gap = chisinau_avg - outside_avg
        comparison = (
            f"Chisinau is {format_price(gap, suffix='/m2')} higher than the "
            "outside-city average."
        )

    cards = [
        (
            "Most active outside city",
            str(most_active["city"]),
            f"{format_int(most_active['listings'])} listings in the visible data.",
        ),
        (
            "Lowest outside-city price",
            format_price(lowest_city[price_col], suffix="/m2"),
            str(lowest_city["city"]),
        ),
        (
            "Chisinau gap",
            format_price(outside_avg, suffix="/m2"),
            comparison,
        ),
    ]
    render_section(
        "Regional value comparison",
        "Sale prices outside Chisinau, compared with the visible Chisinau average.",
    )
    render_insight_card_row(cards)

    regional_comparison = build_city_price_gap_summary(df_sales, CHISINAU_CITY)
    if (
        regional_comparison.empty
        or "price_gap_eur_per_m2" not in regional_comparison.columns
    ):
        return
    regional_comparison = regional_comparison[
        regional_comparison["price_gap_eur_per_m2"] > 0
    ].copy()
    if regional_comparison["city"].nunique() < 2:
        return

    plot = (
        regional_comparison.nlargest(8, "price_gap_eur_per_m2")
        .sort_values("price_gap_eur_per_m2")
        .copy()
    )
    plot["Label"] = plot["price_gap_eur_per_m2"].map(
        lambda value: format_number(value)
    )
    plot["PriceLabel"] = plot["avg_per_m2_eur"].map(format_number)
    plot["ListingsLabel"] = plot["listings"].map(format_int)

    colors = [CHART_NEUTRAL] * len(plot)
    colors[-1] = SALE_COLOR_SCALE[-1]
    fig = px.bar(
        plot,
        x="price_gap_eur_per_m2",
        y="city",
        orientation="h",
        text="Label",
        labels={"price_gap_eur_per_m2": "", "city": ""},
        custom_data=["PriceLabel", "ListingsLabel"],
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]} EUR/m2<br>"
            "%{customdata[1]} visible listings<extra></extra>"
        ),
    )
    fig = apply_common_chart_style(fig, height=max(300, 120 + len(plot) * 36))
    fig.update_layout(margin={"l": 4, "r": 58, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(
        title_text="",
        showgrid=True,
        showticklabels=False,
        ticks="",
        zeroline=False,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=plot["city"].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_chart_title("Largest price gap to Chisinau")
        render_plotly_chart(fig)
    st.caption(
        "Values are listing-weighted city averages, not individual listing prices."
    )


def render_yield_opportunity_notes(df_yield: pd.DataFrame) -> None:
    required = {"yield_monthly_percent", "yield_daily_percent", "city", "sector"}
    if df_yield.empty or not required.issubset(df_yield.columns):
        return

    data = df_yield.copy()
    data["yield_monthly_percent"] = pd.to_numeric(
        data["yield_monthly_percent"], errors="coerce"
    )
    data["yield_daily_percent"] = pd.to_numeric(
        data["yield_daily_percent"], errors="coerce"
    )
    data["daily_uplift"] = (
        data["yield_daily_percent"] - data["yield_monthly_percent"]
    )

    cards = []
    if data["yield_monthly_percent"].notna().any():
        best_monthly = data.loc[data["yield_monthly_percent"].idxmax()]
        cards.append((
            "Best monthly yield",
            format_percent(best_monthly["yield_monthly_percent"]),
            place_label(best_monthly),
        ))
    if data["yield_daily_percent"].notna().any():
        best_daily = data.loc[data["yield_daily_percent"].idxmax()]
        cards.append((
            "Best daily yield",
            format_percent(best_daily["yield_daily_percent"]),
            f"{place_label(best_daily)} at the dashboard occupancy assumption.",
        ))
    if data["daily_uplift"].notna().any():
        strongest_uplift = data.loc[data["daily_uplift"].idxmax()]
        cards.append((
            "Daily rent advantage",
            f"+{format_number(strongest_uplift['daily_uplift'], 1)} pp",
            f"Biggest daily-vs-monthly yield gap: {place_label(strongest_uplift)}.",
        ))

    if not cards:
        return

    render_insight_cards(
        "Yield opportunities",
        "Indicative gross yield signals before operating costs and vacancy risk.",
        cards,
    )


def render_investment_shortlist(
    df_yield: pd.DataFrame,
    min_listings: int,
    daily_occupancy_percent: int,
) -> None:
    required = {
        "city",
        "sector",
        "yield_monthly_percent",
        "yield_daily_percent",
        "avg_sale_price_eur",
        "sale_listings",
        "total_rent_listings",
    }
    if df_yield.empty or not required.issubset(df_yield.columns):
        return

    data = df_yield.copy()
    numeric_columns = [
        "yield_monthly_percent",
        "yield_daily_percent",
        "avg_sale_price_eur",
        "sale_listings",
        "total_rent_listings",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["city", "sector", *numeric_columns])
    data = data[
        (data["sale_listings"] >= min_listings)
        & (data["total_rent_listings"] >= min_listings)
    ]
    if data.empty:
        return

    data["Market"] = sector_label(data)
    daily_yield_label = f"Daily gross yield ({daily_occupancy_percent}%)"
    shortlist = data.nlargest(10, "yield_monthly_percent").copy()
    shortlist = shortlist[
        [
            "Market",
            "yield_monthly_percent",
            "yield_daily_percent",
            "avg_sale_price_eur",
            "sale_listings",
            "total_rent_listings",
        ]
    ].rename(
        columns={
            "yield_monthly_percent": "Monthly gross yield",
            "yield_daily_percent": daily_yield_label,
            "avg_sale_price_eur": "Avg price, EUR",
            "sale_listings": "Sale listings",
            "total_rent_listings": "Rent listings",
        }
    )
    shortlist["Monthly gross yield"] = shortlist["Monthly gross yield"].map(
        format_percent
    )
    shortlist[daily_yield_label] = shortlist[daily_yield_label].map(format_percent)
    shortlist["Avg price, EUR"] = shortlist["Avg price, EUR"].map(format_number)
    shortlist["Sale listings"] = shortlist["Sale listings"].map(format_int)
    shortlist["Rent listings"] = shortlist["Rent listings"].map(format_int)

    render_section(
        "Investment shortlist",
        "Top visible markets by indicative monthly gross yield.",
    )
    with st.container(border=True):
        st.dataframe(
            shortlist,
            width="stretch",
            hide_index=True,
            height=min(420, 48 + len(shortlist) * 36),
            column_config={
                "Market": st.column_config.TextColumn("Market", width="medium"),
                "Monthly gross yield": st.column_config.TextColumn(
                    "Monthly gross yield",
                    width="small",
                ),
                daily_yield_label: st.column_config.TextColumn(
                    daily_yield_label,
                    width="small",
                ),
                "Avg price, EUR": st.column_config.TextColumn(
                    "Avg price, EUR",
                    width="small",
                ),
                "Sale listings": st.column_config.TextColumn(
                    "Sale listings",
                    width="small",
                ),
                "Rent listings": st.column_config.TextColumn(
                    "Rent listings",
                    width="small",
                ),
            },
        )
    st.caption(
        "Yield is indicative and gross. Daily rent uses the selected occupancy "
        "assumption and excludes operating costs, vacancy, taxes, and management fees."
    )


def render_daily_vs_monthly_return(
    df_yield: pd.DataFrame,
    daily_occupancy_percent: int,
    min_listings: int,
) -> None:
    data = build_daily_vs_monthly_return(df_yield, daily_occupancy_percent)
    if data.empty:
        return

    data = data[
        (data["sale_listings"] >= min_listings)
        & (data["total_rent_listings"] >= min_listings)
    ].copy()
    if data.empty:
        return

    daily_ahead = int((data["daily_advantage_pp"] > 0).sum())
    median_advantage = float(data["daily_advantage_pp"].median())
    median_break_even = float(data["occupancy_to_match_monthly_percent"].median())
    best_daily = data.iloc[0]
    signed_median_advantage = (
        f"+{format_number(median_advantage, 1)}"
        if median_advantage > 0
        else format_number(median_advantage, 1)
    )

    render_insight_cards(
        "Daily vs monthly return",
        (
            "Indicative gross-return comparison at "
            f"{daily_occupancy_percent}% expected daily occupancy."
        ),
        [
            (
                "Daily ahead",
                format_int(daily_ahead),
                f"Of {format_int(len(data))} comparable visible markets.",
            ),
            (
                "Median daily advantage",
                f"{signed_median_advantage} pp",
                "Daily gross yield versus monthly rent.",
            ),
            (
                "Median break-even occupancy",
                format_percent(median_break_even),
                "Daily occupancy needed to match monthly annual rent.",
            ),
            (
                "Highest daily yield",
                format_percent(best_daily["daily_gross_yield_percent"]),
                place_label(best_daily),
            ),
        ],
    )

    daily_yield_label = f"Daily yield ({daily_occupancy_percent}%)"
    comparison = data.head(10).copy()
    comparison["Market"] = sector_label(comparison)
    comparison = comparison[
        [
            "Market",
            "monthly_gross_yield_percent",
            "daily_gross_yield_percent",
            "occupancy_to_match_monthly_percent",
            "daily_advantage_pp",
        ]
    ].rename(
        columns={
            "monthly_gross_yield_percent": "Monthly yield",
            "daily_gross_yield_percent": daily_yield_label,
            "occupancy_to_match_monthly_percent": "Break-even occupancy",
            "daily_advantage_pp": "Daily vs monthly",
        }
    )
    comparison["Monthly yield"] = comparison["Monthly yield"].map(format_percent)
    comparison[daily_yield_label] = comparison[daily_yield_label].map(format_percent)
    comparison["Break-even occupancy"] = comparison[
        "Break-even occupancy"
    ].map(format_percent)
    comparison["Daily vs monthly"] = comparison["Daily vs monthly"].map(
        lambda value: (
            f"+{format_number(value, 1)} pp"
            if value > 0
            else f"{format_number(value, 1)} pp"
        )
    )

    with st.container(border=True):
        st.dataframe(
            comparison,
            width="stretch",
            hide_index=True,
            height=min(420, 48 + len(comparison) * 36),
            column_config={
                "Market": st.column_config.TextColumn("Market", width="medium"),
                "Monthly yield": st.column_config.TextColumn(
                    "Monthly yield", width="small"
                ),
                daily_yield_label: st.column_config.TextColumn(
                    daily_yield_label, width="small"
                ),
                "Break-even occupancy": st.column_config.TextColumn(
                    "Break-even occupancy", width="small"
                ),
                "Daily vs monthly": st.column_config.TextColumn(
                    "Daily vs monthly", width="small"
                ),
            },
        )
    st.caption(
        "Daily income is re-scaled from the public 60% occupancy model. Both "
        "returns are indicative and gross, before vacancy, cleaning, utilities, "
        "taxes, platform fees, and management costs."
    )


def render_yield_chart(
    df_yield: pd.DataFrame,
    metric: str,
    title: str,
    caption: str,
) -> None:
    render_section(title, caption)
    if df_yield.empty or metric not in df_yield.columns:
        render_empty_state("Yield data is not available for the current snapshot.")
        return
    if pd.to_numeric(df_yield[metric], errors="coerce").dropna().empty:
        render_empty_state("Yield data is not available for the current filters.")
        return

    top_y = df_yield.copy()
    top_y[metric] = pd.to_numeric(top_y[metric], errors="coerce")
    top_y = top_y.dropna(subset=[metric]).nlargest(10, metric)
    top_y["Sector"] = sector_label(top_y)
    top_y["ChartLabel"] = top_y["Sector"].str.replace(" -> ", " - ", regex=False)
    top_y = top_y.sort_values(metric, ascending=True)
    top_y["Label"] = top_y[metric].map(format_percent)

    colors = [CHART_NEUTRAL] * len(top_y)
    if colors:
        colors[-1] = YIELD_COLOR_SCALE[-1]

    fig = px.bar(
        top_y,
        x=metric,
        y="ChartLabel",
        orientation="h",
        text="Label",
        labels={metric: "Gross yield, % p.a.", "ChartLabel": ""},
        custom_data=["Sector", "Label"],
    )
    fig.update_traces(
        marker_color=colors,
        textposition="outside",
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]} gross yield<extra></extra>"
        ),
    )
    fig = apply_common_chart_style(fig, height=max(340, min(460, 125 + len(top_y) * 34)))
    fig.update_layout(margin={"l": 4, "r": 58, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(
        title_text="",
        showgrid=True,
        showticklabels=False,
        ticks="",
        zeroline=False,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=top_y["ChartLabel"].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_plotly_chart(fig)


def render_sales_trend(hist: pd.DataFrame, selected_cities: list[str]) -> None:
    render_section(
        "Chisinau price pulse",
        "90-day price paths in the most active Chisinau sectors.",
    )
    if hist.empty:
        render_empty_state("Historical sale data is not available.")
        return

    h = hist.copy()
    h["date"] = pd.to_datetime(h["date"], errors="coerce")
    h = h.dropna(subset=["date"])
    history_cutoff = pd.Timestamp.now() - pd.Timedelta(HISTORY_WINDOW_DAYS, unit="D")
    h = h[h["date"] >= history_cutoff]
    h = h[h["city"] == CHISINAU_CITY]

    if selected_cities and CHISINAU_CITY not in selected_cities:
        render_empty_state("Chisinau is not selected, so the 90-day trend is hidden.")
        return

    if h.empty:
        render_empty_state("No Chisinau history is available for the last 90 days.")
        return

    top_sec = h["sector"].value_counts().head(8).index
    plot = h[h["sector"].isin(top_sec)].copy().sort_values("date")

    if plot.empty:
        render_empty_state("No sectors have enough historical observations to plot.")
        return

    plot["sector"] = plot["sector"].fillna("Center").astype(str)
    plot["PriceLabel"] = plot["avg_per_m2_eur"].map(format_number)
    trend_colors = [
        "#315fc9",
        "#12805c",
        "#c56b2c",
        "#b84d4a",
        "#7557b5",
        "#0f8b8d",
        "#6f8f3b",
        "#a36b1c",
    ]
    color_map = {
        sector: trend_colors[index % len(trend_colors)]
        for index, sector in enumerate(plot["sector"].drop_duplicates())
    }

    fig = px.line(
        plot,
        x="date",
        y="avg_per_m2_eur",
        color="sector",
        markers=False,
        color_discrete_map=color_map,
        custom_data=["PriceLabel"],
        labels={"avg_per_m2_eur": "EUR per m2", "date": "Date", "sector": "Sector"},
    )
    fig.update_traces(
        line_width=2.2,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x|%d %b %Y}<br>"
            "%{customdata[0]} EUR per m2<extra></extra>"
        ),
    )

    last_points = plot.sort_values("date").groupby("sector", as_index=False).tail(1)
    last_points = last_points.sort_values("avg_per_m2_eur")
    for _, row in last_points.iterrows():
        sector = row["sector"]
        fig.add_scatter(
            x=[row["date"]],
            y=[row["avg_per_m2_eur"]],
            mode="markers+text",
            marker={"size": 6, "color": color_map.get(sector, THEME["muted"])},
            text=[f"{sector} {format_number(row['avg_per_m2_eur'])}"],
            textposition="middle right",
            textfont={"size": 12, "color": THEME["chart_label"]},
            hoverinfo="skip",
            showlegend=False,
            cliponaxis=False,
        )

    fig = apply_common_chart_style(fig, height=500, show_legend=False)
    fig.update_layout(
        hovermode="x unified",
        margin={"l": 16, "r": 150, "t": 10, "b": 18},
    )
    fig.update_xaxes(
        title_text="",
        tickangle=0,
        showgrid=False,
        tickformat="%d %b",
    )
    fig.update_yaxes(
        title_text="EUR per m2",
        gridcolor=THEME["border"],
        zeroline=False,
    )

    with st.container(border=True):
        render_plotly_chart(fig)


def selected_trend_city(selected_cities: Iterable[str]) -> str:
    selected_cities = list(selected_cities)
    if len(selected_cities) == 1:
        return selected_cities[0]
    if not selected_cities or CHISINAU_CITY in selected_cities:
        return CHISINAU_CITY
    return selected_cities[0]


def render_profile_sales_trend(
    hist_segments: pd.DataFrame,
    selected_cities: Iterable[str],
    selected_rooms: Iterable[str],
    selected_area_bands: Iterable[str],
    min_listings: int,
) -> None:
    trend_city = selected_trend_city(selected_cities)
    render_section(
        "90-day profile movement",
        f"Price paths for the selected room and area profile in {trend_city}.",
    )
    if hist_segments.empty:
        render_empty_state(
            "Profile-level history will appear after the new daily segment API is applied and refreshed."
        )
        return

    h = filter_by_city(hist_segments, [trend_city])
    h = filter_sale_profile_segments(h, selected_rooms, selected_area_bands)
    if h.empty:
        render_empty_state("No profile-level history matches the current filters yet.")
        return

    h["date"] = pd.to_datetime(h["date"], errors="coerce")
    h["listings"] = pd.to_numeric(h["listings"], errors="coerce")
    h["avg_price_eur"] = pd.to_numeric(h["avg_price_eur"], errors="coerce")
    h["avg_per_m2_eur"] = pd.to_numeric(h["avg_per_m2_eur"], errors="coerce")
    h = h.dropna(
        subset=["date", "listings", "avg_price_eur", "avg_per_m2_eur"]
    )
    history_cutoff = pd.Timestamp.now() - pd.Timedelta(HISTORY_WINDOW_DAYS, unit="D")
    h = h[h["date"] >= history_cutoff]
    if h.empty:
        render_empty_state("No profile-level history is available for the last 90 days.")
        return

    plot = build_sale_market_from_segments(h)
    plot = plot[plot["listings"] >= min_listings]
    if plot.empty:
        render_empty_state("No profile-level history has enough listings yet.")
        return
    if plot["date"].nunique() < 2:
        render_empty_state(
            "Profile history has only one snapshot so far. It will become a trend after more refreshes."
        )
        return

    top_sectors = (
        plot.groupby("sector", dropna=False)["listings"]
        .sum()
        .nlargest(8)
        .index
    )
    plot = plot[plot["sector"].isin(top_sectors)].copy().sort_values("date")
    if plot.empty:
        render_empty_state("No sectors have enough profile history to plot.")
        return

    plot["sector"] = plot["sector"].fillna("Center").astype(str)
    plot["PriceLabel"] = plot["avg_per_m2_eur"].map(format_number)
    trend_colors = [
        "#315fc9",
        "#12805c",
        "#c56b2c",
        "#b84d4a",
        "#7557b5",
        "#0f8b8d",
        "#6f8f3b",
        "#a36b1c",
    ]
    color_map = {
        sector: trend_colors[index % len(trend_colors)]
        for index, sector in enumerate(plot["sector"].drop_duplicates())
    }

    fig = px.line(
        plot,
        x="date",
        y="avg_per_m2_eur",
        color="sector",
        markers=False,
        color_discrete_map=color_map,
        custom_data=["PriceLabel"],
        labels={"avg_per_m2_eur": "EUR per m2", "date": "Date", "sector": "Sector"},
    )
    fig.update_traces(
        line_width=2.2,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x|%d %b %Y}<br>"
            "%{customdata[0]} EUR per m2<extra></extra>"
        ),
    )

    last_points = plot.sort_values("date").groupby("sector", as_index=False).tail(1)
    last_points = last_points.sort_values("avg_per_m2_eur")
    for _, row in last_points.iterrows():
        sector = row["sector"]
        fig.add_scatter(
            x=[row["date"]],
            y=[row["avg_per_m2_eur"]],
            mode="markers+text",
            marker={"size": 6, "color": color_map.get(sector, THEME["muted"])},
            text=[f"{sector} {format_number(row['avg_per_m2_eur'])}"],
            textposition="middle right",
            textfont={"size": 12, "color": THEME["chart_label"]},
            hoverinfo="skip",
            showlegend=False,
            cliponaxis=False,
        )

    fig = apply_common_chart_style(fig, height=500, show_legend=False)
    fig.update_layout(
        hovermode="x unified",
        margin={"l": 16, "r": 150, "t": 10, "b": 18},
    )
    fig.update_xaxes(
        title_text="",
        tickangle=0,
        showgrid=False,
        tickformat="%d %b",
    )
    fig.update_yaxes(
        title_text="EUR per m2",
        gridcolor=THEME["border"],
        zeroline=False,
    )

    with st.container(border=True):
        render_plotly_chart(fig)


def render_sector_table(
    df: pd.DataFrame, columns: list[str], labels: list[str], sort_col: str
) -> None:
    label_map = dict(zip(columns, labels, strict=True))
    compact_labels = {
        "Price per m2 (EUR)": "EUR/m2",
        "Price per m2 (EUR/month)": "EUR/m2/month",
        "Price per m2 (EUR/day)": "EUR/m2/day",
        "Average price (EUR)": "Avg price",
    }
    sort_label = compact_labels.get(label_map.get(sort_col, sort_col), sort_col)
    render_section(
        "Sector details",
        f"{format_int(len(df))} visible city-sector groups. Sorted by {sort_label}.",
    )
    if df.empty:
        render_empty_state("No rows match the current filters.")
        return

    disp = df[columns].copy().sort_values(sort_col).reset_index(drop=True)
    numeric_cols = disp.select_dtypes(include="number").columns
    for col in numeric_cols:
        decimals = 1 if "per_m2" in col else 0
        disp[col] = disp[col].map(
            lambda value, decimals=decimals: format_number(value, decimals)
        )

    disp = disp.rename(columns=label_map).rename(columns=compact_labels)

    column_config = {}
    if "City" in disp.columns:
        column_config["City"] = st.column_config.TextColumn("City", width="medium")
    if "Sector" in disp.columns:
        column_config["Sector"] = st.column_config.TextColumn("Sector", width="medium")
    if "Listings" in disp.columns:
        column_config["Listings"] = st.column_config.TextColumn(
            "Listings",
            help="Listings in this city-sector group.",
            width="small",
        )

    for col in disp.columns:
        if col.startswith("EUR/m2"):
            column_config[col] = st.column_config.TextColumn(
                col,
                help="Average listing price per square meter.",
                width="small",
            )
        elif col == "Avg price":
            column_config[col] = st.column_config.TextColumn(
                col,
                help="Average full listing price.",
                width="small",
            )

    st.dataframe(
        disp,
        width="stretch",
        hide_index=True,
        height=min(620, 48 + len(disp) * 36),
        column_config=column_config,
    )


def render_daily_rent_context(
    df_yield: pd.DataFrame,
    daily_occupancy_percent: int,
) -> None:
    render_section(
        "Daily vs monthly rent context",
        "Indicative gross yield comparison for the current market snapshot.",
    )

    top_daily_yield = None
    if not df_yield.empty and "yield_daily_percent" in df_yield.columns:
        top_daily_yield = pd.to_numeric(
            df_yield["yield_daily_percent"], errors="coerce"
        ).max()

    st.markdown(
        f"""
        <div class="insight-strip">
            Daily rent can show materially higher gross yield than monthly rent,
            but it depends on occupancy, seasonality, and operating costs.
            The current model assumes {daily_occupancy_percent}% daily occupancy.
            {
                (
                    f"Top gross daily yield: <strong>{format_percent(top_daily_yield)}</strong> "
                    "p.a."
                )
                if top_daily_yield is not None
                else ""
            }
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        render_kpi_card(
            "Monthly Rent",
            "Stable income",
            "Lower operational effort; yield is shown as indicative gross yield.",
        )
    with col2:
        render_kpi_card(
            "Daily Rent",
            "Higher variance",
            "Potentially higher gross yield, with occupancy and cost sensitivity.",
        )


# =========================
# Load data
# =========================
try:
    with st.spinner("Loading market data..."):
        df_hist_sales = load_historical_data()
        df_hist_sale_segments = load_historical_segment_data()
        (
            df_sales,
            df_sale_segments,
            df_sale_housing_types,
            df_sale_conditions,
            df_sale_floor_positions,
            df_rent,
            df_yield,
        ) = load_data()
# Keep the dashboard readable if the upstream API or local cache fails.
except Exception as exc:  # noqa: BLE001
    render_data_load_error(
        str(exc),
        show_details=os.environ.get("IMOBIL_DEBUG_ERRORS") == "1",
    )
    st.stop()


# =========================
# Filter options
# =========================
all_cities = sorted(
    {
        city
        for dataset in (df_sales, df_sale_segments, df_rent)
        if not dataset.empty and "city" in dataset.columns
        for city in dataset["city"].dropna().unique()
    }
)

# =========================
# Header
# =========================
latest_dates = [
    latest_data_date(df)
    for df in (df_sales, df_rent, df_yield)
    if not df.empty and "date" in df.columns
]
latest_dates = [date for date in latest_dates if date is not None]
latest_snapshot = (
    f"Data as of {max(latest_dates):%d %B %Y}" if latest_dates else "No snapshot"
)
render_app_header(latest_snapshot)

filter_col, main_col = st.columns([1.25, 4.45], gap="large")

with filter_col, st.container(border=True):
    st.markdown(
        """
        <h3 class="panel-title">Explore market</h3>
        <p class="panel-copy">Use presets first, then refine the visible market.</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Presets**")
    preset_col_1, preset_col_2 = st.columns(2)
    with preset_col_1:
        if st.button("All", width="stretch"):
            st.session_state["filter_cities"] = []
            st.session_state["filter_min_listings"] = 1
            st.session_state["filter_sale_rooms"] = []
            st.session_state["filter_sale_area_bands"] = []
        if CHISINAU_CITY in all_cities and st.button("Chișinău", width="stretch"):
            st.session_state["filter_cities"] = [CHISINAU_CITY]
            st.session_state["filter_sale_rooms"] = []
            st.session_state["filter_sale_area_bands"] = []
    with preset_col_2:
        if st.button("Liquid", width="stretch"):
            st.session_state["filter_cities"] = []
            st.session_state["filter_min_listings"] = 50
            st.session_state["filter_sale_rooms"] = []
            st.session_state["filter_sale_area_bands"] = []
        if BALTI_CITY in all_cities and st.button("Bălți", width="stretch"):
            st.session_state["filter_cities"] = [BALTI_CITY]
            st.session_state["filter_sale_rooms"] = []
            st.session_state["filter_sale_area_bands"] = []

    st.markdown("**Filters**")
    selected_cities = st.multiselect(
        "Cities",
        options=all_cities,
        default=[],
        placeholder="All cities",
        key="filter_cities",
    )
    profile_option_segments = filter_by_city(df_sale_segments, selected_cities)
    room_options = ordered_segment_options(
        profile_option_segments, "rooms_group", ROOM_GROUP_ORDER
    )
    area_options = ordered_segment_options(
        profile_option_segments, "area_band", AREA_BAND_ORDER
    )
    if "filter_sale_rooms" in st.session_state:
        st.session_state["filter_sale_rooms"] = [
            value
            for value in st.session_state["filter_sale_rooms"]
            if value in room_options
        ]
    if "filter_sale_area_bands" in st.session_state:
        st.session_state["filter_sale_area_bands"] = [
            value
            for value in st.session_state["filter_sale_area_bands"]
            if value in area_options
        ]
    st.markdown("**For Sale criteria**")
    selected_sale_rooms = st.multiselect(
        "Rooms",
        options=room_options,
        default=[],
        placeholder="All rooms",
        key="filter_sale_rooms",
    )
    selected_sale_area_bands = st.multiselect(
        "Area",
        options=area_options,
        default=[],
        placeholder="All areas",
        key="filter_sale_area_bands",
    )
    buyer_budget = st.number_input(
        "Buyer budget, EUR",
        min_value=10_000,
        value=100_000,
        step=5_000,
        key="buyer_budget_eur",
    )
    st.caption("Rooms and area affect For Sale. Budget applies to Budget guide only.")
    min_listings = st.number_input(
        "Min. listings",
        min_value=1,
        value=1,
        step=1,
        key="filter_min_listings",
    )
    st.markdown("**Daily rent assumption**")
    daily_occupancy_percent = st.slider(
        "Expected occupancy",
        min_value=20,
        max_value=90,
        value=60,
        step=5,
        format="%d%%",
        key="daily_occupancy_percent",
    )
    st.caption("Applies to daily-rent yield and return comparisons.")
    market_lens = st.radio(
        "Chart focus",
        ["Prices", "Listings"],
        horizontal=True,
        key="market_lens",
    )
    st.caption("Applies to the main rankings in every tab.")

    selected_count = len(selected_cities) if selected_cities else len(all_cities)
    st.metric("Cities in view", f"{selected_count}/{len(all_cities)}")
    st.caption("Use presets for fast exploration or filters for a specific view.")

with main_col:
    tab_sale, tab_rent_monthly, tab_rent_daily, tab_insights = st.tabs(
        ["For Sale", "Monthly Rent", "Daily Rent", "Insights"]
    )

    # --------------------- 1. Sale ---------------------
    with tab_sale:
        price_col = "avg_per_m2_eur"
        sale_profile_active = has_sale_profile_filters(
            selected_sale_rooms, selected_sale_area_bands
        )
        city_sale_segments = filter_by_city(df_sale_segments, selected_cities)
        profile_sale_segments = filter_sale_profile_segments(
            city_sale_segments, selected_sale_rooms, selected_sale_area_bands
        )
        if sale_profile_active:
            df = build_sale_market_from_segments(profile_sale_segments)
            df = filter_by_city_and_listings(df, [], min_listings)
        else:
            df = filter_by_city_and_listings(df_sales, selected_cities, min_listings)
        sale_segments = filter_segments_to_market(profile_sale_segments, df)

        if df.empty:
            render_empty_state("No sale listings match the current filters.")
        else:
            if sale_profile_active:
                render_profile_sales_trend(
                    df_hist_sale_segments,
                    selected_cities,
                    selected_sale_rooms,
                    selected_sale_area_bands,
                    min_listings,
                )
            else:
                render_sales_trend(df_hist_sales, selected_cities)
            render_tab_header(
                df,
                price_col,
                "No sale listings match the current filters.",
                price_decimals=0,
                context_note=sale_profile_context_note(
                    selected_sale_rooms, selected_sale_area_bands
                ),
            )
            render_market_highlights(df, price_col, price_decimals=0)
            if market_lens == "Listings":
                render_listing_sections(df, SALE_COLOR_SCALE)
            else:
                render_price_sections(
                    df,
                    price_col,
                    "Price per m2 (EUR)",
                    SALE_COLOR_SCALE,
                    HIGH_PRICE_COLOR_SCALE,
                    0,
                )
            render_budget_guide(df, buyer_budget)
            render_city_comparison(df)
            with st.expander("Property characteristics", icon=":material/home:"):
                st.caption(
                    "Compare housing type, finish, floor position, room count, and area."
                )
                housing_type_data = filter_by_city_and_listings(
                    df_sale_housing_types, selected_cities, min_listings
                )
                render_housing_type_comparison(housing_type_data)
                condition_data = filter_by_city_and_listings(
                    df_sale_conditions, selected_cities, min_listings
                )
                render_condition_comparison(condition_data)
                floor_position_data = filter_by_city_and_listings(
                    df_sale_floor_positions, selected_cities, min_listings
                )
                render_floor_position_comparison(floor_position_data)
                render_sale_segments(
                    sale_segments, selected_sale_rooms, selected_sale_area_bands
                )
            render_sector_table(
                df,
                ["city", "sector", "listings", "avg_per_m2_eur", "avg_price_eur"],
                [
                    "City",
                    "Sector",
                    "Listings",
                    "Price per m2 (EUR)",
                    "Average price (EUR)",
                ],
                "avg_per_m2_eur",
            )

    # --------------------- 2. Monthly Rental ---------------------
    with tab_rent_monthly:
        price_col = "avg_price_per_m2_eur"
        df = df_rent[df_rent["deal_type"] == MONTHLY_RENT_DEAL].copy()
        df = filter_by_city_and_listings(df, selected_cities, min_listings)
        filtered_yield = filter_by_city_and_listings(
            df_yield, selected_cities, min_listings
        )

        if render_tab_header(
            df,
            price_col,
            "No monthly rent listings match the current filters.",
            price_decimals=1,
            price_suffix="/month",
        ):
            render_market_highlights(
                df, price_col, price_decimals=1, price_suffix="/month"
            )
            if market_lens == "Listings":
                render_listing_sections(df, RENT_COLOR_SCALE)
            else:
                render_price_sections(
                    df,
                    price_col,
                    "Price per m2 (EUR/month)",
                    RENT_COLOR_SCALE,
                    DAILY_COLOR_SCALE,
                    1,
                )
            render_yield_chart(
                filtered_yield,
                "yield_monthly_percent",
                "Monthly rental yield",
                "Indicative gross annual yield by sector.",
            )

    # --------------------- 3. Daily Rental ---------------------
    with tab_rent_daily:
        price_col = "avg_price_per_m2_eur"
        df = df_rent[df_rent["deal_type"] == DAILY_RENT_DEAL].copy()
        df = filter_by_city_and_listings(df, selected_cities, min_listings)
        filtered_yield = apply_daily_occupancy_assumption(
            filter_by_city_and_listings(df_yield, selected_cities, min_listings),
            daily_occupancy_percent,
        )

        if render_tab_header(
            df,
            price_col,
            "No daily rent listings match the current filters.",
            price_decimals=1,
            price_suffix="/day",
        ):
            render_market_highlights(
                df, price_col, price_decimals=1, price_suffix="/day"
            )
            render_yield_chart(
                filtered_yield,
                "yield_daily_percent",
                f"Daily rental yield at {daily_occupancy_percent}% occupancy",
                "Indicative gross annual yield, before operating costs.",
            )
            if market_lens == "Listings":
                render_listing_sections(df, DAILY_COLOR_SCALE)
            else:
                render_price_sections(
                    df,
                    price_col,
                    "Price per m2 (EUR/day)",
                    DAILY_COLOR_SCALE,
                    HIGH_DAILY_RENT_COLOR_SCALE,
                    1,
                )
            with st.expander("Return scenarios", icon=":material/analytics:"):
                st.caption(
                    "Compare daily and monthly rent using the selected occupancy assumption."
                )
                render_daily_rent_context(filtered_yield, daily_occupancy_percent)
                break_even_df = build_break_even_table(
                    df_rent, selected_cities, min_listings
                )
                render_break_even_analysis(break_even_df)
                render_daily_vs_monthly_return(
                    filtered_yield,
                    daily_occupancy_percent,
                    min_listings,
                )

    # --------------------- 4. Insights ---------------------
    with tab_insights:
        sale_df = filter_by_city_and_listings(
            df_sales, selected_cities, min_listings
        )
        yield_df = apply_daily_occupancy_assumption(
            filter_by_city_and_listings(df_yield, selected_cities, min_listings),
            daily_occupancy_percent,
        )
        if sale_df.empty and yield_df.empty:
            render_empty_state(
                "No insight-ready market signals match the current filters."
            )
        else:
            render_weekly_market_brief(df_hist_sales, sale_df)
            render_decision_notes(sale_df, "avg_per_m2_eur", price_decimals=0)
            render_outside_chisinau_radar(sale_df)
            if not yield_df.empty:
                with st.expander("Investment analysis"):
                    render_yield_opportunity_notes(yield_df)
                    render_investment_shortlist(
                        yield_df,
                        min_listings,
                        daily_occupancy_percent,
                    )


# =========================
# Footer
# =========================
st.markdown(
    """
    <div
        style="
            text-align: center;
            padding: 2.5rem 0 1rem;
            color: __FOOTER_COLOR__;
            font-size: 0.9rem;
        "
    >
        <a
            href="mailto:sergey.revo@outlook.com"
            style="color:__FOOTER_LINK_COLOR__; text-decoration:none;"
        >
            sergey.revo@outlook.com
        </a>
        <br><br>
        <small>Copyright 2026 - Imobil.Index</small>
    </div>
    """.replace("__FOOTER_COLOR__", THEME["muted"]).replace(
        "__FOOTER_LINK_COLOR__", THEME["chart_label"]
    ),
    unsafe_allow_html=True,
)

