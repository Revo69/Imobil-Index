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

# Используем SERVICE_ROLE ключ для полного доступа
supabase = create_client(
    st.secrets["SUPABASE_URL"], 
    st.secrets["SUPABASE_SERVICE_KEY"]  # Изменил на SERVICE_KEY
)

# =========================
# Функция для запуска обновления данных
# =========================
def refresh_gold_estate():
    try:
        response = supabase.rpc('refresh_gold_estate').execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Ошибка при обновлении: {response.error}")
            return False
        else:
            st.success("✅ Данные успешно обновлены!")
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"❌ Ошибка: {str(e)}")
        return False

# =========================
# Загрузка данных
# =========================
@st.cache_data(ttl=3600)
def load_current():
    try:
        resp = supabase.table("gold_estate_current").select("*").execute()
        return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Ошибка загрузки текущих данных: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def load_history():
    try:
        resp = supabase.table("gold_estate_daily").select("*").execute()
        return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Ошибка загрузки исторических данных: {e}")
        return pd.DataFrame()

# Загружаем данные
df_now = load_current()
df_hist = load_history()

# =========================
# Шапка с кнопкой обновления
# =========================
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("🏠 Imobil.Index — Аналитика недвижимости Молдовы")
    
with col_refresh:
    st.write("")  # Отступ
    if st.button("🔄 Обновить данные", type="primary"):
        with st.spinner("Обновляем данные..."):
            success = refresh_gold_estate()
            if success:
                st.rerun()

if not df_now.empty:
    st.markdown(f"📅 Обновлено: {datetime.now():%d %B %Y в %H:%M} │ 📊 {df_now['listings'].sum():,} активных объявлений")
else:
    st.warning("Нет данных для отображения")

# =========================
# Если данных нет - показываем кнопку принудительного обновления
# =========================
if df_now.empty:
    st.error("❌ Нет данных в gold_estate_current")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🚀 Запустить первичное обновление", type="secondary"):
            with st.spinner("Запускаем обновление данных..."):
                success = refresh_gold_estate()
                if success:
                    st.rerun()
    
    with col2:
        st.info("""
        **Что делает кнопка обновления:**
        - Запускает функцию `refresh_gold_estate()` в Supabase
        - Обрабатывает данные из таблицы `silver_estate`
        - Заполняет аналитическую таблицу `gold_estate_current`
        - Автоматически обновляет дашборд
        """)
    
    st.stop()

# =========================
# Ключевые метрики
# =========================
col1, col2, col3, col4 = st.columns(4)

total_listings = df_now['listings'].sum()
avg_price_m2 = df_now['avg_per_m2_eur'].mean()
min_sector = df_now.loc[df_now['avg_per_m2_eur'].idxmin(), 'sector']
max_sector = df_now.loc[df_now['avg_per_m2_eur'].idxmax(), 'sector']

col1.metric("🏙️ Районов в аналитике", len(df_now))
col2.metric("💰 Средняя цена м²", f"{avg_price_m2:.0f} €")
col3.metric("📉 Самый дешёвый", f"{min_sector}" if min_sector else "—")
col4.metric("📈 Самый дорогой", f"{max_sector}" if max_sector else "—")

st.divider()

# =========================
# ТОП-10 дешёвых и дорогих
# =========================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 ТОП-10 самых дешёвых районов")
    cheap = df_now.nsmallest(10, "avg_per_m2_eur").copy()
    cheap["Район"] = cheap["city"] + " → " + cheap["sector"].fillna("центр")
    
    fig_cheap = px.bar(
        cheap, 
        x="Район", 
        y="avg_per_m2_eur", 
        text=cheap["avg_per_m2_eur"].round(0).astype(int).astype(str) + " €",
        color="avg_per_m2_eur",
        color_continuous_scale="blugrn"
    )
    fig_cheap.update_layout(
        showlegend=False, 
        xaxis_tickangle=45,
        yaxis_title="Цена за м² (€)",
        xaxis_title=""
    )
    fig_cheap.update_traces(textposition='outside')
    st.plotly_chart(fig_cheap, use_container_width=True)

with col_right:
    st.subheader("💎 ТОП-10 самых дорогих районов")
    expensive = df_now.nlargest(10, "avg_per_m2_eur").copy()
    expensive["Район"] = expensive["city"] + " → " + expensive["sector"].fillna("центр")
    
    fig_exp = px.bar(
        expensive, 
        x="Район", 
        y="avg_per_m2_eur", 
        text=expensive["avg_per_m2_eur"].round(0).astype(int).astype(str) + " €",
        color="avg_per_m2_eur", 
        color_continuous_scale="reds"
    )
    fig_exp.update_layout(
        showlegend=False, 
        xaxis_tickangle=45,
        yaxis_title="Цена за м² (€)",
        xaxis_title=""
    )
    fig_exp.update_traces(textposition='outside')
    st.plotly_chart(fig_exp, use_container_width=True)

# =========================
# Распределение цен по городам
# =========================
st.divider()
st.subheader("📊 Распределение цен по городам")

city_stats = df_now.groupby('city').agg({
    'listings': 'sum',
    'avg_per_m2_eur': 'mean',
    'avg_price_eur': 'mean'
}).round(0).reset_index()
city_stats = city_stats.sort_values('avg_per_m2_eur', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_city = px.bar(
        city_stats,
        x='city',
        y='avg_per_m2_eur',
        text=city_stats['avg_per_m2_eur'].astype(int).astype(str) + ' €',
        title='Средняя цена за м² по городам',
        color='avg_per_m2_eur',
        color_continuous_scale='viridis'
    )
    fig_city.update_layout(xaxis_tickangle=45)
    fig_city.update_traces(textposition='outside')
    st.plotly_chart(fig_city, use_container_width=True)

with col2:
    fig_listings = px.pie(
        city_stats,
        values='listings',
        names='city',
        title='Распределение объявлений по городам',
        hole=0.4
    )
    st.plotly_chart(fig_listings, use_container_width=True)

# =========================
# Интерактивный фильтр
# =========================
st.divider()
st.subheader("🔍 Детальный анализ по районам")

cities = ["Все"] + sorted(df_now['city'].unique().tolist())
selected_city = st.selectbox("Выберите город:", cities)

if selected_city == "Все":
    filtered_df = df_now
else:
    filtered_df = df_now[df_now['city'] == selected_city]

min_price = int(filtered_df['avg_per_m2_eur'].min())
max_price = int(filtered_df['avg_per_m2_eur'].max())
price_range = st.slider(
    "Диапазон цен за м² (€):",
    min_price, max_price, (min_price, max_price)
)

filtered_df = filtered_df[
    (filtered_df['avg_per_m2_eur'] >= price_range[0]) & 
    (filtered_df['avg_per_m2_eur'] <= price_range[1])
]

# =========================
# Полная таблица
# =========================
st.subheader(f"📋 Таблица данных ({len(filtered_df)} районов)")

display_df = filtered_df[[
    'city', 'sector', 'listings', 'avg_per_m2_eur', 'avg_price_eur'
]].copy()

display_df['avg_per_m2_eur'] = display_df['avg_per_m2_eur'].round(0).astype(int)
display_df['avg_price_eur'] = display_df['avg_price_eur'].round(0).astype(int)
display_df = display_df.sort_values("avg_per_m2_eur")
display_df.columns = ['Город', 'Район', 'Объявления', 'Цена м² (€)', 'Средняя цена (€)']

st.dataframe(display_df, use_container_width=True, height=400)

# Скачивание данных
csv = display_df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Скачать данные (CSV)",
    data=csv,
    file_name=f"imobil_index_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# =========================
# Информация о исторических данных
# =========================
if df_hist.empty:
    st.sidebar.warning("📈 Исторические данные (gold_estate_daily) пусты")

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown("**Revoland Analytics** │ 📧 sergey.revo@outlook.com │ 🏠 Аналитика недвижимости Молдовы")
