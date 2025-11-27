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

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# ДИАГНОСТИКА - добавь этот блок
# =========================
st.sidebar.header("🔍 Диагностика")

# Проверяем подключение и данные
try:
    # Тестируем подключение
    test_resp = supabase.table("gold_estate_current").select("count", count="exact").execute()
    st.sidebar.success(f"✅ Подключение к Supabase работает")
    
    # Получаем реальные данные
    resp = supabase.table("gold_estate_current").select("*").execute()
    df_now = pd.DataFrame(resp.data)
    
    st.sidebar.info(f"📊 Записей в gold_estate_current: **{len(df_now)}**")
    
    if not df_now.empty:
        st.sidebar.info(f"📅 Последняя дата: **{df_now['date'].iloc[0]}**")
        st.sidebar.info(f"🏙️ Города: **{df_now['city'].nunique()}**")
        
except Exception as e:
    st.sidebar.error(f"❌ Ошибка подключения: {str(e)}")
    df_now = pd.DataFrame()

# =========================
# Загрузка данных (оригинальный код)
# =========================
@st.cache_data(ttl=3600)
def load_current():
    resp = supabase.table("gold_estate_current").select("*").execute()
    st.sidebar.info(f"🔄 Функция load_current вызвана, данных: {len(resp.data)}")
    return pd.DataFrame(resp.data)

@st.cache_data(ttl=86400)
def load_history():
    resp = supabase.table("gold_estate_daily").select("*").execute()
    return pd.DataFrame(resp.data)

# Загружаем данные
df_now = load_current()
df_hist = load_history()

# Показываем сырые данные для отладки
if st.sidebar.checkbox("Показать сырые данные"):
    st.sidebar.write("gold_estate_current:", df_now.head(3) if not df_now.empty else "Пусто")
    st.sidebar.write("Столбцы:", df_now.columns.tolist() if not df_now.empty else "Нет столбцов")

# =========================
# Если пусто — расширенная диагностика
# =========================
if df_now.empty:
    st.error("Нет данных в gold_estate_current")
    
    # Проверяем другие таблицы
    try:
        silver_resp = supabase.table("silver_estate").select("count", count="exact").limit(1).execute()
        st.info(f"📋 Записей в silver_estate: {silver_resp.count if silver_resp.count is not None else 'N/A'}")
    except:
        st.warning("Не удалось проверить silver_estate")
    
    # Кнопка принудительного обновления кэша
    if st.button("🔄 Принудительно обновить кэш"):
        st.cache_data.clear()
        st.rerun()
    
    st.stop()

# =========================
# ОСТАЛЬНОЙ КОД ДАШБОРДА
# =========================
st.title("Imobil.Index — Недвижимость Молдовы 2025")
st.markdown(f"Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {df_now['listings'].sum():,} активных объявлений")

# ... остальной код без изменений
