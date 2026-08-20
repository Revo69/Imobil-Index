from html import escape

import streamlit as st


def format_number(value: float, decimals: int = 0) -> str:
    """Format visible numbers with Moldova-style separators."""
    formatted = f"{float(value):,.{decimals}f}"
    return formatted.replace(",", "|").replace(".", ",").replace("|", ".")


def format_int(value: float) -> str:
    return format_number(value)


def format_price(value: float, decimals: int = 0, suffix: str = "") -> str:
    return f"{format_number(value, decimals)} EUR{suffix}"


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{format_number(value, decimals)}%"


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


def render_market_signal_rail(
    title: str, signals: list[tuple[str, str, str]]
) -> None:
    """Render compact, already-computed signals for the visible market."""
    render_section(title, "Current filtered market.")
    if not signals:
        render_empty_state("No market signals are available for the current filters.")
        return

    signal_html = "".join(
        (
            '<div class="sale-signal">'
            f'<div class="sale-signal-label">{escape(label)}</div>'
            f'<div class="sale-signal-value">{escape(value)}</div>'
            f'<div class="sale-signal-note">{escape(note)}</div>'
            "</div>"
        )
        for label, value, note in signals
    )
    st.markdown(
        f'<div class="sale-signal-rail">{signal_html}</div>',
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
    render_insight_card_row(cards)


def render_insight_card_row(cards: list[tuple[str, str, str]]) -> None:
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
