import unittest
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def sale_tab_source() -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    start = source.index("    with tab_sale:")
    end = source.index("    with tab_rent_monthly:", start)
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


if __name__ == "__main__":
    unittest.main()
