# app.py — Imobil.Index 2025 — For Sale + Monthly Rent + Daily Rent
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Config
# =========================
st.set_page_config(page_title="Imobil.Index | Moldova Real Estate Analytics", page_icon="house", layout="wide")

st.markdown("""
<div style='text-align:center; margin:1rem 0 2rem;'>
    <div style='font-size:2.2rem; font-weight:300; color:#1a1a1a; margin-bottom:0.3rem;'>
        Imobil<span style='color:#2563eb;'>.</span>Index
    </div>
    <div style='font-size:1rem; color:#555; margin-bottom:0.2rem;'>
        Real-time Moldova property market analytics
    </div>
    <div style='font-size:0.9rem; color:#777;'>
        Prices • Trends • Forecasts • Data only
    </div>
</div>
""", unsafe_allow_html=True)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Data (cache 1 hour)
# =========================

@st.cache_data(ttl=3600)
def load_historical_data():
    """Load batches 100 string"""
    all_sales = []
    all_rent = []
    offset = 0
    limit = 1000

    # --- Sale ---
    while True:
        resp = supabase.table("gold_estate_daily") \
            .select("*") \
            .range(offset, offset + limit - 1) \
            .order("date", desc=False) \
            .execute()
        
        batch = resp.data
        if not batch:
            break
        all_sales.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    # --- Rent ---
    offset = 0
    while True:
        resp = supabase.table("gold_rent_daily") \
            .select("*") \
            .range(offset, offset + limit - 1) \
            .order("date", desc=False) \
            .execute()
        
        batch = resp.data
        if not batch:
            break
        all_rent.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    return pd.DataFrame(all_sales), pd.DataFrame(all_rent)

df_hist_sales, df_hist_rent = load_historical_data()


@st.cache_data(ttl=3600)
def load_data():
    sales = pd.DataFrame(supabase.table("gold_estate_current").select("*").execute().data)
    rent = pd.DataFrame(supabase.table("gold_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(supabase.table("gold_rent_yield").select("*").execute().data)
    # hist_sales = pd.DataFrame(supabase.table("gold_estate_daily").select("*").execute().data)
    # hist_rent = pd.DataFrame(supabase.table("gold_rent_daily").select("*").execute().data)
    return sales, rent, yield_data

df_sales, df_rent, df_yield = load_data()

# =========================
# Header
# =========================
st.markdown(
    "<div style='text-align:center; font-size:3.2rem; font-weight:300; color:#1a1a1a; margin:2rem 0 0.5rem;'>"
    "Imobil<span style='color:#2563eb;'>.</span>Index"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align:center; font-size:1.35rem; color:#333; margin:0.5rem 0 1.5rem; letter-spacing:0.3px;'>"
    "Real-time Moldova property market analytics"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align:center; font-size:1.05rem; color:#555; margin-bottom:3rem;'>"
    "Prices • Trends • Forecasts • Data only"
    "</div>",
    unsafe_allow_html=True
)

tab_sale, tab_rent_monthly, tab_rent_daily = st.tabs(["For Sale", "Monthly Rent", "Daily Rent"])

# --------------------- 1. Sale ---------------------
with tab_sale:
    df = df_sales.copy()
    mode = "For Sale"
    price_col = "avg_per_m2_eur"
    hist = df_hist_sales
    color = "Blues"
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Updated: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} listings</div>", unsafe_allow_html=True)
    if df.empty: st.error("No sale listings available"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Sectors", len(df))
    with col2: st.metric("Average price per m²", f"{df[price_col].mean():.0f} €")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Lowest price</b><br>{cheapest['city']} → {cheapest['sector'] or 'Center'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Highest price</b><br>{expensive['city']} → {expensive['sector'] or 'Center'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Top 10 — Lowest price")
        top = df.nsmallest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Center")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale=color, labels={"avg_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")
    with col_r:
        st.subheader("Top 10 — Highest price")
        top = df.nlargest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Center")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale="Reds", labels={"avg_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")

    if not hist.empty:
        st.markdown("---")
        st.subheader("90-day price per m² trend — Chișinău")
        h = hist[hist['city'] == 'Кишинёв'].copy()
        if not h.empty:
            h['date'] = pd.to_datetime(h['date'])
            h = h[h['date'] >= pd.Timestamp.now() - pd.Timedelta(days=90)]
            top_sec = h['sector'].value_counts().head(8).index
            plot = h[h['sector'].isin(top_sec)]
            if not plot.empty:
                fig = px.line(plot.sort_values("date"), x="date", y=price_col, color="sector", markers=True, labels={"avg_per_m2_eur": "Price per m² (€)"})
                fig.update_layout(height=600)
                st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.subheader("All sectors")
    disp = df[['city','sector','listings','avg_per_m2_eur','avg_price_eur']].copy()
    disp['avg_per_m2_eur'] = disp['avg_per_m2_eur'].round(0).astype(int)
    disp['avg_price_eur'] = disp['avg_price_eur'].round(0).astype(int)
    disp = disp.sort_values('avg_per_m2_eur')
    disp.columns = ['City','Sector','Listings','Price per m² (€)','Average price per m² (€)']
    st.dataframe(disp, width="stretch", hide_index=True)

# --------------------- 2. Monthly Rental ---------------------
with tab_rent_monthly:
    df = df_rent[df_rent['deal_type'] == 'Сдаю помесячно'].copy()
    mode = "Monthly rent"
    price_col = "avg_price_per_m2_eur"
    hist = df_hist_rent[df_hist_rent['deal_type'] == 'Сдаю помесячно']
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Updated: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} listings</div>", unsafe_allow_html=True)
    if df.empty: st.error("No monthly rent listings available"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Sectors", len(df))
    with col2: st.metric("Average price per m²", f"{df[price_col].mean():.1f} €/month")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Lowest price</b><br>{cheapest['city']} → {cheapest['sector'] or 'Center'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Highest price</b><br>{expensive['city']} → {expensive['sector'] or 'Center'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Top 10 — Lowest price")
        top = df.nsmallest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Center")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale="Greens", labels={"avg_price_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")
    with col_r:
        st.subheader("Top 10 — Highest price")
        top = df.nlargest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Center")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale="Oranges", labels={"avg_price_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")

    # Yield rental monthly %
    if not df_yield.empty:
        st.markdown("---")

        st.subheader("Monthly rental yield (% per annum)")
        top_y = df_yield.nlargest(10, 'yield_monthly_percent').copy()

        top_y["Sector"] = top_y["city"] + " → " + top_y["sector"].fillna("Center")
    
        fig = px.bar(
            top_y,
            x="Sector",
            y="yield_monthly_percent",
            text=top_y["yield_monthly_percent"].round(1).astype(str),
            color="yield_monthly_percent",
            color_continuous_scale="Viridis",
            labels={"yield_monthly_percent": "%"}
        )
        fig.update_layout(height=600)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, width="stretch")



# --------------------- 3. Daily Rental ---------------------
with tab_rent_daily:
    df = df_rent[df_rent['deal_type'] == 'Сдаю посуточно'].copy()
    mode = "Daily rent"
    price_col = "avg_price_per_m2_eur"
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Updated: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} listings</div>", unsafe_allow_html=True)
    if df.empty: st.error("No daily rent listings available"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Sectors", len(df))
    with col2: st.metric("Average price per m²", f"{df[price_col].mean():.1f} €/daily")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Lowest price</b><br>{cheapest['city']} → {cheapest['sector'] or 'Center'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Highest price</b><br>{expensive['city']} → {expensive['sector'] or 'Center'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Top 10 — Lowest price")
        top = df.nsmallest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale="Purples", labels={"avg_price_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")
    with col_r:
        st.subheader("Top 10 — Highest price")
        top = df.nlargest(10, price_col).copy()
        top["Sector"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Sector", y=price_col, color=price_col, color_continuous_scale="Magenta", labels={"avg_price_per_m2_eur": "Price per m² (€)"})
        fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        st.plotly_chart(fig, width="stretch")

    
    # Daily rental yield — cool feature
    if not df_yield.empty:
        st.markdown("---")
        st.subheader("Daily rental yield at 60% occupancy (% p.a.)")
    
        top_y = df_yield.nlargest(10, 'yield_daily_percent').copy()

        top_y["Sector"] = top_y["city"] + " → " + top_y["sector"].fillna("Center")
    
        fig = px.bar(
            top_y,
            x="Sector",
            y="yield_daily_percent",
            text=top_y["yield_daily_percent"].round(1).astype(str),
            color="yield_daily_percent",
            color_continuous_scale="Viridis",
            labels={"yield_daily_percent": "%"}
        )
        fig.update_layout(height=600)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, width="stretch")
        


        st.markdown("---")
        st.markdown("<h2 style='text-align:center; color:#e0e0e0;'>Daily vs Monthly Rental — Moldova 2025 Reality</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Monthly Rent**")
            st.markdown("• €400–650 per month")
            st.markdown("• **6.5–9.1%** annual yield")
            st.markdown("• Stable • Low risk • True passive income")
        
        with col2:
            st.markdown("**Daily Rent** (60% occupancy)")
            st.markdown("• €900–1,400 monthly revenue")
            st.markdown("• **8–19%** annual yield")
            st.markdown("• Peak: **19.2%** (house + leisure zone)")
            st.markdown("• Higher costs • Seasonal")
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align:center; font-size:1.25rem; margin:1.5rem 0;'>"
            "Daily rent = <b>1.5–2× higher yield</b> vs monthly<br>"
            "<span style='color:#d32f2f; font-weight:600;'>19.2% max</span> — rare premium units"
            "</div>",
            unsafe_allow_html=True
        )

# =========================
# footer
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 3rem; color: #888; font-size: 0.95rem;">
&nbsp;&nbsp;&nbsp;&nbsp;<a href="mailto:sergey.revo@outlook.com" style="color:#888; text-decoration:none;">✉ sergey.revo@outlook.com</a><br><br>
&nbsp;&nbsp;&nbsp;&nbsp;<small>© 2025 - Imobil.Index</small>
</div>
""", unsafe_allow_html=True)
