import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# =========================
# Конфиг и подключение
# =========================
st.set_page_config(
    page_title="Imobil.Index — Аналитика недвижимости Молдовы",
    page_icon="house",
    layout="wide"
)

# Секреты добавишь в Streamlit Cloud → Settings → Secrets
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# Загрузка данных
# =========================
@st.cache_data(ttl=3600)  # обновляется каждый час
def load_current():
    resp = supabase.table("gold_estate_current").select("*").execute()
    return pd.DataFrame(resp.data)

@st.cache_data(ttl=86400)  # ежедневно
def load_history():
    resp = supabase.table("gold_estate_daily").select("*").execute()
    return pd.DataFrame(resp.data)

df_now = load_current()
df_hist = load_history()

# Если пусто — защита
if df_now.empty:
    st.error("Нет данных в gold_estate_current. Запусти refresh_gold_estate()")
    st.stop()

# =========================
# Шапка
# =========================
st.title("Imobil.Index — Недвижимость Молдовы 2025")
st.markdown(f"**Обновлено:** {datetime.now():%d %B %Y в %H:%M} │ {df_now['listings'].sum():,} активных объявлений")

# =========================
# Ключевые метрики
# =========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Районов в аналитике", len(df_now))
col2.metric("Средняя цена м²", f"{df_now['avg_per_m2_eur'].mean():.0f} €")
col3.metric("Самый дешёвый", f"{df_now.loc[df_now['avg_per_m2_eur'].idxmin(), 'sector'] or '—'}")
col4.metric("Самый дорогой", f"{df_now.loc[df_now['avg_per_m2_eur'].idxmax(), 'sector'] or '—'}")

st.divider()

# =========================
# ТОП-10 дешёвых и дорогих
# =========================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("ТОП-10 самых дешёвых районов")
    cheap = df_now.nsmallest(10, "avg_per_m2_eur").copy()
    cheap["Район"] = cheap["city"] + cheap["sector"].fillna("").apply(lambda x: f" → {x}" if x else "")
    fig_cheap = px.bar(
        cheap, x="Район", y="avg_per_m2",
        text=cheap["avg_per_m2_eur"].round(0).astype(int).astype(str) + "€",
        color="avg_per_m2_eur", color_continuous_scale="Blues"
    )
    fig_cheap.update_layout(showlegend=False, xaxis_tickangle=45)
    fig_cheap.update_traces(textposition='outside')
    st.plotly_chart(fig_cheap, use_container_width=True)

with col_right:
    st.subheader("ТОП-10 самых дорогих районов")
    expensive = df_now.nlargest(10, "avg_per_m2_eur").copy()
    expensive["Район"] = expensive["city"] + expensive["sector"].fillna("").apply(lambda x: f" → {x}" if x else "")
    fig_exp = px.bar(
        expensive, x="Район", y="avg_per_m2_eur",
        text=expensive["avg_per_m2_eur"].round(0).astype(int).astype(str) + "€",
        color="avg_per_m2_eur", color_continuous_scale="Reds"
    )
    fig_exp.update_layout(showlegend=False, xaxis_tickangle=45)
    fig_exp.update_traces(textposition='outside')
    st.plotly_chart(fig_exp, use_container_width=True)

# =========================
# Интерактивный фильтр + динамика
# =========================
st.divider()
st.subheader("Динамика цен по секторам Кишинёва (90 дней)")

# Фильтр городов
cities = ["Все"] + sorted(df_hist['city'].unique().tolist())
selected_city = st.selectbox("Город", cities, index=cities.index("Кишинёв") if "Кишинёв" in cities else 0)

if selected_city == "Все":
    hist_filtered = df_hist.copy()
else:
    hist_filtered = df_hist[df_hist['city'] == selected_city]

# Только сектора с данными за последние 90 дней
recent_sectors = hist_filtered[
    hist_filtered['date'] >= pd.Timestamp.now() - pd.Timedelta(days=90)
]['sector'].dropna().unique()

if len(recent_sectors) == 0:
    st.info("Нет исторических данных за 90 дней")
else:
    sector_options = st.multiselect("Сектора", options=sorted(recent_sectors), default=sorted(recent_sectors)[:6])
    if sector_options:
        plot_df = hist_filtered[
            (hist_filtered['sector'].isin(sector_options)) &
            (hist_filtered['date'] >= pd.Timestamp.now() - pd.Timedelta(days=90))
        ]
        fig_line = px.line(
            plot_df, x="date", y="avg_per_m2", color="sector",
            markers=True, title=f"Цена м² в {selected_city}"
        )
        fig_line.update_traces(line=dict(width=3))
        st.plotly_chart(fig_line, use_container_width=True)

# =========================
# Полная таблица
# =========================
st.divider()
st.subheader("Все районы — полная таблица")
display_df = df_now[['city', 'sector', 'listings', 'avg_per_m2_eur', 'avg_price_eur']].copy()
display_df['avg_per_m2_eur'] = display_df['avg_per_m2_eur'].round(0).astype(int)
display_df['avg_price_eur'] = display_df['avg_price_eur'].round(0).astype(int)
display_df = display_df.sort_values("avg_per_m2_eur")
st.dataframe(display_df, use_container_width=True)

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown(
    "Revoland Analytics │ "
    "sergey.revo@outlook.com"
)
