# app.py - Imobil.Index 2026 - For Sale + Monthly Rent + Daily Rent
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

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

        .chart-shell {
            padding: 0.85rem 0.9rem 0.25rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
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
    sales = pd.DataFrame(
        supabase.table("gold_estate_current").select("*").execute().data
    )
    rent = pd.DataFrame(supabase.table("gold_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(
        supabase.table("gold_rent_yield").select("*").execute().data
    )
    return sales, rent, yield_data


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


def render_empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


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
    )
    fig.update_yaxes(
        title_font={"color": "#475569"},
        tickfont={"color": "#475569"},
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
        st.plotly_chart(fig, width="stretch")


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
        st.plotly_chart(fig, width="stretch")


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
    if "Listings" in disp.columns and disp["Listings"].sum() > 0:
        share = (disp["Listings"] / disp["Listings"].sum() * 100).round(1)
        disp.insert(disp.columns.get_loc("Listings") + 1, "Share", share)

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
    if "Share" in disp.columns:
        column_config["Share"] = st.column_config.ProgressColumn(
            "Share",
            help="Share of listings inside the current filtered table.",
            format="%.1f%%",
            min_value=0.0,
            max_value=max(1.0, float(disp["Share"].max())),
            width="medium",
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
                width="medium",
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
        df_sales, df_rent, df_yield = load_data()
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
        for dataset in (df_sales, df_rent)
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
    tab_sale, tab_rent_monthly, tab_rent_daily = st.tabs(
        ["For Sale", "Monthly Rent", "Daily Rent"]
    )

    # --------------------- 1. Sale ---------------------
    with tab_sale:
        price_col = "avg_per_m2_eur"
        df = filter_by_city_and_listings(df_sales, selected_cities, min_listings)

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
