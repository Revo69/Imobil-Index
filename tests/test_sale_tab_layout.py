import ast
import unittest
from pathlib import Path

from dashboard_theme import THEME

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
CHARTS_PATH = Path(__file__).resolve().parents[1] / "dashboard_charts.py"


def sale_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_sale:")
    end = source.index("    with tab_rent_monthly:", start)
    return source[start:end]


def daily_rent_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_rent_daily:")
    end = source.index("    with tab_insights:", start)
    return source[start:end]


def monthly_rent_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_rent_monthly:")
    end = source.index("    with tab_rent_daily:", start)
    return source[start:end]


def market_highlights_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("def render_market_highlights(")
    end = source.index("def render_decision_notes(", start)
    return source[start:end]


def app_function_source(name: str, next_name: str) -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index(f"def {name}(")
    end = source.index(f"def {next_name}(", start)
    return source[start:end]


def chart_function_source(name: str, next_name: str) -> str:
    source = CHARTS_PATH.read_text(encoding="utf-8")
    start = source.index(f"def {name}(")
    end = source.index(f"def {next_name}(", start)
    return source[start:end]


def module_constant(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{path.name} must define {name}.")


def relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def insights_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_insights:")
    end = source.index("# =========================\n# Footer", start)
    return source[start:end]


class SaleTabLayoutTests(unittest.TestCase):
    def test_sale_trends_precede_market_overview(self) -> None:
        source = sale_tab_source()
        header_position = source.index("render_tab_header(")

        self.assertLess(source.index("render_sales_trend"), header_position)
        self.assertLess(source.index("render_profile_sales_trend"), header_position)

    def test_sale_rail_replaces_market_pulse_without_changing_rent_tabs(self) -> None:
        self.assertNotIn("render_market_highlights(", sale_tab_source())
        self.assertIn("render_market_highlights(", monthly_rent_tab_source())
        self.assertIn("render_market_highlights(", daily_rent_tab_source())


class SaleHeroChartContractTests(unittest.TestCase):
    def test_sale_trend_paths_use_the_scoped_hero_chart_treatment(self) -> None:
        sales_trend = app_function_source("render_sales_trend", "selected_trend_city")
        profile_trend = app_function_source(
            "render_profile_sales_trend", "render_sector_table"
        )
        charts_source = CHARTS_PATH.read_text(encoding="utf-8")

        self.assertIn("def apply_sale_hero_chart_style(", charts_source)
        self.assertIn("def render_sale_hero_chart(", charts_source)
        self.assertIn('key="sale-trend-hero"', charts_source)
        for trend_source in (sales_trend, profile_trend):
            self.assertIn("apply_sale_hero_chart_style(", trend_source)
            self.assertIn("render_sale_hero_chart(", trend_source)
            self.assertIn('THEME["sale_hero_text"]', trend_source)
            self.assertIn("SALE_HERO_TRACE_COLORS", trend_source)

    def test_sale_hero_trace_palette_meets_dark_background_contrast(self) -> None:
        colors = module_constant(CHARTS_PATH, "SALE_HERO_TRACE_COLORS")

        self.assertGreaterEqual(len(colors), 3)
        for color in colors:
            with self.subTest(color=color):
                self.assertGreaterEqual(
                    contrast_ratio(color, THEME["sale_hero_bg"]),
                    3.0,
                )

    def test_sale_hero_uses_chisinau_diacritics_in_user_copy(self) -> None:
        sales_trend = app_function_source("render_sales_trend", "selected_trend_city")

        self.assertIn('"Chișinău price pulse"', sales_trend)
        self.assertIn("most active Chișinău sectors", sales_trend)
        self.assertNotIn('"Chisinau', sales_trend)

    def test_generic_rankings_keep_the_common_chart_style(self) -> None:
        ranked_bars = chart_function_source("render_ranked_bars", "render_price_sections")

        self.assertIn("apply_common_chart_style(", ranked_bars)
        self.assertNotIn("apply_sale_hero_chart_style(", ranked_bars)


class DailyRentTabLayoutTests(unittest.TestCase):
    def test_daily_yield_precedes_market_rankings(self) -> None:
        source = daily_rent_tab_source()
        yield_position = source.index("render_yield_chart(")
        rankings_position = min(
            source.index("render_listing_sections"),
            source.index("render_price_sections"),
        )

        self.assertLess(yield_position, rankings_position)

    def test_return_scenarios_group_secondary_daily_analysis(self) -> None:
        source = daily_rent_tab_source()
        disclosure = 'with st.expander("Return scenarios"'
        self.assertIn(disclosure, source)
        disclosure_position = source.index(disclosure)

        self.assertLess(disclosure_position, source.index("render_daily_rent_context"))
        self.assertLess(disclosure_position, source.index("render_break_even_analysis"))
        self.assertLess(
            disclosure_position, source.index("render_daily_vs_monthly_return")
        )


class MarketPulseLayoutTests(unittest.TestCase):
    def test_market_pulse_uses_compact_metrics_instead_of_kpi_cards(self) -> None:
        source = market_highlights_source()

        self.assertIn('render_section("Market pulse"', source)
        self.assertNotIn("render_kpi_card(", source)
        self.assertEqual(source.count("st.metric("), 3)


class InsightsTabLayoutTests(unittest.TestCase):
    def test_weekly_brief_precedes_decision_notes(self) -> None:
        source = insights_tab_source()

        self.assertLess(
            source.index("render_weekly_market_brief"),
            source.index("render_decision_notes"),
        )


if __name__ == "__main__":
    unittest.main()
