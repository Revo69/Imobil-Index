"""Source and data-contract checks for the For Sale reference baseline."""

import ast
import re
import unittest
from pathlib import Path

import pandas as pd

from dashboard_components import format_int, format_price
from dashboard_transforms import (
    latest_data_date,
    place_label,
    weighted_average,
)

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
COMPONENTS_PATH = Path(__file__).resolve().parents[1] / "dashboard_components.py"


def app_source() -> str:
    return APP_PATH.read_text(encoding="utf-8-sig")


def components_source() -> str:
    return COMPONENTS_PATH.read_text(encoding="utf-8")


def sale_tab_source(source: str) -> str:
    start = source.index("    with tab_sale:")
    end = source.index("    with tab_rent_monthly:", start)
    return source[start:end]


def extracted_app_function(name: str):
    tree = ast.parse(app_source())
    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )
    if function is None:
        raise AssertionError(f"app.py must define {name}().")

    namespace = {
        "pd": pd,
        "format_int": format_int,
        "format_price": format_price,
        "place_label": place_label,
        "weighted_average": weighted_average,
    }
    module = ast.Module(body=[function], type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, APP_PATH, "exec"), namespace)  # noqa: S102
    return namespace[name]


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
            self.assertLess(trend_position, source.index("render_tab_header"))

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

    def test_empty_for_sale_market_renders_only_no_listings_state(self) -> None:
        source = sale_tab_source(app_source())
        empty_branch_start = source.index("        if df.empty:")
        empty_branch_end = source.index("        else:", empty_branch_start)
        empty_branch = source[empty_branch_start:empty_branch_end]

        self.assertNotIn("render_market_signal_rail(", empty_branch)
        self.assertEqual(
            empty_branch.count(
                'render_empty_state("No sale listings match the current filters.")'
            ),
            1,
        )

    def test_for_sale_rail_uses_the_shared_market_signal_values(self) -> None:
        source = sale_tab_source(app_source())

        self.assertIn("build_market_signal_values(", source)
        for label, key in (
            ("Weighted price per m2", "weighted_price"),
            ("Visible supply", "visible_supply"),
            ("Most active sector", "active_sector"),
            ("Price range", "price_range"),
            ("Median sector price", "median_price"),
        ):
            self.assertIn(f'"{label}"', source)
            self.assertIn(f'signal_values["{key}"]', source)

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


class MarketSignalValueTests(unittest.TestCase):
    def test_shared_signal_values_preserve_sale_market_calculations(self) -> None:
        build_market_signal_values = extracted_app_function(
            "build_market_signal_values"
        )
        market = pd.DataFrame(
            {
                "city": ["Chișinău", "Chișinău"],
                "sector": ["Centru", "Botanica"],
                "listings": [4, 6],
                "avg_per_m2_eur": [1000.0, 2000.0],
            }
        )

        self.assertEqual(
            build_market_signal_values(market, "avg_per_m2_eur", price_suffix="/m2"),
            {
                "weighted_price": "1.600 EUR/m2",
                "visible_supply": "10",
                "visible_groups": "2",
                "active_sector": "Chișinău -> Botanica",
                "active_listings": "6",
                "price_range": "1.000 EUR/m2",
                "price_range_places": (
                    "Chișinău -> Centru to Chișinău -> Botanica"
                ),
                "median_price": "1.500 EUR/m2",
            },
        )


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
