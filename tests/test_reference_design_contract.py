"""Source and data-contract checks for the For Sale reference baseline."""

import unittest
from pathlib import Path

import pandas as pd

from dashboard_transforms import latest_data_date

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def app_source() -> str:
    return APP_PATH.read_text(encoding="utf-8")


def sale_tab_source(source: str) -> str:
    start = source.index("    with tab_sale:")
    end = source.index("    with tab_rent_monthly:", start)
    return source[start:end]


class ReferenceDesignSourceContractTests(unittest.TestCase):
    def test_app_header_is_rendered_once_from_latest_snapshot(self) -> None:
        source = app_source()

        self.assertEqual(source.count("render_app_header("), 1)
        self.assertIn("render_app_header(latest_snapshot)", source)

    def test_for_sale_trend_precedes_current_market_summary(self) -> None:
        source = sale_tab_source(app_source())
        trend_positions = [
            source.index("render_sales_trend"),
            source.index("render_profile_sales_trend"),
        ]

        for trend_position in trend_positions:
            self.assertLess(trend_position, source.index("render_market_highlights"))


class SnapshotDataContractTests(unittest.TestCase):
    def test_latest_data_date_uses_latest_valid_snapshot(self) -> None:
        snapshots = pd.DataFrame(
            {"date": ["2026-08-17", "not-a-date", "2026-08-19"]}
        )

        self.assertEqual(latest_data_date(snapshots), pd.Timestamp("2026-08-19"))

    def test_latest_data_date_returns_none_without_a_valid_snapshot(self) -> None:
        snapshots = pd.DataFrame({"date": ["not-a-date", None]})

        self.assertIsNone(latest_data_date(snapshots))


if __name__ == "__main__":
    unittest.main()
