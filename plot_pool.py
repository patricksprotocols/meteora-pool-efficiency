import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from main import short_address
from plot_trends import daily_readings
from trend import HISTORY_DIR, build_timelines, load_snapshots

POOL = "zxTp...SCLX"  # short address of STONK / SOL, as printed by trend.py
CHART_FILE = Path(__file__).parent / "pool_breakdown.png"

PANELS = [
    ("volume", "24h volume (USD)"),
    ("liquidity", "Liquidity (USD)"),
    ("efficiency", "Volume / liquidity (x)"),
]


def find_pool(timelines, short):
    for address in timelines:
        if short_address(address) == short:
            return address
    return None


def millions(value, _position):
    return f"{value / 1e6:.1f}M"


def print_change(points):
    print(f"{'':<26}{'First':>14}{'Latest':>14}{'Change':>10}")
    for field, label in PANELS:
        days = list(daily_readings(points, field).values())
        first, latest = days[0], days[-1]
        change = f"{(latest - first) / first * 100:+.1f}%" if first else "n/a"
        print(f"{label:<26}{first:>14,.2f}{latest:>14,.2f}{change:>10}")


def plot_pool(points, name, out_path):
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 8))
    for ax, (field, label) in zip(axes, PANELS):
        days = daily_readings(points, field)
        ax.plot(list(days), list(days.values()), marker="o")
        ax.set_ylabel(label)
        ax.spines[["top", "right"]].set_visible(False)
        if field != "efficiency":
            ax.yaxis.set_major_formatter(FuncFormatter(millions))

    axes[0].set_title(f"{name}: volume, liquidity and efficiency by day")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


def main():
    snapshots = load_snapshots(HISTORY_DIR)
    if not snapshots:
        sys.exit("No snapshots found in history/. Run fetch.py first.")

    timelines = build_timelines(snapshots)
    address = find_pool(timelines, POOL)
    if address is None:
        sys.exit(f"Pool {POOL} not found. It may never have had enough liquidity.")

    points = timelines[address]
    print_change(points)
    plot_pool(points, points[-1]["name"], CHART_FILE)
    print(f"\nChart saved: {CHART_FILE.name}")


if __name__ == "__main__":
    main()