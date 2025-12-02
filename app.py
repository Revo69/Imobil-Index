# app.py — Imobil.Index 2025 — Продажа + Помесячная + Посуточная аренда
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Конфиг
# =========================
st.set_page_config(page_title="Imobil.Index 2025", page_icon="house", layout="wide")
st.markdown("""
<style>
    .main-title {text-align: center; font-size: 2.8em; font-weight: 300; color: #e0e0e0; margin: 0.5em 0;}
    .subtitle {text-align: center; font-size: 1.2em; color: #bbbbbb; margin-bottom: 2em;}
    .stTabs [data-baseweb="tab"] {font-size: 1.2em; font-weight: 600; padding: 1rem 2rem;}
</style>
""", unsafe_allow_html=True)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Данные (кэш 1 час)
# =========================
@st.cache_data(ttl=3600)
def load_data():
    sales = pd.DataFrame(supabase.table("gold_estate_current").select("*").execute().data)
    rent = pd.DataFrame(supabase.table("gold_rent_current").select("*").execute().data)
    yield_data = pd.DataFrame(supabase.table("gold_rent_yield").select("*").execute().data)
    hist_sales = pd.DataFrame(supabase.table("gold_estate_daily").select("*").execute().data)
    hist_rent = pd.DataFrame(supabase.table("gold_rent_daily").select("*").execute().data)
    return sales, rent, yield_data, hist_sales, hist_rent

df_sales, df_rent, df_yield, df_hist_sales, df_hist_rent = load_data()

# =========================
# Шапка
# =========================
st.markdown("<div class='main-title'>Imobil.Index — Недвижимость Молдовы 2025</div>", unsafe_allow_html=True)

tab_sale, tab_rent_monthly, tab_rent_daily = st.tabs(["Продажа", "Аренда (помесячно)", "Посуточная аренда"])

# --------------------- 1. ПРОДАЖА ---------------------
with tab_sale:
    df = df_sales.copy()
    mode = "Продажа"
    price_col = "avg_per_m2_eur"
    hist = df_hist_sales
    color = "Blues"
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} объявлений</div>", unsafe_allow_html=True)
    if df.empty: st.error("Нет данных по продаже"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Районов", len(df))
    with col2: st.metric("Средняя цена м²", f"{df[price_col].mean():.0f} €")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Самый дешёвый</b><br>{cheapest['city']} → {cheapest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("ТОП-10 самых дешёвых")
        top = df.nsmallest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale=color)
        fig.update_traces(texttemplate='%{y:.0f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("ТОП-10 самых дорогих")
        top = df.nlargest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale="Reds")
        fig.update_traces(texttemplate='%{y:.0f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    if not hist.empty:
        st.markdown("---")
        st.subheader("Динамика цены м² за 90 дней — Кишинёв")
        h = hist[hist['city'] == 'Кишинёв'].copy()
        if not h.empty:
            h['date'] = pd.to_datetime(h['date'])
            h = h[h['date'] >= pd.Timestamp.now() - pd.Timedelta(days=90)]
            top_sec = h['sector'].value_counts().head(8).index
            plot = h[h['sector'].isin(top_sec)]
            if not plot.empty:
                fig = px.line(plot.sort_values("date"), x="date", y=price_col, color="sector", markers=True)
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Все районы")
    disp = df[['city','sector','listings','avg_per_m2_eur','avg_price_eur']].copy()
    disp['avg_per_m2_eur'] = disp['avg_per_m2_eur'].round(0).astype(int)
    disp['avg_price_eur'] = disp['avg_price_eur'].round(0).astype(int)
    disp = disp.sort_values('avg_per_m2_eur')
    disp.columns = ['Город','Район','Объявления','Цена м² (€)','Средняя цена (€)']
    st.dataframe(disp, use_container_width=True, hide_index=True)

# --------------------- 2. АРЕНДА ПОМЕСЯЧНО ---------------------
with tab_rent_monthly:
    df = df_rent[df_rent['deal_type'] == 'Сдаю помесячно'].copy()
    mode = "Аренда (помесячно)"
    price_col = "avg_price_per_m2_eur"
    hist = df_hist_rent[df_hist_rent['deal_type'] == 'Сдаю помесячно']
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} объявлений</div>", unsafe_allow_html=True)
    if df.empty: st.error("Нет данных по помесячной аренде"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Районов", len(df))
    with col2: st.metric("Средняя цена за м²", f"{df[price_col].mean():.1f} €/мес")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Самый дешёвый</b><br>{cheapest['city']} → {cheapest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("ТОП-10 самых дешёвых")
        top = df.nsmallest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale="Greens")
        fig.update_traces(texttemplate='%{y:.1f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("ТОП-10 самых дорогих")
        top = df.nlargest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale="Oranges")
        fig.update_traces(texttemplate='%{y:.1f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Доходность помесячной
    if not df_yield.empty:
        st.markdown("---")
        st.subheader("Доходность помесячной аренды — % годовых")
        top_y = df_yield.nlargest(10, 'yield_monthly_percent').copy()
        top_y["Район"] = top_y["sector"].fillna("Центр")
        fig = px.bar(top_y, x="Район", y="yield_monthly_percent",
                     text=top_y["yield_monthly_percent"].round(1).astype(str)+"%",
                     color="yield_monthly_percent", color_continuous_scale="Blues")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# --------------------- 3. ПОСУТОЧНАЯ АРЕНДА ---------------------
with tab_rent_daily:
    df = df_rent[df_rent['deal_type'] == 'Сдаю посуточно'].copy()
    mode = "Посуточная аренда"
    price_col = "avg_price_per_m2_eur"
    listings = int(df['listings'].sum()) if not df.empty else 0

    st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {listings:,} объявлений</div>", unsafe_allow_html=True)
    if df.empty: st.error("Нет данных по посуточной аренде"); st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Районов", len(df))
    with col2: st.metric("Средняя цена за м²", f"{df[price_col].mean():.1f} €/сутки")
    with col3:
        cheapest = df.loc[df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center'><b>Самый дешёвый</b><br>{cheapest['city']} → {cheapest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = df.loc[df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("ТОП-10 самых дешёвых")
        top = df.nsmallest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale="Purples")
        fig.update_traces(texttemplate='%{y:.1f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("ТОП-10 самых дорогих")
        top = df.nlargest(10, price_col).copy()
        top["Район"] = top["city"] + " → " + top["sector"].fillna("Центр")
        fig = px.bar(top, x="Район", y=price_col, color=price_col, color_continuous_scale="Magenta")
        fig.update_traces(texttemplate='%{y:.1f}€', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    
    # Доходность посуточной — САМАЯ КРУТАЯ ФИЧА
    if not df_yield.empty:
        st.markdown("---")
        st.subheader("Доходность посуточной аренды — % годовых (60% загрузка)")
        top_y = df_yield.nlargest(10, 'yield_daily_percent').copy()
        top_y["Район"] = top_y["sector"].fillna("Центр")
        fig = px.bar(top_y, x="Район", y="yield_daily_percent",
                     text=top_y["yield_daily_percent"].round(1).astype(str)+"%",
                     color="yield_daily_percent", color_continuous_scale="Viridis")
        fig.update_layout(height=600)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)



        st.markdown("---")
        st.markdown("<h2 style='text-align:center; color:#e0e0e0;'>Посуточная vs Помесячная аренда — реальность 2025</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Помесячная аренда**")
            st.markdown("• 400–650 €/мес за квартиру")
            st.markdown("• **6.5–9.1%** годовых")
            st.markdown("• Стабильно • Низкие риски")
            st.markdown("• Лучший пассивный доход")
        
        with col2:
            st.markdown("**Посуточная аренда** (60% загрузка)")
            st.markdown("• Обычные квартиры: 900–1 400 €/мес")
            st.markdown("• **8–19%** годовых")
            st.markdown("• БАМ: до **109%** (дома с зоной отдыха)")
            st.markdown("• Высокие расходы • Сезонность")
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align:center; font-size:1.25rem; color:#aaa; margin:1.5rem 0;'>"
            "Для обычной квартиры посуточная аренда даёт <b>в 1.5–2 раза выше доходность</b><br>"
            "109% на БАМ — редкие премиум-объекты (менее 1% рынка)"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("Реалистичная доходность посуточной аренды: **8–19%** годовых")
        st.markdown("<span style='color:#ff6b6b;'>109% на БАМ</span> — дома с баней (менее 1% рынка)", unsafe_allow_html=True)
        st.markdown("---")
        
# =========================
# Футер
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 3rem; color: #888; font-size: 0.95rem;">
    <strong>Revoland Analytics</strong> • 
    <a href="mailto:sergey.revo@outlook.com" style="color:#888; text-decoration:none;">sergey.revo@outlook.com</a><br><br>
    <small>© 2025 — Imobil.Index — аналитика недвижимости Молдовы</small>
</div>
""", unsafe_allow_html=True)
