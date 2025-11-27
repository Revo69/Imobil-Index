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

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]  # лучше использовать service_role только на сервере
)

# =========================
# Функция обновления
# =========================
def refresh_gold_estate():
    try:
        resp = supabase.rpc("refresh_gold_estate").execute()
        if hasattr(resp, "error") and resp.error:
            st.error(f"Ошибка при обновлении: {resp.error}")
            return False
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

# =========================
# Загрузка данных
# =========================
@st.cache_data(ttl=3600)
def load_current():
    resp = supabase.table("gold_estate_current").select("*").execute()
    return pd.DataFrame(resp.data)

@st.cache_data(ttl=86400)
def load_history():
    resp = supabase.table("gold_estate_daily").select("*").execute()
    return pd.DataFrame(resp.data)

df_now = load_current()
df_hist = load_history()

# =========================
# Если пусто — запускаем обновление
# =========================
if df_now.empty:
    st.warning("Нет данных в gold_estate_current")
    with st.spinner("Обновляем данные..."):
        if refresh_gold_estate():
            st.success("✅ Данные обновлены, перезапускаем дашборд")
            st.rerun()
        else:
            st.stop()

# =========================
# Шапка с кнопкой обновления
# =========================
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("🏠 Imobil.Index — Аналитика недвижимости Молдовы")

with col_refresh:
    st.write("")  # отступ
    if st.button("🔄 Обновить данные", type="primary"):
        with st.spinner("Обновляем данные..."):
            if refresh_gold_estate():
                st.rerun()

st.markdown(f"📅 Обновлено: {datetime.now():%d %B %Y в %H:%M} │ 📊 {df_now['listings'].sum():,} активных объявлений")

# =========================
# Ключевые метрики
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("🏙️ Районов в аналитике", len(df_now))
col2.metric("💰 Средняя цена м²", f"{df_now['avg_per_m2_eur'].mean():.0f} €")

min_row = df_now.loc[df_now['avg_per_m2_eur'].idxmin()]
max_row = df_now.loc[df_now['avg_per_m2_eur'].idxmax()]

min_city = str(min_row['city'])
min_sector = str(min_row['sector']) if pd.notna(min_row['sector']) else "—"

max_city = str(max_row['city'])
max_sector = str(max_row['sector']) if pd.notna(max_row['sector']) else "—"

col3.metric("📉 Самый дешёвый", min_city, delta=f"{min_sector}")
col4.metric("📈 Самый дорогой", max_city, delta=f"{max_sector}")



st.divider()

# =========================
# ТОП-10 дешёвых и дорогих
# =========================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 ТОП-10 самых дешёвых районов")
    cheap = df_now.nsmallest(10, "avg_per_m2_eur").copy()
    cheap["Район"] = cheap["city"].str.cat(cheap["sector"].fillna("центр"), sep=" → ")
    fig_cheap = px.bar(
        cheap, x="Район", y="avg_per_m2_eur",
        text=cheap["avg_per_m2_eur"].round(0).astype(int).astype(str) + " €",
        color="avg_per_m2_eur", color_continuous_scale="Blues"
    )
    fig_cheap.update_layout(showlegend=False, xaxis_tickangle=45)
    fig_cheap.update_traces(textposition='outside')
    st.plotly_chart(fig_cheap, use_container_width=True)

with col_right:
    st.subheader("💎 ТОП-10 самых дорогих районов")
    expensive = df_now.nlargest(10, "avg_per_m2_eur").copy()
    expensive["Район"] = expensive["city"].str.cat(expensive["sector"].fillna("центр"), sep=" → ")
    fig_exp = px.bar(
        expensive, x="Район", y="avg_per_m2_eur",
        text=expensive["avg_per_m2_eur"].round(0).astype(int).astype(str) + " €",
        color="avg_per_m2_eur", color_continuous_scale="Reds"
    )
    fig_exp.update_layout(showlegend=False, xaxis_tickangle=45)
    fig_exp.update_traces(textposition='outside')
    st.plotly_chart(fig_exp, use_container_width=True)

# =========================
# Полная таблица
# =========================
st.divider()
st.subheader("📋 Все районы — полная таблица")

display_df = df_now[['city', 'sector', 'listings', 'avg_per_m2_eur', 'avg_price_eur']].copy()
display_df['avg_per_m2_eur'] = display_df['avg_per_m2_eur'].round(0).astype(int)
display_df['avg_price_eur'] = display_df['avg_price_eur'].round(0).astype(int)
display_df = display_df.sort_values("avg_per_m2_eur")
display_df.columns = ['Город', 'Район', 'Объявления', 'Цена м² (€)', 'Средняя цена (€)']

st.dataframe(display_df, use_container_width=True)

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown("**Revoland Analytics** │ 📧 sergey.revo@outlook.com │ 🏠 Аналитика недвижимости Молдовы")
