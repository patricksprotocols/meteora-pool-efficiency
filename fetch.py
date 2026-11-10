import json
import sys
from pathlib import Path
import time

import requests

from history import archive_snapshot

API_URL = "https://api.geckoterminal.com/api/v2/networks/solana/dexes/meteora/pools"
OUTPUT_FILE = Path(__file__).parent / "meteora_data.json"
HISTORY_DIR = Path(__file__).parent / "history"


PAGES = 3


def fetch_pools(url=API_URL, pages=PAGES):
    pools = []
    for page in range(1, pages + 1):
        response = requests.get(
            url,
            params={"page": page},
            headers={"accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        pools.extend(response.json()["data"])
        time.sleep(2)  # stay well under the free API's rate limit
    return pools


def to_record(pool):
    """Reduce an API pool to the fields the analysis uses."""
    attrs = pool["attributes"]
    try:
        return {
            "name": attrs["name"],
            "address": attrs.get("address"),
            "volume_24h": float(attrs["volume_usd"]["h24"]),
            "liquidity": float(attrs["reserve_in_usd"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def main():
    try:
        raw_pools = fetch_pools()
    except requests.RequestException as err:
        sys.exit(f"Request failed: {err}")

    records = [r for r in map(to_record, raw_pools) if r is not None]
    if not records:
        sys.exit("No usable pools returned by the API.")

    OUTPUT_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} pools to {OUTPUT_FILE.name}")

    snapshot = archive_snapshot(OUTPUT_FILE, HISTORY_DIR)
    print(f"Snapshot saved: {snapshot.name}")


if __name__ == "__main__":
    main()