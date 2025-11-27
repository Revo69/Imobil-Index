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
# Загрузка данных БЕЗ КЭША для теста
# =========================
def load_current():
    try:
        resp = supabase.table("gold_estate_current").select("*").execute()
        return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return pd.DataFrame()

def load_history():
    try:
        resp = supabase.table("gold_estate_daily").select("*").execute()
        return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Ошибка загрузки истории: {e}")
        return pd.DataFrame()

# Загружаем данные
df_now = load_current()
df_hist = load_history()

# =========================
# Проверка данных и отладка
# =========================
st.sidebar.header("Отладка данных")
st.sidebar.write(f"Записей в current: {len(df_now)}")
st.sidebar.write(f"Записей в history: {len(df_hist)}")

if not df_now.empty:
    st.sidebar.write("Колонки current:", df_now.columns.tolist())
    st.sidebar.write("Пример данных:", df_now[['city', 'sector', 'avg_per_m2_eur']].head(3).to_dict('records'))

# =========================
# ЕСЛИ ДАННЫЕ ЕСТЬ - показываем дашборд
# =========================
if not df_now.empty:
    # =========================
    # Шапка
    # =========================
    st.title("Imobil.Index — Недвижимость Молдовы 2025")
    st.markdown(f"Обновлено: {datetime.now():%d %B %Y в %H:%M} │ {df_now['listings'].sum():,} активных объявлений")
    
    # =========================
    # Ключевые метрики - с проверкой колонок
    # =========================
    col1, col2, col3, col4 = st.columns(4)
    
    # Проверяем наличие нужных колонок
    if 'listings' in df_now.columns:
        col1.metric("Районов в аналитике", len(df_now))
    else:
        col1.metric("Районов в аналитике", len(df_now))
    
    if 'avg_per_m2_eur' in df_now.columns:
        avg_price = df_now['avg_per_m2_eur'].mean()
        col2.metric("Средняя цена м²", f"{avg_price:.0f} €")
        
        # Ищем мин и макс цены
        if not df_now.empty:
            min_idx = df_now['avg_per_m2_eur'].idxmin()
            max_idx = df_now['avg_per_m2_eur'].idxmax()
            
            min_sector = df_now.loc[min_idx, 'sector'] if 'sector' in df_now.columns else '—'
            max_sector = df_now.loc[max_idx, 'sector'] if 'sector' in df_now.columns else '—'
            
            col3.metric("Самый дешёвый", f"{min_sector or '—'}")
            col4.metric("Самый дорогой", f"{max_sector or '—'}")
    
    st.divider()
    
    # =========================
    # ТОП-10 дешёвых и дорогих
    # =========================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("ТОП-10 самых дешёвых районов")
        if 'avg_per_m2_eur' in df_now.columns:
            cheap = df_now.nsmallest(10, "avg_per_m2_eur").copy()
            
            # Создаем название для отображения
            if 'city' in cheap.columns and 'sector' in cheap.columns:
                cheap["Район"] = cheap["city"] + cheap["sector"].fillna("").apply(lambda x: f" → {x}" if x else "")
            else:
                cheap["Район"] = cheap.index.astype(str)
            
            fig_cheap = px.bar(
                cheap, 
                x="Район", 
                y="avg_per_m2_eur", 
                text=cheap["avg_per_m2_eur"].round(0).astype(int).astype(str) + "€",
                color="avg_per_m2_eur",
                color_continuous_scale="Blues"
            )
            fig_cheap.update_layout(showlegend=False, xaxis_tickangle=45)
            fig_cheap.update_traces(textposition='outside')
            st.plotly_chart(fig_cheap, use_container_width=True)
        else:
            st.warning("Нет данных о ценах за м²")
    
    with col_right:
        st.subheader("ТОП-10 самых дорогих районов")
        if 'avg_per_m2_eur' in df_now.columns:
            expensive = df_now.nlargest(10, "avg_per_m2_eur").copy()
            
            # Создаем название для отображения
            if 'city' in expensive.columns and 'sector' in expensive.columns:
                expensive["Район"] = expensive["city"] + expensive["sector"].fillna("").apply(lambda x: f" → {x}" if x else "")
            else:
                expensive["Район"] = expensive.index.astype(str)
            
            fig_exp = px.bar(
                expensive, 
                x="Район", 
                y="avg_per_m2_eur", 
                text=expensive["avg_per_m2_eur"].round(0).astype(int).astype(str) + "€",
                color="avg_per_m2_eur", 
                color_continuous_scale="Reds"
            )
            fig_exp.update_layout(showlegend=False, xaxis_tickangle=45)
            fig_exp.update_traces(textposition='outside')
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.warning("Нет данных о ценах за м²")
    
    # =========================
    # Интерактивный фильтр + динамика
    # =========================
    st.divider()
    st.subheader("Динамика цен по секторам")
    
    if not df_hist.empty and 'city' in df_hist.columns:
        # Фильтр городов
        cities = ["Все"] + sorted(df_hist['city'].unique().tolist())
        selected_city = st.selectbox("Город", cities, index=cities.index("Кишинёв") if "Кишинёв" in cities else 0)
        
        if selected_city == "Все":
            hist_filtered = df_hist.copy()
        else:
            hist_filtered = df_hist[df_hist['city'] == selected_city]
        
        # Сектора с данными
        if 'sector' in hist_filtered.columns:
            sector_options = st.multiselect(
                "Сектора", 
                options=sorted(hist_filtered['sector'].dropna().unique()),
                default=sorted(hist_filtered['sector'].dropna().unique())[:3] if not hist_filtered.empty else []
            )
            
            if sector_options and 'avg_per_m2_eur' in hist_filtered.columns and 'date' in hist_filtered.columns:
                plot_df = hist_filtered[hist_filtered['sector'].isin(sector_options)]
                fig_line = px.line(
                    plot_df, 
                    x="date", 
                    y="avg_per_m2_eur", 
                    color="sector",
                    markers=True, 
                    title=f"Цена м² в {selected_city}"
                )
                fig_line.update_traces(line=dict(width=3))
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Выберите сектора для отображения графика")
        else:
            st.info("Нет данных по секторам")
    else:
        st.info("Нет исторических данных для анализа")
    
    # =========================
    # Полная таблица
    # =========================
    st.divider()
    st.subheader("Все районы — полная таблица")
    
    # Выбираем колонки для отображения
    display_columns = []
    if 'city' in df_now.columns: display_columns.append('city')
    if 'sector' in df_now.columns: display_columns.append('sector') 
    if 'listings' in df_now.columns: display_columns.append('listings')
    if 'avg_per_m2_eur' in df_now.columns: display_columns.append('avg_per_m2_eur')
    if 'avg_price_eur' in df_now.columns: display_columns.append('avg_price_eur')
    
    if display_columns:
        display_df = df_now[display_columns].copy()
        
        # Форматируем числовые колонки
        if 'avg_per_m2_eur' in display_df.columns:
            display_df['avg_per_m2_eur'] = display_df['avg_per_m2_eur'].round(0).astype(int)
        if 'avg_price_eur' in display_df.columns:
            display_df['avg_price_eur'] = display_df['avg_price_eur'].round(0).astype(int)
        
        # Сортируем по цене м²
        if 'avg_per_m2_eur' in display_df.columns:
            display_df = display_df.sort_values("avg_per_m2_eur")
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("Нет данных для отображения в таблице")

else:
    st.error("❌ Нет данных для отображения")
    st.info("Проверьте:")
    st.write("1. Наличие данных в таблице gold_estate_current")
    st.write("2. Правильность названий колонок")
    st.write("3. Настройки RLS в Supabase")

# =========================
# Футер
# =========================
st.markdown("---")
st.markdown("Revoland Analytics │ sergey.revo@outlook.com")
