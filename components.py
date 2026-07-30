from html import escape

import streamlit as st


def format_int(value: float) -> str:
    return f"{value:,.0f}"


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


def render_app_header(latest_snapshot: str) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand-row">
                <div>
                    <div class="brand-kicker">Moldova market intelligence</div>
                    <div class="brand-title">
                        Imobil<span class="brand-dot">.</span>Index
                    </div>
                    <div class="brand-copy">
                        Residential real estate analytics for sale prices, rent,
                        short-term rent, and gross yield across Moldova.
                    </div>
                </div>
                <div class="status-pill">{escape(latest_snapshot)}</div>
            </div>
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


def render_kpi_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(label)}</div>
            <div class="kpi-value">{escape(value)}</div>
            <div class="kpi-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_cards(
    title: str, caption: str, cards: list[tuple[str, str, str]]
) -> None:
    render_section(title, caption)
    if not cards:
        render_empty_state("Not enough data for this insight yet.")
        return

    for start in range(0, len(cards), 3):
        row_cards = cards[start : start + 3]
        columns = st.columns(len(row_cards), gap="medium")
        for column, (label, value, note) in zip(columns, row_cards, strict=True):
            with column:
                card_html = (
                    '<div class="insight-card">'
                    f'<div class="insight-card-label">{escape(label)}</div>'
                    f'<div class="insight-card-value">{escape(value)}</div>'
                    f'<div class="insight-card-note">{escape(note)}</div>'
                    "</div>"
                )
                st.markdown(
                    card_html,
                    unsafe_allow_html=True,
                )
