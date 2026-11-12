import json
import sys
import time
from pathlib import Path
import requests
from history import archive_snapshot

API_URL = "https://api.geckoterminal.com/api/v2/networks/solana/dexes/meteora/pools"
BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "meteora_data.json"
HISTORY_DIR = BASE_DIR / "history"
PAGES = 3


def fetch_pools():
    pools = []
    for page in range(1, PAGES + 1):
        response = requests.get(
            API_URL,
            params={"page": page},
            headers={"accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        pools.extend(response.json()["data"])
        time.sleep(2)  # to avoid hitting the API's rate limits
    return pools


def clean_pool(pool):
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

    records = []
    for pool in raw_pools:
        cleaned = clean_pool(pool)
        if cleaned:
            records.append(cleaned)
    if not records:
        sys.exit("No valid pools found.")

    OUTPUT_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} pools to {OUTPUT_FILE.name}")

    snapshot = archive_snapshot(OUTPUT_FILE, HISTORY_DIR)
    print(f"Snapshot saved: {snapshot.name}")


if __name__ == "__main__":
    main()