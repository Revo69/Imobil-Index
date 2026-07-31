from __future__ import annotations

import os
from pathlib import Path

import tomllib
from supabase import create_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECRETS_PATH = PROJECT_ROOT / ".streamlit" / "secrets.toml"

API_TABLES = [
    ("api_estate_current", "date"),
    ("api_estate_daily", "date"),
    ("api_estate_segments_current", "date"),
    ("api_estate_segments_daily", "date"),
    ("api_rent_current", "date"),
    ("api_rent_daily", "date"),
    ("api_rent_yield", "refreshed_at"),
]


def load_supabase_credentials() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key

    if not SECRETS_PATH.exists():
        raise RuntimeError(
            "Supabase credentials were not found. Add .streamlit/secrets.toml "
            "or set SUPABASE_URL and SUPABASE_KEY."
        )

    secrets = tomllib.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    url = secrets.get("SUPABASE_URL")
    key = secrets.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL or SUPABASE_KEY is missing from .streamlit/secrets.toml."
        )
    return str(url), str(key)


def check_table(client, table_name: str, freshness_column: str) -> tuple[int, str | None]:
    response = (
        client.table(table_name)
        .select(freshness_column, count="exact")
        .order(freshness_column, desc=True)
        .limit(1)
        .execute()
    )
    latest_value = response.data[0][freshness_column] if response.data else None
    return int(response.count or 0), latest_value


def main() -> int:
    try:
        url, key = load_supabase_credentials()
        client = create_client(url, key)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL credentials/client: {type(exc).__name__}: {exc}")
        return 1

    failed = False
    for table_name, freshness_column in API_TABLES:
        try:
            row_count, latest_value = check_table(client, table_name, freshness_column)
        except Exception as exc:  # noqa: BLE001
            failed = True
            print(f"FAIL {table_name}: {type(exc).__name__}: {exc}")
            continue

        if row_count <= 0 or latest_value is None:
            failed = True
            print(f"CHECK {table_name}: rows={row_count} latest={latest_value}")
        else:
            print(f"OK {table_name}: rows={row_count} latest={latest_value}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
