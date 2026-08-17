"""Regression tests for public Supabase API data loading."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import dashboard_data


class FakeQuery:
    """Small fluent Supabase query fake for pagination tests."""

    def __init__(self, batches: list[list[dict]]) -> None:
        self.batches = batches
        self.range_calls: list[tuple[int, int]] = []

    def select(self, columns: str):
        self.columns = columns
        return self

    def gte(self, column: str, cutoff: str):
        self.gte_call = (column, cutoff)
        return self

    def range(self, start: int, end: int):
        self.range_calls.append((start, end))
        return self

    def order(self, column: str, desc: bool = False):
        self.order_call = (column, desc)
        return self

    def execute(self):
        batch_index = len(self.range_calls) - 1
        return SimpleNamespace(data=self.batches[batch_index])


class FakeSupabase:
    def __init__(self, query: FakeQuery) -> None:
        self.query = query
        self.tables: list[str] = []

    def table(self, table_name: str) -> FakeQuery:
        self.tables.append(table_name)
        return self.query


class DashboardDataTests(unittest.TestCase):
    def setUp(self) -> None:
        dashboard_data.load_historical_data.clear()
        dashboard_data.load_historical_segment_data.clear()

    def tearDown(self) -> None:
        dashboard_data.load_historical_data.clear()
        dashboard_data.load_historical_segment_data.clear()

    def test_fetch_paginated_rows_collects_every_page(self) -> None:
        rows = [{"id": row_id} for row_id in range(5)]
        query = FakeQuery([rows[:2], rows[2:4], rows[4:]])
        supabase = FakeSupabase(query)

        with patch("dashboard_data.get_supabase_client", return_value=supabase):
            result = dashboard_data.fetch_paginated_rows(
                "api_estate_daily", "date,id", "2026-08-01", page_size=2
            )

        self.assertEqual(result, rows)
        self.assertEqual(supabase.tables, ["api_estate_daily"] * 3)
        self.assertEqual(query.range_calls, [(0, 1), (2, 3), (4, 5)])
        self.assertEqual(query.gte_call, ("date", "2026-08-01"))
        self.assertEqual(query.order_call, ("date", False))

    def test_fetch_paginated_rows_stops_after_short_page(self) -> None:
        query = FakeQuery([[{"id": 1}, {"id": 2}], [{"id": 3}]])
        supabase = FakeSupabase(query)

        with patch("dashboard_data.get_supabase_client", return_value=supabase):
            result = dashboard_data.fetch_paginated_rows(
                "api_estate_daily", "date,id", "2026-08-01", page_size=2
            )

        self.assertEqual(result, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(query.range_calls, [(0, 1), (2, 3)])

    def test_required_history_request_propagates_failure(self) -> None:
        with (
            patch(
                "dashboard_data.fetch_paginated_rows",
                side_effect=RuntimeError("history unavailable"),
            ),
            self.assertRaisesRegex(RuntimeError, "history unavailable"),
        ):
            dashboard_data.load_historical_data()

    def test_optional_profile_history_returns_empty_data_on_failure(self) -> None:
        with patch(
            "dashboard_data.fetch_paginated_rows",
            side_effect=RuntimeError("profile history unavailable"),
        ):
            result = dashboard_data.load_historical_segment_data()

        self.assertTrue(result.empty)
