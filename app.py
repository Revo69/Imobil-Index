# app.py — Imobil.Index 2025 — Premium Dashboard (Продажа + Аренда + Доходность)
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Конфиг + Дизайн
# =========================
st.set_page_config(
    page_title="Imobil.Index — Недвижимость Молдовы 2025",
    page_icon="house",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .css-1d391kg {padding-top: 1rem;}
    .main-title {text-align: center; font-size: 2.6em; font-weight: 300; color: #e0e0e0; margin: 0.5em 0;}
    .subtitle {text-align: center; font-size: 1.15em; color: #bbbbbb; margin-bottom: 2em;}
    .stTabs [data-baseweb="tab"] {font-size: 1.15em; font-weight: 600;}
    .stPlotlyChart {background: #0e1117;}
</style>
""", unsafe_allow_html=True)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Загрузка данных (кэш 1 час)
# =========================
@st.cache_data(ttl=3600)
def load_sales_current():
    return pd.DataFrame(supabase.table("gold_estate_current").select("*").execute().data)

@st.cache_data(ttl=3600)
def load_rent_current():
    return pd.DataFrame(supabase.table("gold_rent_current").select("*").execute().data)

@st.cache_data(ttl=3600)
def load_rent_yield():
    return pd.DataFrame(supabase.table("gold_rent_yield").select("*").execute().data)

@st.cache_data(ttl=3600)
def load_sales_history():
    return pd.DataFrame(supabase.table("gold_estate_daily").select("*").execute().data)

@st.cache_data(ttl=3600)
def load_rent_history():
    return pd.DataFrame(supabase.table("gold_rent_daily").select("*").execute().data)

df_sales = load_sales_current()
df_rent = load_rent_current()
df_yield = load_rent_yield()
df_hist_sales = load_sales_history()
df_hist_rent = load_rent_history()

# =========================
# Шапка + Переключатель
# =========================
st.markdown("<div class='main-title'>Imobil.Index — Недвижимость Молдовы 2025</div>", unsafe_allow_html=True)

tab_sale, tab_rent = st.tabs(["Продажа", "Аренда"])

# --------------------- ПРОДАЖА ---------------------
with tab_sale:
    current_df = df_sales
    hist_df = df_hist_sales
    mode = "Продажа"
    price_col = "avg_per_m2_eur"
    color_cheap = "Blues"
    color_expensive = "Reds"
    listings_total = int(current_df['listings'].sum()) if not current_df.empty else 0

    st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {listings_total:,} активных объявлений │ Режим: <b>{mode}</b></div>", 
                unsafe_allow_html=True)
    st.markdown("---")

    if current_df.empty:
        st.error("Нет данных по продаже. Запусти Gold пайплайн.")
        st.stop()

    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Районов в аналитике", len(current_df))
    with col2:
        st.metric("Средняя цена м²", f"{current_df[price_col].mean():.0f} €")
    with col3:
        cheapest = current_df.loc[current_df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дешёвый</b><br>{cheapest['city']} → {cheapest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = current_df.loc[current_df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ТОП-10
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("ТОП-10 самых дешёвых районов")
        cheap = current_df.nsmallest(10, price_col).copy()
        cheap["Район"] = cheap["city"] + " → " + cheap["sector"].fillna("Центр")
        fig1 = px.bar(cheap, x="Район", y=price_col,
                      text=cheap[price_col].round(0).astype(int),
                      color=price_col, color_continuous_scale=color_cheap)
        fig1.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

    with col_r:
        st.subheader("ТОП-10 самых дорогих районов")
        exp = current_df.nlargest(10, price_col).copy()
        exp["Район"] = exp["city"] + " → " + exp["sector"].fillna("Центр")
        fig2 = px.bar(exp, x="Район", y=price_col,
                      text=exp[price_col].round(0).astype(int),
                      color=price_col, color_continuous_scale=color_expensive)
        fig2.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    # Динамика
    if not hist_df.empty:
        st.markdown("---")
        st.subheader("Динамика цены м² за 90 дней — Кишинёв")
        h = hist_df[hist_df['city'] == 'Кишинёв'].copy()
        if not h.empty:
            h['date'] = pd.to_datetime(h['date'])
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=90)
            h = h[h['date'] >= cutoff]
            top_sec = h['sector'].value_counts().head(8).index
            plot_data = h[h['sector'].isin(top_sec)]
            if not plot_data.empty:
                fig_line = px.line(plot_data.sort_values("date"), x="date", y=price_col,
                                   color="sector", markers=True,
                                   title="Изменение цены м² по секторам")
                fig_line.update_layout(height=600, legend_title="Сектор")
                st.plotly_chart(fig_line, use_container_width=True)

    # Полная таблица
    st.markdown("---")
    st.subheader("Все районы — Продажа")
    disp = current_df[['city','sector','listings','avg_per_m2_eur','avg_price_eur']].copy()
    disp['avg_per_m2_eur'] = disp['avg_per_m2_eur'].round(0).astype(int)
    disp['avg_price_eur'] = disp['avg_price_eur'].round(0).astype(int)
    disp = disp.sort_values('avg_per_m2_eur')
    disp.columns = ['Город','Район','Объявления','Цена м² (€)','Средняя цена (€)']
    st.dataframe(disp, use_container_width=True, hide_index=True)


# --------------------- АРЕНДА ---------------------
with tab_rent:
    current_df = df_rent[df_rent['deal_type'] == 'Сдаю помесячно']
    hist_df = df_hist_rent[df_hist_rent['deal_type'] == 'Сдаю помесячно']
    mode = "Аренда (помесячно)"
    price_col = "avg_price_per_m2_eur"
    color_cheap = "Greens"
    color_expensive = "Oranges"
    listings_total = int(current_df['listings'].sum()) if not current_df.empty else 0

    st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {listings_total:,} активных объявлений │ Режим: <b>{mode}</b></div>", 
                unsafe_allow_html=True)
    st.markdown("---")

    if current_df.empty:
        st.error("Нет данных по аренде. Запусти Gold пайплайн.")
        st.stop()

    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Районов в аналитике", len(current_df))
    with col2:
        st.metric("Средняя цена за м²", f"{current_df[price_col].mean():.1f} €/мес")
    with col3:
        cheapest = current_df.loc[current_df[price_col].idxmin()]
        st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дешёвый</b><br>{cheapest['city']} → {cheapest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
    with col4:
        expensive = current_df.loc[current_df[price_col].idxmax()]
        st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ТОП-10
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("ТОП-10 самых дешёвых районов")
        cheap = current_df.nsmallest(10, price_col).copy()
        cheap["Район"] = cheap["city"] + " → " + cheap["sector"].fillna("Центр")
        fig1 = px.bar(cheap, x="Район", y=price_col,
                      text=cheap[price_col].round(1),
                      color=price_col, color_continuous_scale=color_cheap)
        fig1.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

    with col_r:
        st.subheader("ТОП-10 самых дорогих районов")
        exp = current_df.nlargest(10, price_col).copy()
        exp["Район"] = exp["city"] + " → " + exp["sector"].fillna("Центр")
        fig2 = px.bar(exp, x="Район", y=price_col,
                      text=exp[price_col].round(1),
                      color=price_col, color_continuous_scale=color_expensive)
        fig2.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    # Динамика
    if not hist_df.empty:
        st.markdown("---")
        st.subheader("Динамика цены м² за 90 дней — Аренда (Кишинёв)")
        h = hist_df[hist_df['city'] == 'Кишинёв'].copy()
        if not h.empty:
            h['date'] = pd.to_datetime(h['date'])
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=90)
            h = h[h['date'] >= cutoff]
            top_sec = h['sector'].value_counts().head(8).index
            plot_data = h[h['sector'].isin(top_sec)]
            if not plot_data.empty:
                fig_line = px.line(plot_data.sort_values("date"), x="date", y=price_col,
                                   color="sector", markers=True)
                fig_line.update_layout(height=600, legend_title="Сектор")
                st.plotly_chart(fig_line, use_container_width=True)

    # Доходность аренды
    if not df_yield.empty:
        st.markdown("---")
        st.subheader("Доходность аренды — сколько % годовых приносит сдача")
        top_y = df_yield.nlargest(10, 'rent_yield_percent').copy()
        top_y["Район"] = top_y["sector"].fillna("Центр")
        fig_y = px.bar(top_y, x="Район", y="rent_yield_percent",
                       text=top_y["rent_yield_percent"].round(2).astype(str) + "%",
                       color="rent_yield_percent", color_continuous_scale="Viridis")
        fig_y.update_traces(textposition='outside')
        fig_y.update_layout(height=550, xaxis_tickangle=45)
        st.plotly_chart(fig_y, use_container_width=True)

    # Полная таблица
    st.markdown("---")
    st.subheader("Все районы — Аренда")
    disp = current_df[['city','sector','listings','avg_price_per_m2_eur','avg_price_eur']].copy()
    disp['avg_price_per_m2_eur'] = disp['avg_price_per_m2_eur'].round(1)
    disp['avg_price_eur'] = disp['avg_price_eur'].round(0).astype(int)
    disp = disp.sort_values('avg_price_per_m2_eur')
    disp.columns = ['Город','Район','Объявления','Цена м² (€/мес)','Средняя цена (€/мес)']
    st.dataframe(disp, use_container_width=True, hide_index=True)

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 3rem 1rem 2rem; color: #888; font-size: 0.95rem;">
    <strong>Revoland Analytics</strong> • 
    <a href="mailto:sergey.revo@outlook.com" style="color:#888; text-decoration:none;">sergey.revo@outlook.com</a> • 
    Аналитика недвижимости Молдовы<br><br>
    <small>© {datetime.now().year} — Все права защищены</small>
</div>
""", unsafe_allow_html=True)
