from collections.abc import Callable

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import CHART_NEUTRAL, PLOTLY_FONT_FAMILY, THEME
from transforms import sector_label

PLOTLY_CHART_CONFIG = {
    "displayModeBar": False,
    "displaylogo": False,
    "responsive": True,
}


def render_plotly_chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CHART_CONFIG)


def apply_common_chart_style(fig, height: int = 430, show_legend: bool = False):
    fig.update_layout(
        height=height,
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": PLOTLY_FONT_FAMILY, "size": 13, "color": THEME["text"]},
        hoverlabel={
            "bgcolor": THEME["ink"],
            "font_size": 13,
            "font_color": THEME["white"],
        },
        coloraxis_showscale=False,
        showlegend=show_legend,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "title_text": "",
        },
    )
    fig.update_xaxes(
        title_text="",
        showgrid=False,
        tickangle=-35,
        tickfont={"color": THEME["muted"]},
        fixedrange=True,
    )
    fig.update_yaxes(
        title_font={"color": THEME["muted"]},
        tickfont={"color": THEME["muted"]},
        gridcolor=THEME["border"],
        zeroline=False,
        fixedrange=True,
    )
    return fig


def format_chart_hover_value(value: float, y_label: str, digits: int) -> str:
    formatted = f"{value:,.{digits}f}"
    if y_label == "Listings":
        return f"{formatted} listings"
    if "month" in y_label:
        return f"{formatted} EUR/m2/month"
    if "day" in y_label:
        return f"{formatted} EUR/m2/day"
    if "EUR" in y_label:
        return f"{formatted} EUR/m2"
    return formatted


def render_ranked_bars(
    df: pd.DataFrame,
    title: str,
    price_col: str,
    y_label: str,
    color_scale: list[str],
    mode: str,
    digits: int,
    render_section: Callable[[str, str | None], None],
    render_empty_state: Callable[[str], None],
) -> None:
    caption = (
        "Lowest visible sectors, sorted from lower to higher value."
        if mode == "lowest"
        else "Highest visible sectors, sorted from lower to higher value."
    )
    render_section(title, caption)
    if df.empty:
        render_empty_state("No sectors match the current filters.")
        return

    top = (
        df.nsmallest(10, price_col).copy()
        if mode == "lowest"
        else df.nlargest(10, price_col).copy()
    )
    top["Sector"] = sector_label(top)
    top["ChartLabel"] = top["Sector"].str.replace(" -> ", " - ", regex=False)
    top = top.sort_values(price_col, ascending=True)
    top["Label"] = top[price_col].map(lambda value: f"{value:.{digits}f}")
    top["HoverValue"] = top[price_col].map(
        lambda value: format_chart_hover_value(value, y_label, digits)
    )

    accent_color = color_scale[1] if mode == "lowest" else color_scale[-1]
    colors = [CHART_NEUTRAL] * len(top)
    if colors:
        colors[0 if mode == "lowest" else -1] = accent_color

    fig = px.bar(
        top,
        x=price_col,
        y="ChartLabel",
        orientation="h",
        text="Label",
        labels={price_col: y_label, "ChartLabel": ""},
        custom_data=["Sector", "HoverValue"],
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
    )
    fig = apply_common_chart_style(fig, height=max(350, min(500, 120 + len(top) * 32)))
    fig.update_layout(margin={"l": 4, "r": 58, "t": 8, "b": 4}, bargap=0.24)
    fig.update_xaxes(
        title_text="",
        showgrid=True,
        showticklabels=False,
        ticks="",
        zeroline=False,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=top["ChartLabel"].tolist()[::-1],
        tickangle=0,
        automargin=True,
        title_text="",
    )

    with st.container(border=True):
        render_plotly_chart(fig)


def render_price_sections(
    df: pd.DataFrame,
    price_col: str,
    y_label: str,
    low_scale: list[str],
    high_scale: list[str],
    digits: int,
    render_section: Callable[[str, str | None], None],
    render_empty_state: Callable[[str], None],
) -> None:
    col_l, col_r = st.columns(2)
    with col_l:
        render_ranked_bars(
            df,
            "Lowest priced sectors",
            price_col,
            y_label,
            low_scale,
            "lowest",
            digits,
            render_section,
            render_empty_state,
        )
    with col_r:
        render_ranked_bars(
            df,
            "Highest priced sectors",
            price_col,
            y_label,
            high_scale,
            "highest",
            digits,
            render_section,
            render_empty_state,
        )


def render_listing_sections(
    df: pd.DataFrame,
    color_scale: list[str],
    render_section: Callable[[str, str | None], None],
    render_empty_state: Callable[[str], None],
) -> None:
    col_l, col_r = st.columns(2)
    with col_l:
        render_ranked_bars(
            df,
            "Lowest inventory sectors",
            "listings",
            "Listings",
            color_scale,
            "lowest",
            0,
            render_section,
            render_empty_state,
        )
    with col_r:
        render_ranked_bars(
            df,
            "Highest inventory sectors",
            "listings",
            "Listings",
            color_scale,
            "highest",
            0,
            render_section,
            render_empty_state,
        )
