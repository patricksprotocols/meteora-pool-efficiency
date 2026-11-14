import json
from pathlib import Path
import matplotlib.pyplot as plt

import pandas as pd

DATA_FILE = Path(__file__).parent / "meteora_data.json"
CHART_FILE = Path(__file__).parent / "band_medians.png"

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


def plot_band_medians(summary, out_path):
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(summary.index.astype(str), summary["median"], color="#4C72B0")
    for bar, count in zip(bars, summary["count"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"n={count}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_title("Median volume / liquidity by pool size")
    ax.set_xlabel("Pool liquidity (USD)")
    ax.set_ylabel("Median volume / liquidity (x)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


def main():
    pools = load_pools(DATA_FILE)
    summary = efficiency_by_band(pools)
    print(summary.round(2))
    print(top_efficiency(pools))
    print(pools[pools["liquidity"] > 2_000_000][["name", "liquidity", "volume_24h"]])
    plot_band_medians(summary, CHART_FILE)
    print(f"Chart saved: {CHART_FILE.name}")


if __name__ == "__main__":
    main()