from html import escape

import streamlit as st


def render_section(title: str, caption: str | None = None) -> None:
    caption_html = f'<p class="section-caption">{caption}</p>' if caption else ""
    st.markdown(
        f"""
        <div class="section">
            <h3 class="section-title">{title}</h3>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def render_chart_title(title: str) -> None:
    st.markdown(
        f'<div class="chart-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )
