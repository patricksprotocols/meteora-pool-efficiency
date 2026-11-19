import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from main import short_address
from trend import HISTORY_DIR, build_timelines, load_snapshots

CHART_FILE = Path(__file__).parent / "efficiency_over_time.png"


def daily_readings(points, field="efficiency"):
    """Keep one value of `field` per calendar day: the last reading of that day."""
    by_day = {}
    for point in points:  # oldest first, so a later reading overwrites an earlier one
        by_day[point["time"].date()] = point[field]
    return by_day


def most_tracked(timelines, n=5):
    """Addresses of the n pools with readings on the most days."""
    days_seen = {address: len(daily_readings(points)) for address, points in timelines.items()}
    return sorted(days_seen, key=lambda address: days_seen[address], reverse=True)[:n]


def plot_efficiency(timelines, addresses, out_path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for address in addresses:
        points = timelines[address]
        days = daily_readings(points)
        label = f"{points[-1]['name']} ({short_address(address)})"
        ax.plot(list(days), list(days.values()), marker="o", label=label)

    ax.set_title("Volume / liquidity by day (9 to 16 Nov 2026)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume / liquidity (x)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1))
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")


def main():
    snapshots = load_snapshots(HISTORY_DIR)
    if not snapshots:
        sys.exit("No snapshots found in history/. Run fetch.py first.")

    timelines = build_timelines(snapshots)
    addresses = most_tracked(timelines)
    if not addresses:
        sys.exit("No pools with an address and enough liquidity to plot.")

    plot_efficiency(timelines, addresses, CHART_FILE)
    print(f"Chart saved: {CHART_FILE.name}")


if __name__ == "__main__":
    main()