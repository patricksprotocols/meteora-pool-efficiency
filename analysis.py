import json
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).parent / "meteora_data.json"

# Liquidity bands in USD, smallest to largest.
BAND_EDGES = [0, 100_000, 500_000, 2_000_000, float("inf")]
BAND_LABELS = ["under 100k", "100k to 500k", "500k to 2M", "over 2M"]


def load_pools(path):
    with path.open(encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def efficiency_by_band(pools):
    """Count pools and summarise volume / liquidity within each liquidity band."""
    pools = pools[pools["liquidity"] > 0].copy()
    pools["efficiency"] = pools["volume_24h"] / pools["liquidity"]
    pools["band"] = pd.cut(pools["liquidity"], bins=BAND_EDGES, labels=BAND_LABELS)
    return pools.groupby("band", observed=True)["efficiency"].agg(["count", "median", "mean"])


def top_efficiency(pools, n=5):
    """The n pools with the highest volume / liquidity."""
    pools = pools[pools["liquidity"] > 0].copy()
    pools["efficiency"] = pools["volume_24h"] / pools["liquidity"]
    return pools.nlargest(n, "efficiency")[["name", "liquidity", "volume_24h", "efficiency"]]


def main():
    pools = load_pools(DATA_FILE)
    summary = efficiency_by_band(pools)
    print(summary.round(2))
    print(top_efficiency(pools))
    print(pools[pools["liquidity"] > 2_000_000][["name", "liquidity", "volume_24h"]])


if __name__ == "__main__":
    main()