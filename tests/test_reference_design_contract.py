"""Source and data-contract checks for the For Sale reference baseline."""

import re
import unittest
from pathlib import Path

import pandas as pd

from dashboard_transforms import latest_data_date

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
COMPONENTS_PATH = Path(__file__).resolve().parents[1] / "dashboard_components.py"


def app_source() -> str:
    return APP_PATH.read_text(encoding="utf-8")


def components_source() -> str:
    return COMPONENTS_PATH.read_text(encoding="utf-8")


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

    def test_for_sale_frame_places_both_trends_and_signals_before_summary(self) -> None:
        source = sale_tab_source(app_source())
        header_position = source.index("render_tab_header(")
        rail_call = "render_market_signal_rail("

        self.assertLess(source.index("render_sales_trend"), header_position)
        self.assertLess(source.index("render_profile_sales_trend"), header_position)
        if rail_call not in source:
            self.fail("For Sale frame must render the market signal rail.")
        self.assertLess(source.index(rail_call), header_position)
        self.assertIn('"Chișinău signals"', source)
        self.assertIn('"Market signals"', source)

    def test_signal_rail_owns_no_snapshot_or_fake_reference_metrics(self) -> None:
        source = components_source()
        rail_match = re.search(
            r"def render_market_signal_rail\((?P<signature>.*?)\) -> None:\n"
            r"(?P<body>.*?)(?=\ndef |\Z)",
            source,
            flags=re.DOTALL,
        )

        self.assertIsNotNone(rail_match)
        assert rail_match is not None
        rail_source = rail_match.group(0)

        self.assertNotIn("date", rail_match.group("signature").lower())
        self.assertNotIn("Data as of", rail_source)
        for fake_label in ("Live", "Price drops", "Days on market"):
            self.assertNotIn(fake_label, rail_source)


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
