# app.py - Imobil.Index 2026 - For Sale + Monthly Rent + Daily Rent
from datetime import datetime, timedelta
from typing import Iterable

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
MONTHLY_RENT_DEAL = "\u0421\u0434\u0430\u044e \u043f\u043e\u043c\u0435\u0441\u044f\u0447\u043d\u043e"
DAILY_RENT_DEAL = "\u0421\u0434\u0430\u044e \u043f\u043e\u0441\u0443\u0442\u043e\u0447\u043d\u043e"
CHISINAU_CITY = "\u041a\u0438\u0448\u0438\u043d\u0451\u0432"

SALE_COLOR_SCALE = ["#dbeafe", "#93c5fd", "#2563eb", "#1e3a8a"]
RENT_COLOR_SCALE = ["#dcfce7", "#86efac", "#16a34a", "#14532d"]
DAILY_COLOR_SCALE = ["#fef3c7", "#fbbf24", "#f97316", "#9a3412"]
YIELD_COLOR_SCALE = ["#e0f2fe", "#67e8f9", "#0e7490", "#164e63"]


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
            max-width: 1360px;
            padding-top: 2rem;
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

        div[data-testid="stTabs"] button {
            padding: 0.75rem 1rem;
            font-weight: 650;
            color: #475569;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--blue);
            border-bottom-color: var(--blue);
        }

        .app-header {
            margin: 0 0 1.25rem;
            padding: 0 0 1.25rem;
            background: transparent;
            border-bottom: 1px solid rgba(226, 232, 240, 0.85);
        }

        .brand-row {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
        }

        .brand-title {
            font-size: clamp(2rem, 4vw, 3.1rem);
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
            padding: 1.1rem 0 0.25rem;
        }

        .section-title {
            margin: 0 0 0.2rem;
            font-size: 1.1rem;
            font-weight: 720;
            color: var(--text);
        }

        .section-caption {
            margin: 0 0 0.75rem;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .kpi-card {
            min-height: 132px;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .kpi-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .kpi-value {
            margin-top: 0.45rem;
            color: var(--text);
            font-size: clamp(1.35rem, 2vw, 1.8rem);
            line-height: 1.12;
            font-weight: 760;
        }

        .kpi-note {
            margin-top: 0.45rem;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.35;
        }

        .chart-shell {
            padding: 1rem 1rem 0.35rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .insight-strip {
            padding: 1rem;
            border-left: 4px solid var(--cyan);
            border-radius: 8px;
            background: #f0f9ff;
            color: #164e63;
            line-height: 1.55;
        }

        .empty-state {
            padding: 1.25rem;
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            background: #ffffff;
            color: var(--muted);
        }

        .filter-note {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.4;
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
    cutoff = (datetime.now() - timedelta(days=HISTORY_WINDOW_DAYS)).strftime("%Y-%m-%d")

    all_sales = []
    offset = 0
    limit = 1000

    while True:
        resp = (
            supabase.table("gold_estate_daily")
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
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales = pd.DataFrame(supabase.table("gold_estate_current").select("*").execute().data)
    rent = pd.DataFrame(supabase.table("gold_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(supabase.table("gold_rent_yield").select("*").execute().data)
    return sales, rent, yield_data


# =========================
# UI helpers
# =========================
def format_int(value: float | int) -> str:
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
                    <div class="brand-title">Imobil<span class="brand-dot">.</span>Index</div>
                    <div class="brand-copy">
                        Moldova residential real estate analytics across sale prices,
                        monthly rent, short-term rent, and gross yield indicators.
                    </div>
                </div>
                <div class="status-pill">{latest_snapshot} | Gold-layer metrics</div>
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


def render_empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def apply_common_chart_style(fig, height: int = 430, show_legend: bool = False):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=28, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#111827"),
        hoverlabel=dict(bgcolor="#111827", font_size=13, font_color="#ffffff"),
        coloraxis_showscale=False,
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
    )
    fig.update_xaxes(
        title_text="",
        showgrid=False,
        tickangle=-35,
        tickfont=dict(color="#475569"),
    )
    fig.update_yaxes(
        title_font=dict(color="#475569"),
        tickfont=dict(color="#475569"),
        gridcolor="#e2e8f0",
        zeroline=False,
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
    render_section(title)
    if df.empty:
        render_empty_state("No sectors match the current filters.")
        return

    top = df.nsmallest(10, price_col).copy() if mode == "lowest" else df.nlargest(10, price_col).copy()
    top["Sector"] = sector_label(top)
    top = top.sort_values(price_col, ascending=(mode == "lowest"))

    fig = px.bar(
        top,
        x="Sector",
        y=price_col,
        color=price_col,
        color_continuous_scale=color_scale,
        labels={price_col: y_label},
    )
    fig.update_traces(
        texttemplate=f"%{{y:.{digits}f}}",
        textposition="outside",
        marker_line_width=0,
        cliponaxis=False,
    )
    fig = apply_common_chart_style(fig)

    with st.container(border=True):
        st.plotly_chart(fig, width="stretch")


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
        "Market Snapshot",
        f"{data_freshness(df)} | {format_int(listings)} listings after filters",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Sectors", format_int(len(df)), "Active city-sector groups")
    with col2:
        render_kpi_card(
            "Average Listing Price per m2",
            f"{avg_price} EUR{price_suffix}",
            "Weighted by listing count",
        )
    with col3:
        render_kpi_card(
            "Lowest Price",
            f"{price_fmt.format(lowest[price_col])} EUR{price_suffix}",
            place_label(lowest),
        )
    with col4:
        render_kpi_card(
            "Highest Price",
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
        render_ranked_bars(df, "Lowest priced sectors", price_col, y_label, low_scale, "lowest", digits)
    with col_r:
        render_ranked_bars(df, "Highest priced sectors", price_col, y_label, high_scale, "highest", digits)


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

    top_y = df_yield.nlargest(10, metric).copy()
    top_y["Sector"] = sector_label(top_y)

    fig = px.bar(
        top_y,
        x="Sector",
        y=metric,
        text=top_y[metric].round(1).astype(str),
        color=metric,
        color_continuous_scale=YIELD_COLOR_SCALE,
        labels={metric: "Gross yield, % p.a."},
    )
    fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
    fig = apply_common_chart_style(fig, height=460)

    with st.container(border=True):
        st.plotly_chart(fig, width="stretch")


def render_sales_trend(hist: pd.DataFrame, selected_cities: list[str]) -> None:
    render_section(
        "90-day price trend",
        "Top active Chisinau sectors by recent historical observations.",
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
    plot = h[h["sector"].isin(top_sec)].sort_values("date")

    if plot.empty:
        render_empty_state("No sectors have enough historical observations to plot.")
        return

    fig = px.line(
        plot,
        x="date",
        y="avg_per_m2_eur",
        color="sector",
        markers=False,
        labels={"avg_per_m2_eur": "Price per m2 (EUR)", "date": "Date"},
    )
    fig.update_traces(line_width=2.4)
    fig = apply_common_chart_style(fig, height=520, show_legend=True)
    fig.update_xaxes(tickangle=0)

    with st.container(border=True):
        st.plotly_chart(fig, width="stretch")


def render_sector_table(df: pd.DataFrame, columns: list[str], labels: list[str], sort_col: str) -> None:
    render_section("All sectors", "Sortable table with the exact values used in this view.")
    if df.empty:
        render_empty_state("No rows match the current filters.")
        return

    disp = df[columns].copy().sort_values(sort_col)
    numeric_cols = disp.select_dtypes(include="number").columns
    for col in numeric_cols:
        disp[col] = disp[col].round(1 if "per_m2" in col else 0)
    disp.columns = labels

    st.dataframe(
        disp,
        width="stretch",
        hide_index=True,
        height=min(560, 44 + len(disp) * 35),
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
        "Gross yield comparison based on the current Gold-layer yield model.",
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
            {f"Top observed gross daily yield: <strong>{top_daily_yield:.1f}%</strong> p.a." if top_daily_yield is not None else ""}
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
    with st.spinner("Loading Gold-layer market data..."):
        df_hist_sales = load_historical_data()
        df_sales, df_rent, df_yield = load_data()
except Exception as exc:
    st.error("Could not load dashboard data from Supabase.")
    st.caption(str(exc))
    st.stop()


# =========================
# Filter options
# =========================
all_cities = sorted(
    {
        city
        for dataset in (df_sales, df_rent)
        if not dataset.empty and "city" in dataset.columns
        for city in dataset["city"].dropna().unique()
    }
)

with st.sidebar:
    st.markdown("### Filters")
    st.caption("Leave cities empty to include all cities.")
    selected_cities = st.multiselect(
        "Cities",
        options=all_cities,
        default=[],
        placeholder="All cities",
        key="filter_cities",
    )
    min_listings = st.number_input(
        "Minimum listings per sector",
        min_value=1,
        value=1,
        step=1,
        key="filter_min_listings",
    )

    selected_count = len(selected_cities) if selected_cities else len(all_cities)
    st.metric("Cities in view", f"{selected_count}/{len(all_cities)}")

    st.markdown("---")
    st.caption("Cached for one hour. Filters affect presentation only.")

# =========================
# Header
# =========================
latest_dates = [
    latest_data_date(df)
    for df in (df_sales, df_rent, df_yield)
    if not df.empty and "date" in df.columns
]
latest_dates = [date for date in latest_dates if date is not None]
latest_snapshot = f"Data as of {max(latest_dates):%d %B %Y}" if latest_dates else "No snapshot"
render_app_header(latest_snapshot)


tab_sale, tab_rent_monthly, tab_rent_daily = st.tabs(["For Sale", "Monthly Rent", "Daily Rent"])


# --------------------- 1. Sale ---------------------
with tab_sale:
    price_col = "avg_per_m2_eur"
    df = filter_by_city_and_listings(df_sales, selected_cities, min_listings)

    if render_tab_header(df, price_col, "No sale listings match the current filters.", price_fmt="{:.0f}"):
        render_price_sections(
            df,
            price_col,
            "Price per m2 (EUR)",
            SALE_COLOR_SCALE,
            ["#fee2e2", "#fca5a5", "#ef4444", "#991b1b"],
            0,
        )
        render_sales_trend(df_hist_sales, selected_cities)
        render_sector_table(
            df,
            ["city", "sector", "listings", "avg_per_m2_eur", "avg_price_eur"],
            ["City", "Sector", "Listings", "Price per m2 (EUR)", "Average price (EUR)"],
            "avg_per_m2_eur",
        )


# --------------------- 2. Monthly Rental ---------------------
with tab_rent_monthly:
    price_col = "avg_price_per_m2_eur"
    df = df_rent[df_rent["deal_type"] == MONTHLY_RENT_DEAL].copy()
    df = filter_by_city_and_listings(df, selected_cities, min_listings)
    filtered_yield = filter_by_city_and_listings(df_yield, selected_cities, min_listings)

    if render_tab_header(
        df,
        price_col,
        "No monthly rent listings match the current filters.",
        price_fmt="{:.1f}",
        price_suffix="/month",
    ):
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
    filtered_yield = filter_by_city_and_listings(df_yield, selected_cities, min_listings)

    if render_tab_header(
        df,
        price_col,
        "No daily rent listings match the current filters.",
        price_fmt="{:.1f}",
        price_suffix="/day",
    ):
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


# =========================
# Footer
# =========================
st.markdown(
    """
    <div style="text-align: center; padding: 2.5rem 0 1rem; color: #64748b; font-size: 0.9rem;">
        <a href="mailto:sergey.revo@outlook.com" style="color:#475569; text-decoration:none;">sergey.revo@outlook.com</a>
        <br><br>
        <small>Copyright 2026 - Imobil.Index</small>
    </div>
    """,
    unsafe_allow_html=True,
)
