# app.py — Imobil.Index 2025 — Premium Dashboard (Продажа + Аренда)
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Конфиг
# =========================
st.set_page_config(
    page_title="Imobil.Index — Недвижимость Молдовы",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Тёмная тема + кастом
st.markdown("""
<style>
    .css-1d391kg {padding-top: 1rem; padding-bottom: 3rem;}
    .stPlotlyChart {background: #0e1117;}
    .main-title {text-align: center; font-size: 2.4em; font-weight: 300; color: #e0e0e0; margin: 0.5em 0;}
    .subtitle {text-align: center; font-size: 1.1em; color: #aaaaaa; margin-bottom: 2em;}
    .stTabs [data-baseweb="tab"] {font-size: 1.1em; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Данные (с кэшем)
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
def load_history():
    return pd.DataFrame(supabase.table("gold_estate_daily").select("*").execute().data)

@st.cache_data(ttl=3600)
def load_rent_history():
    return pd.DataFrame(supabase.table("gold_rent_daily").select("*").execute().data)

# Загружаем всё
df_sales = load_sales_current()
df_rent = load_rent_current()
df_yield = load_rent_yield()
df_hist_sales = load_history()
df_hist_rent = load_rent_history()

# =========================
# Шапка
# =========================
st.markdown("<div class='main-title'>Imobil.Index — Недвижимость Молдовы 2025</div>", unsafe_allow_html=True)

# Переключатель: Продажа / Аренда
tab1, tab2 = st.tabs(["Продажа", "Аренда"])

with tab1:
    current_df = df_sales
    hist_df = df_hist_sales
    mode = "Продажа"
    color_scheme = "Blues"
    color_scheme_expensive = "Reds"
    price_col = "avg_per_m2_eur"
    total_listings = current_df['listings'].sum() if not current_df.empty else 0

with tab2:
    current_df = df_rent[df_rent['deal_type'] == 'Сдаю помесячно']
    hist_df = df_hist_rent[df_hist_rent['deal_type'] == 'Сдаю помесячно']
    mode = "Аренда (помесячно)"
    color_scheme = "Greens"
    color_scheme_expensive = "Blues"
    price_col = "avg_price_per_m2_eur"
    total_listings = current_df['listings'].sum() if not current_df.empty else 0

st.markdown(f"<div class='subtitle'>Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {total_listings:,} активных объявлений │ Режим: <b>{mode}</b></div>", 
            unsafe_allow_html=True)
st.markdown("---")

if current_df.empty:
    st.error(f"Нет данных по {mode.lower()}. Запусти Gold пайплайн.")
    st.stop()

# =========================
# Ключевые метрики
# =========================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Районов в аналитике", len(current_df))
with col2:
    avg_m2 = current_df[price_col].mean()
    if mode.startswith("Аренда"):
        st.metric("Средняя цена за м²", f"{avg_m2:.1f} €/мес")
    else:
        st.metric("Средняя цена м²", f"{avg_m2:.0f} €")
with col3:
    cheapest = current_df.loc[current_df[price_col].idxmin()]
    st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дешёвый</b><br>{cheaviest['city']} → {cheaviest['sector'] or 'Центр'}</div>", unsafe_allow_html=True)
with col4:
    expensive = current_df.loc[current_df[price_col].idxmax()]
    st.markdown(f"<div style='text-align:center; font-size:1.1em;'><b>Самый дорогой</b><br>{expensive['city']} → {expensive['sector'] or 'Центр'}</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================
# ТОП-10
# =========================
col_left, col_right = st.columns(2)
with col_left:
    st.subheader(f"ТОП-10 самых дешёвых районов — {mode}")
    cheap = current_df.nsmallest(10, price_col).copy()
    cheap["Район"] = cheap["city"] + " → " + cheap["sector"].fillna("Центр")
    fig1 = px.bar(
        cheap, x="Район", y=price_col,
        text=cheap[price_col].round(1).astype(str),
        color=price_col, color_continuous_scale=color_scheme
    )
    fig1.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
    fig1.update_traces(textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader(f"ТОП-10 самых дорогих районов — {mode}")
    exp = current_df.nlargest(10, price_col).copy()
    exp["Район"] = exp["city"] + " → " + exp["sector"].fillna("Центр")
    fig2 = px.bar(
        exp, x="Район", y=price_col,
        text=exp[price_col].round(1).astype(str),
        color=price_col, color_continuous_scale=color_scheme_expensive
    )
    fig2.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# Динамика цен
# =========================
if not hist_df.empty:
    st.markdown("---")
    st.subheader(f"Динамика цены м² за 90 дней — {mode} (Кишинёв)")
    hist_kish = hist_df[hist_df['city'] == 'Кишинёв'].copy()
    if not hist_kish.empty:
        hist_kish['date'] = pd.to_datetime(hist_kish['date'])
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=90)
        hist_kish = hist_kish[hist_kish['date'] >= cutoff]
        top_sectors = hist_kish['sector'].value_counts().head(8).index
        plot_data = hist_kish[hist_kish['sector'].isin(top_sectors)]
        if not plot_data.empty:
            fig_line = px.line(
                plot_data.sort_values("date"),
                x="date", y=price_col, color="sector",
                markers=True,
                title=f"Изменение цены м² по секторам Кишинёва — {mode}"
            )
            fig_line.update_layout(height=600, legend_title="Сектор")
            st.plotly_chart(fig_line, use_container_width=True)

# =========================
# Только в Аренде: Доходность
# =========================
if tab2 and not df_yield.empty:
    st.markdown("---")
    st.subheader("Доходность аренды — сколько % годовых приносит сдача")
    yield_top = df_yield.nlargest(10, 'rent_yield_percent').copy()
    yield_top["Район"] = yield_top["sector"].fillna("Центр")
    fig_yield = px.bar(
        yield_top,
        x="Район",
        y="rent_yield_percent",
        text=yield_top["rent_yield_percent"].round(2).astype(str) + "%",
        color="rent_yield_percent",
        color_continuous_scale="Viridis",
        title="ТОП-10 районов по доходности аренды (годовых)"
    )
    fig_yield.update_traces(textposition='outside')
    fig_yield.update_layout(height=550, xaxis_tickangle=45)
    st.plotly_chart(fig_yield, use_container_width=True)

# =========================
# Полная таблица
# =========================
st.markdown("---")
st.subheader(f"Все районы — {mode}")
display = current_df[['city', 'sector', 'listings', price_col, 'avg_price_eur']].copy()
display[price_col] = display[price_col].round(1)
display['avg_price_eur'] = display['avg_price_eur'].round(0).astype(int)
display = display.sort_values(price_col)
display.columns = ['Город', 'Район', 'Объявления', 'Цена м²', 'Средняя цена (€)']
st.dataframe(display, use_container_width=True, hide_index=True)

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 3rem 1rem 2rem; color: #888; font-size: 0.9rem;">
    <strong>Revoland Analytics</strong> • 
    <a href="mailto:sergey.revo@outlook.com" style="color: #888; text-decoration: none;">sergey.revo@outlook.com</a> • 
    Аналитика недвижимости Молдовы<br><br>
    <small>© {datetime.now().year} — Все права защищены</small>
</div>
""", unsafe_allow_html=True)
