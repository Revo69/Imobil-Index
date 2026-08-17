import unittest

import pandas as pd

from dashboard_transforms import (
    apply_daily_occupancy_assumption,
    build_city_market_summary,
    build_daily_vs_monthly_return,
    build_sale_market_from_segments,
    build_weekly_city_price_movement,
    build_weekly_price_movement,
    weighted_average,
)


class DashboardTransformsTests(unittest.TestCase):
    def test_weighted_average_does_not_treat_sectors_equally(self) -> None:
        markets = pd.DataFrame(
            {
                "listings": [90, 10],
                "avg_per_m2_eur": [1_000, 2_000],
            }
        )

        self.assertEqual(weighted_average(markets, "avg_per_m2_eur"), 1_100.0)

    def test_city_summary_uses_listing_weighted_prices(self) -> None:
        markets = pd.DataFrame(
            {
                "city": ["Chisinau", "Chisinau", "Balti"],
                "listings": [90, 10, 20],
                "avg_price_eur": [100_000, 200_000, 50_000],
                "avg_per_m2_eur": [1_000, 2_000, 800],
            }
        )

        summary = build_city_market_summary(markets).set_index("city")

        self.assertEqual(summary.loc["Chisinau", "listings"], 100)
        self.assertEqual(summary.loc["Chisinau", "avg_price_eur"], 110_000.0)
        self.assertEqual(summary.loc["Chisinau", "avg_per_m2_eur"], 1_100.0)

    def test_profile_market_aggregation_preserves_snapshot_grain(self) -> None:
        segments = pd.DataFrame(
            {
                "date": ["2026-08-10", "2026-08-10"],
                "city": ["Chisinau", "Chisinau"],
                "sector": ["Center", "Center"],
                "listings": [80, 20],
                "avg_price_eur": [120_000, 200_000],
                "avg_per_m2_eur": [1_500, 2_000],
            }
        )

        market = build_sale_market_from_segments(segments)

        self.assertEqual(len(market), 1)
        self.assertEqual(market.loc[0, "listings"], 100)
        self.assertEqual(market.loc[0, "avg_price_eur"], 136_000.0)
        self.assertEqual(market.loc[0, "avg_per_m2_eur"], 1_600.0)

    def test_weekly_movement_uses_closest_snapshot_at_least_seven_days_earlier(
        self,
    ) -> None:
        history = pd.DataFrame(
            [
                ("2026-08-01", "Chisinau", "Center", 1_000),
                ("2026-08-03", "Chisinau", "Center", 1_100),
                ("2026-08-10", "Chisinau", "Center", 1_210),
                ("2026-08-03", "Balti", "Center", 800),
                ("2026-08-10", "Balti", "Center", 720),
                ("2026-08-03", "Cahul", "Center", 700),
                ("2026-08-10", "Cahul", "Center", 900),
            ],
            columns=["date", "city", "sector", "avg_per_m2_eur"],
        )
        visible_markets = pd.DataFrame(
            {
                "city": ["Chisinau", "Balti"],
                "sector": ["Center", "Center"],
            }
        )

        movement = build_weekly_price_movement(history, visible_markets).set_index(
            "city"
        )

        self.assertEqual(len(movement), 2)
        self.assertEqual(movement.loc["Chisinau", "baseline_date"], pd.Timestamp("2026-08-03"))
        self.assertEqual(movement.loc["Chisinau", "days_between"], 7)
        self.assertAlmostEqual(movement.loc["Chisinau", "change_percent"], 10.0)
        self.assertAlmostEqual(movement.loc["Balti", "change_percent"], -10.0)

    def test_city_weekly_movement_is_listing_weighted(self) -> None:
        history = pd.DataFrame(
            [
                ("2026-08-03", "Chisinau", "Center", 100, 1_000),
                ("2026-08-03", "Chisinau", "Botanica", 10, 2_000),
                ("2026-08-10", "Chisinau", "Center", 100, 1_100),
                ("2026-08-10", "Chisinau", "Botanica", 10, 1_900),
            ],
            columns=["date", "city", "sector", "listings", "avg_per_m2_eur"],
        )
        visible_markets = history[["city", "sector"]].drop_duplicates()

        movement = build_weekly_city_price_movement(history, visible_markets)

        self.assertEqual(movement.loc[0, "comparable_sectors"], 2)
        self.assertEqual(movement.loc[0, "latest_listings"], 110)
        self.assertAlmostEqual(movement.loc[0, "baseline_avg_per_m2_eur"], 1_090.909, places=3)
        self.assertAlmostEqual(movement.loc[0, "latest_avg_per_m2_eur"], 1_172.727, places=3)
        self.assertAlmostEqual(movement.loc[0, "change_percent"], 7.5)

    def test_daily_return_tracks_the_selected_occupancy(self) -> None:
        yield_data = pd.DataFrame(
            {
                "city": ["Chisinau"],
                "sector": ["Center"],
                "annual_rent_monthly": [7_200],
                "annual_rent_daily_60pct": [12_000],
                "avg_sale_price_eur": [120_000],
                "sale_listings": [80],
                "total_rent_listings": [60],
                "yield_daily_percent": [10.0],
            }
        )

        adjusted = apply_daily_occupancy_assumption(yield_data, 30)
        comparison = build_daily_vs_monthly_return(yield_data, 60)

        self.assertEqual(yield_data.loc[0, "yield_daily_percent"], 10.0)
        self.assertEqual(adjusted.loc[0, "annual_rent_daily_eur"], 6_000.0)
        self.assertEqual(adjusted.loc[0, "yield_daily_percent"], 5.0)
        self.assertAlmostEqual(comparison.loc[0, "monthly_gross_yield_percent"], 6.0)
        self.assertAlmostEqual(comparison.loc[0, "daily_gross_yield_percent"], 10.0)
        self.assertAlmostEqual(comparison.loc[0, "daily_advantage_pp"], 4.0)
        self.assertAlmostEqual(
            comparison.loc[0, "occupancy_to_match_monthly_percent"], 36.0
        )


if __name__ == "__main__":
    unittest.main()
