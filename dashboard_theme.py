THEME = {
    "bg": "#f5f7f4",
    "surface": "#ffffff",
    "surface_soft": "#edf4f0",
    "surface_muted": "#f9fbf8",
    "ink": "#123026",
    "text": "#17201c",
    "muted": "#63746d",
    "border": "#d8e2dd",
    "blue": "#315fc9",
    "green": "#12805c",
    "amber": "#b76725",
    "cyan": "#0f8b8d",
    "white": "#ffffff",
    "chart_label": "#31443b",
    "shadow": "0 10px 26px rgba(18, 48, 38, 0.08)",
    "shadow_card": "0 6px 18px rgba(18, 48, 38, 0.055)",
    "sale_hero_bg": "#123026",
    "sale_hero_surface": "#1b4134",
    "sale_hero_text": "#ffffff",
    "sale_hero_muted": "#c9d9d2",
    "sale_signal_bg": "#edf4f0",
    "sale_signal_border": "#c9d9d2",
    "section_space": "1rem",
    "section_space_compact": "0.3rem",
    "mobile_stack_gap": "0.75rem",
}

CSS_VARIABLES = {
    "bg": THEME["bg"],
    "surface": THEME["surface"],
    "surface-soft": THEME["surface_soft"],
    "surface-muted": THEME["surface_muted"],
    "ink": THEME["ink"],
    "text": THEME["text"],
    "muted": THEME["muted"],
    "border": THEME["border"],
    "blue": THEME["blue"],
    "green": THEME["green"],
    "amber": THEME["amber"],
    "cyan": THEME["cyan"],
    "shadow": THEME["shadow"],
    "shadow-card": THEME["shadow_card"],
    "sale-hero-bg": THEME["sale_hero_bg"],
    "sale-hero-surface": THEME["sale_hero_surface"],
    "sale-hero-text": THEME["sale_hero_text"],
    "sale-hero-muted": THEME["sale_hero_muted"],
    "sale-signal-bg": THEME["sale_signal_bg"],
    "sale-signal-border": THEME["sale_signal_border"],
    "section-space": THEME["section_space"],
    "section-space-compact": THEME["section_space_compact"],
    "mobile-stack-gap": THEME["mobile_stack_gap"],
}

SALE_COLOR_SCALE = ["#e5edff", "#9db7f4", "#315fc9", "#1e3f8f"]
RENT_COLOR_SCALE = ["#dff6ea", "#8bd7b2", "#12805c", "#0b5d43"]
DAILY_COLOR_SCALE = ["#fff0df", "#f5b86f", "#c56b2c", "#8f451d"]
YIELD_COLOR_SCALE = ["#d9f3f1", "#7bcac5", "#0f8b8d", "#0b5f63"]
HIGH_PRICE_COLOR_SCALE = ["#fee2e2", "#fca5a5", "#ef4444", "#991b1b"]
HIGH_DAILY_RENT_COLOR_SCALE = ["#f3e8ff", "#c084fc", "#9333ea", "#581c87"]
CHART_NEUTRAL = "#cbd8d2"
PLOTLY_FONT_FAMILY = "Inter, Segoe UI, sans-serif"


def theme_css_vars() -> str:
    return "\n".join(
        f"            --{name}: {value};" for name, value in CSS_VARIABLES.items()
    )
