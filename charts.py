import streamlit as st

from theme import PLOTLY_FONT_FAMILY, THEME

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
