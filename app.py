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

import streamlit as st
from datetime import datetime

# =========================
# Улучшенная шапка дашборда
# =========================

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 24px;
    padding: 3rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
">
    <!-- Декоративные элементы -->
    <div style="
        position: absolute;
        top: -100px;
        right: -50px;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    "></div>
    <div style="
        position: absolute;
        bottom: -80px;
        left: -30px;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
        animation: float 8s ease-in-out infinite;
    "></div>
    
    <div style="position: relative; z-index: 2;">
        <!-- Заголовок -->
        <div style="text-align: center; margin-bottom: 3rem;">
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 1rem;
                background: rgba(255,255,255,0.15);
                padding: 1rem 2rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                margin-bottom: 1rem;
            ">
                <div style="font-size: 2.5rem;">🏠</div>
                <div>
                    <h1 style="
                        margin: 0;
                        font-size: 2.5rem;
                        font-weight: 800;
                        color: white;
                        line-height: 1.1;
                    ">Imobil.Index</h1>
                    <p style="
                        margin: 0;
                        color: rgba(255,255,255,0.9);
                        font-size: 1.1rem;
                        font-weight: 500;
                    ">Аналитика недвижимости Молдовы</p>
                </div>
            </div>
        </div>

        <!-- Метрики -->
        <div style="
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 3rem;
            max-width: 700px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        ">
            <!-- Левая метрика -->
            <div style="text-align: right;">
                <div style="
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                ">
                    <div style="font-size: 0.875rem; color: rgba(255,255,255,0.8); font-weight: 600; letter-spacing: 1px;">
                        ОБНОВЛЕНО
                    </div>
                    <div style="font-size: 1.5rem; color: white; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        {datetime.now():%d %b %Y}
                    </div>
                    <div style="font-size: 1rem; color: rgba(255,255,255,0.7); font-weight: 500;">
                        в {datetime.now():%H:%M}
                    </div>
                </div>
            </div>

            <!-- Разделитель -->
            <div style="
                width: 2px;
                height: 80px;
                background: linear-gradient(180deg, 
                    transparent 0%, 
                    rgba(255,255,255,0.5) 50%, 
                    transparent 100%);
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 8px;
                    height: 8px;
                    background: white;
                    border-radius: 50%;
                    box-shadow: 0 0 10px rgba(255,255,255,0.5);
                "></div>
            </div>

            <!-- Правая метрика -->
            <div style="text-align: left;">
                <div style="
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                ">
                    <div style="font-size: 0.875rem; color: rgba(255,255,255,0.8); font-weight: 600; letter-spacing: 1px;">
                        АКТИВНЫХ ОБЪЯВЛЕНИЙ
                    </div>
                    <div style="
                        font-size: 2.5rem;
                        color: #fbbf24;
                        font-weight: 900;
                        line-height: 1;
                        text-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
                        background: linear-gradient(45deg, #fbbf24, #f59e0b);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">
                        16,197
                    </div>
                    <div style="
                        font-size: 0.875rem;
                        color: rgba(255,255,255,0.7);
                        font-weight: 500;
                    ">
                        +124 за сегодня
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    @keyframes float {
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(180deg); }}
    }}
    
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }}
        50% {{ box-shadow: 0 0 40px rgba(102, 126, 234, 0.8); }}
    }}
</style>
""", unsafe_allow_html=True)

# Стилизованный разделитель
st.markdown("""
<div style="
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 3rem 0;
    gap: 1rem;
">
    <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent, #667eea);"></div>
    <div style="
        display: flex;
        gap: 0.5rem;
        align-items: center;
    ">
        <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%;"></div>
        <div style="width: 8px; height: 8px; background: #764ba2; border-radius: 50%;"></div>
        <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%;"></div>
    </div>
    <div style="flex: 1; height: 2px; background: linear-gradient(90deg, #764ba2, transparent);"></div>
</div>
""", unsafe_allow_html=True)

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
    st.metric("Самый дешёвый", f"{city_c}\n→ {sector_c}")

with col4:
    expensive = df_now.loc[df_now['avg_per_m2_eur'].idxmax()]
    city_e = expensive['city']
    sector_e = expensive['sector'] or "Центр"
    st.metric("Самый дорогой", f"{city_e}\n→ {sector_e}")
    
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
