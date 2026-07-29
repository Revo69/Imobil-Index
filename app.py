# app.py - Imobil.Index 2026 - For Sale + Monthly Rent + Daily Rent
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

# =========================
# Config
# =========================
st.set_page_config(
    page_title="Imobil.Index | Moldova Real Estate Analytics",
    page_icon="house",
    layout="wide",
    initial_sidebar_state="expanded",
)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

HISTORY_WINDOW_DAYS = 90
HISTORY_SALE_COLUMNS = "date,city,sector,avg_per_m2_eur"
ESTATE_SEGMENT_COLUMNS = (
    "date,city,sector,rooms_group,area_band,listings,avg_price_eur,avg_per_m2_eur"
)
MONTHLY_RENT_DEAL = (
    "\u0421\u0434\u0430\u044e \u043f\u043e\u043c\u0435\u0441\u044f\u0447\u043d\u043e"
)
DAILY_RENT_DEAL = (
    "\u0421\u0434\u0430\u044e \u043f\u043e\u0441\u0443\u0442\u043e\u0447\u043d\u043e"
)
CHISINAU_CITY = "\u041a\u0438\u0448\u0438\u043d\u0451\u0432"
BALTI_CITY = "\u0411\u0435\u043b\u044c\u0446\u044b"

SALE_COLOR_SCALE = ["#dbeafe", "#93c5fd", "#2563eb", "#1e3a8a"]
RENT_COLOR_SCALE = ["#dcfce7", "#86efac", "#16a34a", "#14532d"]
DAILY_COLOR_SCALE = ["#fef3c7", "#fbbf24", "#f97316", "#9a3412"]
YIELD_COLOR_SCALE = ["#e0f2fe", "#67e8f9", "#0e7490", "#164e63"]
CHART_NEUTRAL = "#cbd5e1"
ROOM_GROUP_ORDER = ["1", "2", "3", "4+"]
AREA_BAND_ORDER = ["<40 m2", "40-59 m2", "60-79 m2", "80-119 m2", "120+ m2"]
PLOTLY_CHART_CONFIG = {
    "displayModeBar": False,
    "displaylogo": False,
    "responsive": True,
}


# =========================
# Style
# =========================
st.markdown(
    """
    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --text: #111827;
            --muted: #64748b;
            --border: #e2e8f0;
            --blue: #2563eb;
            --green: #16a34a;
            --amber: #d97706;
            --cyan: #0891b2;
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
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
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
            display: inline-flex;
            gap: 0.25rem;
            padding: 0.25rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #ffffff;
        }

        div[data-testid="stTabs"] button {
            min-height: 2.25rem;
            padding: 0.45rem 0.9rem;
            border-radius: 6px;
            font-weight: 650;
            color: #475569;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: #111827;
            color: #ffffff;
            border-bottom-color: transparent;
        }

        .app-header {
            margin: 0 0 1rem;
            padding: 0 0 1rem;
            background: transparent;
            border-bottom: 1px solid rgba(226, 232, 240, 0.9);
        }

        .brand-row {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
        }

        .brand-title {
            font-size: clamp(2.15rem, 4vw, 2.85rem);
            line-height: 1;
            font-weight: 760;
            color: var(--text);
        }

        .brand-dot {
            color: var(--blue);
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
            border: 1px solid var(--border);
            border-radius: 999px;
            background: var(--surface);
            color: #334155;
            font-size: 0.86rem;
            white-space: nowrap;
        }

        .section {
            padding: 0.85rem 0 0.2rem;
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
            min-height: 112px;
            padding: 0.9rem 0.95rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
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
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
        }

        .chart-title {
            margin: 0.05rem 0 0.45rem;
            color: #334155;
            font-size: 0.82rem;
            font-weight: 760;
            letter-spacing: 0;
        }

        .insight-strip {
            padding: 1rem;
            border-left: 4px solid var(--cyan);
            border-radius: 8px;
            background: #f0f9ff;
            color: #164e63;
            line-height: 1.55;
        }

        .insight-card {
            height: 100%;
            min-height: 118px;
            padding: 0.95rem 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
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
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            background: #ffffff;
            color: var(--muted);
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {
            border-radius: 8px;
            background: #f8fafc;
            border-color: var(--border);
        }

        div[data-testid="stMetric"] {
            padding: 0.75rem 0.8rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #ffffff;
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
            background: #ffffff;
            color: #334155;
            font-weight: 650;
        }

        div[data-testid="stButton"] button:hover {
            border-color: var(--blue);
            color: var(--blue);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            background: var(--surface);
        }

        @media (max-width: 760px) {
            .brand-row {
                align-items: flex-start;
                flex-direction: column;
            }

            .status-pill {
                white-space: normal;
            }

            .insight-card {
                min-height: auto;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Data (cache 1 hour)
# =========================
@st.cache_data(ttl=3600)
def load_historical_data() -> pd.DataFrame:
    """
    Loads only the last HISTORY_WINDOW_DAYS of sale history, filtered at the
    database level, since that's all the 90-day trend chart uses.
    """
    cutoff = (datetime.now(UTC) - timedelta(days=HISTORY_WINDOW_DAYS)).strftime(
        "%Y-%m-%d"
    )

    all_sales = []
    offset = 0
    limit = 1000

    while True:
        resp = (
            supabase.table("api_estate_daily")
            .select(HISTORY_SALE_COLUMNS)
            .gte("date", cutoff)
            .range(offset, offset + limit - 1)
            .order("date", desc=False)
            .execute()
        )

        batch = resp.data
        if not batch:
            break
        all_sales.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    return pd.DataFrame(all_sales)


@st.cache_data(ttl=3600)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales = pd.DataFrame(
        supabase.table("api_estate_current").select("*").execute().data
    )
    sale_segments = pd.DataFrame(
        supabase.table("api_estate_segments_current")
        .select(ESTATE_SEGMENT_COLUMNS)
        .execute()
        .data
    )
    rent = pd.DataFrame(supabase.table("api_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(
        supabase.table("api_rent_yield").select("*").execute().data
    )
    return sales, sale_segments, rent, yield_data


# =========================
# UI helpers
# =========================
def format_int(value: float) -> str:
    return f"{value:,.0f}"


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


def render_app_header(latest_snapshot: str) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand-row">
                <div>
                    <div class="brand-title">
                        Imobil<span class="brand-dot">.</span>Index
                    </div>
                    <div class="brand-copy">
                        Residential real estate analytics for sale prices, rent,
                        short-term rent, and gross yield across Moldova.
                    </div>
                </div>
                <div class="status-pill">{latest_snapshot}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, caption: str | None = None) -> None:
    caption_html = f'<p class="section-caption">{caption}</p>' if caption else ""
    st.markdown(
        f"""
        <div class="section">
            <h3 class="section-title">{title}</h3>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_cards(
    title: str, caption: str, cards: list[tuple[str, str, str]]
) -> None:
    render_section(title, caption)
    if not cards:
        render_empty_state("Not enough data for this insight yet.")
        return

    for start in range(0, len(cards), 3):
        row_cards = cards[start : start + 3]
        columns = st.columns(len(row_cards))
        for column, (label, value, note) in zip(columns, row_cards, strict=True):
            with column:
                card_html = (
                    '<div class="insight-card">'
                    f'<div class="insight-card-label">{escape(label)}</div>'
                    f'<div class="insight-card-value">{escape(value)}</div>'
                    f'<div class="insight-card-note">{escape(note)}</div>'
                    "</div>"
                )
                st.markdown(
                    card_html,
                    unsafe_allow_html=True,
                )


def render_empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def render_chart_title(title: str) -> None:
    st.markdown(
        f'<div class="chart-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def render_plotly_chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CHART_CONFIG)


def apply_common_chart_style(fig, height: int = 430, show_legend: bool = False):
    fig.update_layout(
        height=height,
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "size": 13, "color": "#111827"},
        hoverlabel={"bgcolor": "#111827", "font_size": 13, "font_color": "#ffffff"},
        coloraxis_showscale=False,
        showlegend=show_legend,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "title_text": "",
        },
    )
    fig.update_xaxes(
        title_text="",
        showgrid=False,
        tickangle=-35,
        tickfont={"color": "#475569"},
        fixedrange=True,
    )
    fig.update_yaxes(
        title_font={"color": "#475569"},
        tickfont={"color": "#475569"},
        gridcolor="#e2e8f0",
        zeroline=False,
        fixedrange=True,
    )
    return fig


def render_ranked_bars(
    df: pd.DataFrame,
    title: str,
    price_col: str,
    y_label: str,
    color_scale: list[str],
    mode: str,
    digits: int,
) -> None:
    caption = (
        "Lowest visible sectors, sorted from lower to higher value."
        if mode == "lowest"
        else "Highest visible sectors, sorted from lower to higher value."
    )
    render_section(title, caption)
    if df.empty:
        render_empty_state("No sectors match the current filters.")
        return

    top = (
        df.nsmallest(10, price_col).copy()
        if mode == "lowest"
        else df.nlargest(10, price_col).copy()
    )
    top["Sector"] = sector_label(top)
    top["ChartLabel"] = top["Sector"].str.replace(" -> ", " - ", regex=False)
    top = top.sort_values(price_col, ascending=True)
    top["Label"] = top[price_col].map(lambda value: f"{value:.{digits}f}")

    accent_color = color_scale[1] if mode == "lowest" else color_scale[-1]
    colors = [CHART_NEUTRAL] * len(top)
    if colors:
        colors[0 if mode == "lowest" else -1] = accent_color

    fig = px.bar(
        top,
        x=price_col,
        y="ChartLabel",
        orientation="h",
        text="Label",
        labels={price_col: y_label, "ChartLabel": ""},
        custom_data=["Sector"],
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{customdata[0]}</b><br>%{x}<extra></extra>",
    )
    fig = apply_common_chart_style(fig, height=max(350, min(500, 120 + len(top) * 32)))
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
        categoryarray=top["ChartLabel"].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_plotly_chart(fig)


def render_tab_header(
    df: pd.DataFrame,
    price_col: str,
    empty_message: str,
    price_fmt: str = "{:.0f}",
    price_suffix: str = "",
) -> bool:
    if df.empty:
        render_empty_state(empty_message)
        return False

    listings = int(df["listings"].sum())
    lowest = df.loc[df[price_col].idxmin()]
    highest = df.loc[df[price_col].idxmax()]
    avg_price = price_fmt.format(weighted_average(df, price_col))

    render_section(
        "Current market view",
        f"{data_freshness(df)} | {format_int(listings)} listings after filters",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Sectors", format_int(len(df)), "Active city-sector groups")
    with col2:
        render_kpi_card(
            "Avg price per m2",
            f"{avg_price} EUR{price_suffix}",
            "Weighted by listings",
        )
    with col3:
        render_kpi_card(
            "Lowest price",
            f"{price_fmt.format(lowest[price_col])} EUR{price_suffix}",
            place_label(lowest),
        )
    with col4:
        render_kpi_card(
            "Highest price",
            f"{price_fmt.format(highest[price_col])} EUR{price_suffix}",
            place_label(highest),
        )

    return True


def render_price_sections(
    df: pd.DataFrame,
    price_col: str,
    y_label: str,
    low_scale: list[str],
    high_scale: list[str],
    digits: int,
) -> None:
    col_l, col_r = st.columns(2)
    with col_l:
        render_ranked_bars(
            df, "Lowest priced sectors", price_col, y_label, low_scale, "lowest", digits
        )
    with col_r:
        render_ranked_bars(
            df,
            "Highest priced sectors",
            price_col,
            y_label,
            high_scale,
            "highest",
            digits,
        )


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
    plot["Label"] = plot["avg_per_m2_eur"].map(lambda value: f"{value:.0f}")
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
        custom_data=["ListingsLabel"],
        category_orders={group_col: category_order},
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x:,.0f} EUR/m2<br>"
            "%{customdata[0]} listings<extra></extra>"
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


def render_sale_segments(df_segments: pd.DataFrame) -> None:
    render_section(
        "Prices by home profile",
        "Sale prices by room count and total area, weighted by listings.",
    )
    if df_segments.empty:
        render_empty_state("No sale segment data matches the current filters.")
        return

    room_options = ordered_segment_options(
        df_segments, "rooms_group", ROOM_GROUP_ORDER
    )
    area_options = ordered_segment_options(df_segments, "area_band", AREA_BAND_ORDER)

    filter_col_1, filter_col_2 = st.columns(2)
    with filter_col_1:
        selected_rooms = st.multiselect(
            "Rooms",
            options=room_options,
            default=[],
            placeholder="All room groups",
            key="sale_segment_rooms",
        )
    with filter_col_2:
        selected_area_bands = st.multiselect(
            "Area",
            options=area_options,
            default=[],
            placeholder="All area bands",
            key="sale_segment_area_bands",
        )

    filtered_segments = df_segments.copy()
    if selected_rooms:
        filtered_segments = filtered_segments[
            filtered_segments["rooms_group"].astype(str).isin(selected_rooms)
        ]
    if selected_area_bands:
        filtered_segments = filtered_segments[
            filtered_segments["area_band"].astype(str).isin(selected_area_bands)
        ]

    if filtered_segments.empty:
        render_empty_state("No home profiles match the selected rooms and area.")
        return

    room_summary = build_segment_summary(
        filtered_segments, "rooms_group", ROOM_GROUP_ORDER
    )
    area_summary = build_segment_summary(
        filtered_segments, "area_band", AREA_BAND_ORDER
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


def render_listing_sections(df: pd.DataFrame, color_scale: list[str]) -> None:
    col_l, col_r = st.columns(2)
    with col_l:
        render_ranked_bars(
            df,
            "Lowest inventory sectors",
            "listings",
            "Listings",
            color_scale,
            "lowest",
            0,
        )
    with col_r:
        render_ranked_bars(
            df,
            "Highest inventory sectors",
            "listings",
            "Listings",
            color_scale,
            "highest",
            0,
        )


def render_market_highlights(
    df: pd.DataFrame, price_col: str, price_fmt: str = "{:.0f}", price_suffix: str = ""
) -> None:
    if df.empty:
        return

    most_listings = df.loc[df["listings"].idxmax()]
    lowest = df.loc[df[price_col].idxmin()]
    highest = df.loc[df[price_col].idxmax()]
    spread = highest[price_col] - lowest[price_col]

    render_section("Key signals", "Quick read of the current filtered market.")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi_card(
            "Most Active Sector",
            format_int(most_listings["listings"]),
            place_label(most_listings),
        )
    with col2:
        render_kpi_card(
            "Price Range",
            f"{price_fmt.format(spread)} EUR{price_suffix}",
            f"{place_label(lowest)} to {place_label(highest)}",
        )
    with col3:
        render_kpi_card(
            "Median Sector Price",
            f"{price_fmt.format(df[price_col].median())} EUR{price_suffix}",
            "Median across visible sectors",
        )


def render_decision_notes(
    df: pd.DataFrame,
    price_col: str,
    price_fmt: str = "{:.0f}",
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

    cards = [
        (
            "Entry point",
            f"{price_fmt.format(lowest[price_col])} EUR{price_suffix}",
            f"Lowest visible value: {place_label(lowest)}.",
        ),
        (
            "Liquidity hub",
            f"{inventory_share:.1f}% of listings",
            f"Most active visible sector: {place_label(most_listings)}.",
        ),
        (
            "Market spread",
            f"{spread_pct:.0f}%",
            f"From {place_label(lowest)} to {place_label(highest)}.",
        ),
        (
            "Weighted vs median",
            f"{abs(premium_or_discount):.1f} EUR {direction}",
            "Shows whether larger listing pools are priced above or below the middle sector.",
        ),
    ]
    render_insight_cards(
        "Decision notes",
        "Plain-language signals from the current filtered market.",
        cards,
    )


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
    render_section(
        "Daily vs monthly break-even",
        "Estimated number of daily-rent days that equals one month of rent per m2.",
    )
    if df_break_even.empty:
        render_empty_state("Not enough matching monthly and daily rent data.")
        return

    fastest = df_break_even.iloc[0]
    slowest = df_break_even.iloc[-1]
    median_days = df_break_even["break_even_days"].median()
    cards = [
        (
            "Fastest switch point",
            f"{fastest['break_even_days']:.0f} days",
            f"After this, monthly rent can be cheaper in {fastest['Sector']}.",
        ),
        (
            "Median switch point",
            f"{median_days:.0f} days",
            "Middle value across visible sectors with both rent modes.",
        ),
        (
            "Longest daily window",
            f"{slowest['break_even_days']:.0f} days",
            f"Daily rent stays competitive longest in {slowest['Sector']}.",
        ),
    ]
    render_insight_cards(
        "Stay calculator",
        "Useful for short stays, temporary housing, and relocation scenarios.",
        cards,
    )

    top = df_break_even.nsmallest(10, "break_even_days").copy()
    top["ChartLabel"] = top["Sector"].str.replace(" -> ", " - ", regex=False)
    top = top.sort_values("break_even_days", ascending=True)
    top["Label"] = top["break_even_days"].map(lambda value: f"{value:.0f} days")

    fig = px.bar(
        top,
        x="break_even_days",
        y="ChartLabel",
        orientation="h",
        text="Label",
        labels={"break_even_days": "Days", "ChartLabel": ""},
        custom_data=["Sector"],
    )
    colors = [CHART_NEUTRAL] * len(top)
    if colors:
        colors[0] = DAILY_COLOR_SCALE[2]
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{customdata[0]}</b><br>%{x:.1f} days<extra></extra>",
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
        comparison = f"Chisinau is {gap:.0f} EUR/m2 higher than the outside-city average."

    cards = [
        (
            "Most active outside city",
            str(most_active["city"]),
            f"{format_int(most_active['listings'])} listings in the visible data.",
        ),
        (
            "Lowest outside-city price",
            f"{lowest_city[price_col]:.0f} EUR/m2",
            str(lowest_city["city"]),
        ),
        (
            "Chisinau gap",
            f"{outside_avg:.0f} EUR/m2",
            comparison,
        ),
    ]
    render_insight_cards(
        "Outside Chisinau radar",
        "Quick view of sale prices outside Chisinau.",
        cards,
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
            f"{best_monthly['yield_monthly_percent']:.1f}%",
            place_label(best_monthly),
        ))
    if data["yield_daily_percent"].notna().any():
        best_daily = data.loc[data["yield_daily_percent"].idxmax()]
        cards.append((
            "Best daily yield",
            f"{best_daily['yield_daily_percent']:.1f}%",
            f"{place_label(best_daily)} at the dashboard occupancy assumption.",
        ))
    if data["daily_uplift"].notna().any():
        strongest_uplift = data.loc[data["daily_uplift"].idxmax()]
        cards.append((
            "Daily rent advantage",
            f"+{strongest_uplift['daily_uplift']:.1f} pp",
            f"Biggest daily-vs-monthly yield gap: {place_label(strongest_uplift)}.",
        ))

    render_insight_cards(
        "Yield opportunities",
        "Indicative gross yield signals before operating costs and vacancy risk.",
        cards,
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
    top_y["Label"] = top_y[metric].map(lambda value: f"{value:.1f}%")

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
        custom_data=["Sector"],
    )
    fig.update_traces(
        marker_color=colors,
        textposition="outside",
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="<b>%{customdata[0]}</b><br>%{x:.1f}% gross yield<extra></extra>",
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
        "90-day price movement",
        "Most active Chisinau sectors, shown as comparable price paths.",
    )
    if hist.empty:
        render_empty_state("Historical sale data is not available.")
        return

    h = hist.copy()
    h["date"] = pd.to_datetime(h["date"], errors="coerce")
    h = h.dropna(subset=["date"])
    h = h[h["date"] >= pd.Timestamp.now() - pd.Timedelta(days=HISTORY_WINDOW_DAYS)]
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
    trend_colors = [
        "#2563eb",
        "#0f766e",
        "#f97316",
        "#dc2626",
        "#7c3aed",
        "#0891b2",
        "#65a30d",
        "#ca8a04",
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
        labels={"avg_per_m2_eur": "EUR per m2", "date": "Date", "sector": "Sector"},
    )
    fig.update_traces(
        line_width=2.2,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x|%d %b %Y}<br>"
            "%{y:,.0f} EUR per m2<extra></extra>"
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
            marker={"size": 6, "color": color_map.get(sector, "#64748b")},
            text=[f"{sector} {row['avg_per_m2_eur']:.0f}"],
            textposition="middle right",
            textfont={"size": 12, "color": "#334155"},
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
        gridcolor="#e5e7eb",
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
        f"{len(df):,} visible city-sector groups. Sorted by {sort_label}.",
    )
    if df.empty:
        render_empty_state("No rows match the current filters.")
        return

    disp = df[columns].copy().sort_values(sort_col).reset_index(drop=True)
    numeric_cols = disp.select_dtypes(include="number").columns
    for col in numeric_cols:
        disp[col] = disp[col].round(1 if "per_m2" in col else 0)

    disp = disp.rename(columns=label_map).rename(columns=compact_labels)

    column_config = {}
    if "City" in disp.columns:
        column_config["City"] = st.column_config.TextColumn("City", width="medium")
    if "Sector" in disp.columns:
        column_config["Sector"] = st.column_config.TextColumn("Sector", width="medium")
    if "Listings" in disp.columns:
        column_config["Listings"] = st.column_config.NumberColumn(
            "Listings",
            help="Listings in this city-sector group.",
            format="%d",
            width="small",
        )

    for col in disp.columns:
        if col.startswith("EUR/m2"):
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="Average listing price per square meter.",
                format="%.0f",
                width="small",
            )
        elif col == "Avg price":
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="Average full listing price.",
                format="%.0f",
                width="small",
            )

    st.dataframe(
        disp,
        width="stretch",
        hide_index=True,
        height=min(620, 48 + len(disp) * 36),
        column_config=column_config,
    )


def filter_by_city_and_listings(
    df: pd.DataFrame,
    selected_cities: Iterable[str],
    min_listings: int,
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    selected_cities = list(selected_cities)
    if selected_cities and "city" in filtered.columns:
        filtered = filtered[filtered["city"].isin(selected_cities)]
    if "listings" in filtered.columns:
        filtered = filtered[filtered["listings"] >= min_listings]
    return filtered


def render_daily_rent_context(df_yield: pd.DataFrame) -> None:
    render_section(
        "Daily vs monthly rent context",
        "Indicative gross yield comparison for the current market snapshot.",
    )

    top_daily_yield = None
    if not df_yield.empty and "yield_daily_percent" in df_yield.columns:
        top_daily_yield = df_yield["yield_daily_percent"].max()

    st.markdown(
        f"""
        <div class="insight-strip">
            Daily rent can show materially higher gross yield than monthly rent,
            but it depends on occupancy, seasonality, and operating costs.
            The current model assumes 60% daily occupancy.
            {
                (
                    f"Top gross daily yield: <strong>{top_daily_yield:.1f}%</strong> "
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
        df_sales, df_sale_segments, df_rent, df_yield = load_data()
# Keep the dashboard readable if the upstream API or local cache fails.
except Exception as exc:  # noqa: BLE001
    st.error("Could not load dashboard data from Supabase.")
    st.caption(str(exc))
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

filter_col, main_col = st.columns([1.35, 4.25], gap="medium")

with filter_col, st.container(border=True):
    st.markdown("### Explore")
    st.caption("Use presets first, then refine the visible market.")

    st.markdown("**Presets**")
    preset_col_1, preset_col_2 = st.columns(2)
    with preset_col_1:
        if st.button("All", width="stretch"):
            st.session_state["filter_cities"] = []
            st.session_state["filter_min_listings"] = 1
        if CHISINAU_CITY in all_cities and st.button("Chișinău", width="stretch"):
            st.session_state["filter_cities"] = [CHISINAU_CITY]
    with preset_col_2:
        if st.button("Liquid", width="stretch"):
            st.session_state["filter_cities"] = []
            st.session_state["filter_min_listings"] = 50
        if BALTI_CITY in all_cities and st.button("Bălți", width="stretch"):
            st.session_state["filter_cities"] = [BALTI_CITY]

    st.markdown("**Filters**")
    selected_cities = st.multiselect(
        "Cities",
        options=all_cities,
        default=[],
        placeholder="All cities",
        key="filter_cities",
    )
    min_listings = st.number_input(
        "Min. listings",
        min_value=1,
        value=1,
        step=1,
        key="filter_min_listings",
    )
    market_lens = st.radio(
        "Chart focus",
        ["Prices", "Listings"],
        horizontal=True,
        key="market_lens",
    )

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
        df = filter_by_city_and_listings(df_sales, selected_cities, min_listings)
        sale_segments = filter_by_city_and_listings(
            df_sale_segments, selected_cities, min_listings
        )

        if render_tab_header(
            df,
            price_col,
            "No sale listings match the current filters.",
            price_fmt="{:.0f}",
        ):
            render_market_highlights(df, price_col, price_fmt="{:.0f}")
            if market_lens == "Listings":
                render_listing_sections(df, SALE_COLOR_SCALE)
            else:
                render_price_sections(
                    df,
                    price_col,
                    "Price per m2 (EUR)",
                    SALE_COLOR_SCALE,
                    ["#fee2e2", "#fca5a5", "#ef4444", "#991b1b"],
                    0,
                )
            render_sale_segments(sale_segments)
            render_sales_trend(df_hist_sales, selected_cities)
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
            price_fmt="{:.1f}",
            price_suffix="/month",
        ):
            render_market_highlights(
                df, price_col, price_fmt="{:.1f}", price_suffix="/month"
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
        filtered_yield = filter_by_city_and_listings(
            df_yield, selected_cities, min_listings
        )

        if render_tab_header(
            df,
            price_col,
            "No daily rent listings match the current filters.",
            price_fmt="{:.1f}",
            price_suffix="/day",
        ):
            render_market_highlights(
                df, price_col, price_fmt="{:.1f}", price_suffix="/day"
            )
            if market_lens == "Listings":
                render_listing_sections(df, DAILY_COLOR_SCALE)
            else:
                render_price_sections(
                    df,
                    price_col,
                    "Price per m2 (EUR/day)",
                    DAILY_COLOR_SCALE,
                    ["#f3e8ff", "#c084fc", "#9333ea", "#581c87"],
                    1,
                )
            render_yield_chart(
                filtered_yield,
                "yield_daily_percent",
                "Daily rental yield at 60% occupancy",
                "Indicative gross annual yield, before operating costs.",
            )
            render_daily_rent_context(filtered_yield)

    # --------------------- 4. Insights ---------------------
    with tab_insights:
        sale_df = filter_by_city_and_listings(
            df_sales, selected_cities, min_listings
        )
        monthly_df = df_rent[df_rent["deal_type"] == MONTHLY_RENT_DEAL].copy()
        monthly_df = filter_by_city_and_listings(
            monthly_df, selected_cities, min_listings
        )
        daily_df = df_rent[df_rent["deal_type"] == DAILY_RENT_DEAL].copy()
        daily_df = filter_by_city_and_listings(
            daily_df, selected_cities, min_listings
        )
        yield_df = filter_by_city_and_listings(
            df_yield, selected_cities, min_listings
        )

        render_section(
            "Insight center",
            "Practical signals inspired by common real-estate decisions.",
        )

        if sale_df.empty and monthly_df.empty and daily_df.empty and yield_df.empty:
            render_empty_state("No market data matches the current filters.")
        else:
            render_decision_notes(sale_df, "avg_per_m2_eur", price_fmt="{:.0f}")
            render_outside_chisinau_radar(sale_df)
            render_break_even_analysis(
                build_break_even_table(df_rent, selected_cities, min_listings)
            )
            render_yield_opportunity_notes(yield_df)


# =========================
# Footer
# =========================
st.markdown(
    """
    <div
        style="
            text-align: center;
            padding: 2.5rem 0 1rem;
            color: #64748b;
            font-size: 0.9rem;
        "
    >
        <a
            href="mailto:sergey.revo@outlook.com"
            style="color:#475569; text-decoration:none;"
        >
            sergey.revo@outlook.com
        </a>
        <br><br>
        <small>Copyright 2026 - Imobil.Index</small>
    </div>
    """,
    unsafe_allow_html=True,
)

