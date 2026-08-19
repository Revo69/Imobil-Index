import unittest
from pathlib import Path

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


def insights_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_insights:")
    end = source.index("# =========================\n# Footer", start)
    return source[start:end]


class SaleTabLayoutTests(unittest.TestCase):
    def test_sale_trends_precede_market_overview(self) -> None:
        source = sale_tab_source()
        header_position = source.index("render_tab_header(")
        overview_position = source.index("render_market_highlights")

        self.assertLess(source.index("render_sales_trend"), header_position)
        self.assertLess(source.index("render_profile_sales_trend"), header_position)
        self.assertLess(source.index("render_sales_trend"), overview_position)
        self.assertLess(source.index("render_profile_sales_trend"), overview_position)


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
