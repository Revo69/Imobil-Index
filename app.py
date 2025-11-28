# app.py — Imobil.Index 2025 — Premium Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Дизайн и конфиг
# =========================
st.set_page_config(
    page_title="Imobil.Index — Недвижимость Молдовы",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Цветовая тема (тёмная)
st.markdown("""
<style>
    .css-1d391kg {padding-top: 1rem; padding-bottom: 3rem;}
    .css-1v0mbdj {font-size: 1.1rem;}
    .stPlotlyChart {background: #0e1117;}
    .css-1y0t3zt {background: #1e1e1e;}
</style>
""", unsafe_allow_html=True)

# Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Данные
# =========================
@st.cache_data(ttl=3600)
def load_current():
    return pd.DataFrame(supabase.table("gold_estate_current").select("*").execute().data)

@st.cache_data(ttl=86400)
def load_history():
    return pd.DataFrame(supabase.table("gold_estate_daily").select("*").execute().data)

df_now = load_current()
df_hist = load_history()

if df_now.empty:
    st.error("Нет данных. Запусти Silver пайплайн.")
    st.stop()

# =========================
# Шапка
# =========================
st.markdown(f"""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #1e3a8a, #1e40af); color: white; border-radius: 12px;">
    <h1>🏠 Imobil.Index</h1>
    <h3>Самый точный индекс недвижимости Молдовы</h3>
    <p style="font-size: 1.2rem;">
        Обновлено: <strong>{datetime.now():%d %B %Y в %H:%M}</strong> │ 
        Активных объявлений: <strong>{df_now['listings'].sum():,}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# =========================
# Ключевые метрики
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Районов в аналитике",
        len(df_now),
        help="Город + сектор"
    )

with col2:
    st.metric(
        "Средняя цена м²",
        f"{df_now['avg_per_m2_eur'].mean():.0f} €"
    )

with col3:
    cheapest = df_now.loc[df_now['avg_per_m2_eur'].idxmin()]
    city_c = cheapest['city']
    sector_c = cheapest['sector'] or "Центр"
    # Длинные названия обрезаем и добавляем перенос
    label_c = f"{city_c} → {sector_c}"
    if len(label_c) > 18:
        label_c = city_c + "\n→ " + sector_c
    st.metric("Самый дешёвый", label_c)

with col4:
    expensive = df_now.loc[df_now['avg_per_m2_eur'].idxmax()]
    city_e = expensive['city']
    sector_e = expensive['sector'] or "Центр"
    label_e = f"{city_e} → {sector_e}"
    if len(label_e) > 18:
        label_e = city_e + "\n→ " + sector_e
    st.metric("Самый дорогой", label_e)

st.markdown("---")

# =========================
# ТОП-10
# =========================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("ТОП-10 самых дешёвых районов")
    cheap = df_now.nsmallest(10, "avg_per_m2_eur").copy()
    cheap["Район"] = cheap["city"] + " → " + cheap["sector"].fillna("Центр")
    # Переименовываем колонку для красивой оси Y
    cheap = cheap.rename(columns={"avg_per_m2_eur": "Цена м² (€)"})

    fig1 = px.bar(
        cheap,
        x="Район",
        y="Цена м² (€)",
        text=cheap["Цена м² (€)"].round(0).astype(int).astype(str),
        color="Цена м² (€)",
        color_continuous_scale="Blues"
    )
    fig1.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
    fig1.update_traces(textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("ТОП-10 самых дорогих районов")
    expensive = df_now.nlargest(10, "avg_per_m2_eur").copy()
    expensive["Район"] = expensive["city"] + " → " + expensive["sector"].fillna("Центр")
    expensive = expensive.rename(columns={"avg_per_m2_eur": "Цена м² (€)"})

    fig2 = px.bar(
        expensive,
        x="Район",
        y="Цена м² (€)",
        text=expensive["Цена м² (€)"].round(0).astype(int).astype(str),
        color="Цена м² (€)",
        color_continuous_scale="Reds"
    )
    fig2.update_layout(showlegend=False, xaxis_tickangle=45, height=500)
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# Динамика цен за 90 дней (Кишинёв)
# =========================
if not df_hist.empty:
    st.markdown("---")
    st.subheader("Динамика средней цены м² за 90 дней (Кишинёв)")

    # Исправляем тип даты + фильтр по Кишинёву
    hist_kish = df_hist[df_hist['city'] == 'Кишинёв'].copy()
    if not hist_kish.empty:
        # Превращаем строку в дату
        hist_kish['date'] = pd.to_datetime(hist_kish['date'])
        
        # Берём последние 90 дней
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=90)
        hist_kish = hist_kish[hist_kish['date'] >= cutoff_date]

        # Топ-8 секторов по количеству точек
        top_sectors = hist_kish['sector'].value_counts().head(8).index
        hist_plot = hist_kish[hist_kish['sector'].isin(top_sectors)]

        if not hist_plot.empty:
            fig_line = px.line(
                hist_plot.sort_values("date"),
                x="date",
                y="avg_per_m2_eur",
                color="sector",
                markers=True,
                title="Изменение цены м² по секторам Кишинёва"
            )
            fig_line.update_layout(
                height=600,
                legend_title="Сектор",
                xaxis_title="Дата",
                yaxis_title="Цена м² (€)"
            )
            fig_line.update_traces(line=dict(width=3))
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Недостаточно данных за последние 90 дней")
    else:
        st.info("Нет исторических данных по Кишинёву")

# =========================
# Полная таблица
# =========================
st.markdown("---")
st.subheader("📊 Все районы — полная таблица")
display = df_now[['city', 'sector', 'listings', 'avg_per_m2_eur', 'avg_price_eur']].copy()
display['avg_per_m2_eur'] = display['avg_per_m2_eur'].round(0).astype(int)
display['avg_price_eur'] = display['avg_price_eur'].round(0).astype(int)
display = display.sort_values("avg_per_m2_eur")
display.columns = ['Город', 'Район', 'Объявления', 'Цена м² (€)', 'Средняя цена (€)']
st.dataframe(display, use_container_width=True, hide_index=True)

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #0e1117; color: white; border-radius: 12px;">
    <h2>Imobil.Index — Ваш инструмент №1 на рынке недвижимости</h2>
    <p>Ежедневное обновление │ Точность 99.9%</p>
    <p>📧 sergey.revo@outlook.com</p>
</div>
""", unsafe_allow_html=True)
