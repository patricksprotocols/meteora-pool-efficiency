import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from main import MIN_LIQUIDITY, rank_by_efficiency, short_address

HISTORY_DIR = Path(__file__).parent / "history"
SNAPSHOT_PREFIX = "meteora_data_"


def snapshot_time(path):
    """Read the capture time from a name like meteora_data_2026-11-09_13-19-20.json."""
    stamp = path.stem.removeprefix(SNAPSHOT_PREFIX)
    return datetime.strptime(stamp, "%Y-%m-%d_%H-%M-%S")


def load_snapshots(history_dir):
    """Return (captured_at, pools) for every readable snapshot, oldest first."""
    snapshots = []
    for path in sorted(history_dir.glob(f"{SNAPSHOT_PREFIX}*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                snapshots.append((snapshot_time(path), json.load(f)))
        except (json.JSONDecodeError, ValueError):
            print(f"Skipping unreadable snapshot: {path.name}", file=sys.stderr)
    return snapshots


def build_timelines(snapshots, min_liquidity=MIN_LIQUIDITY):
    """Group each pool's efficiency readings by pool address."""
    timelines = defaultdict(list)
    for captured_at, pools in snapshots:
        for pool in rank_by_efficiency(pools, min_liquidity):
            address = pool.get("address")
            if address:
                timelines[address].append(
                    {
                        "time": captured_at,
                        "name": pool["name"],
                        "efficiency": pool["efficiency"],
                    }
                )
    return timelines


def trend_rows(timelines):
    """One row per pool with two or more readings, biggest rise first."""
    rows = []
    for address, points in timelines.items():
        if len(points) < 2:
            continue
        first, last = points[0], points[-1]
        rows.append(
            {
                "address": address,
                "name": last["name"],
                "readings": len(points),
                "first": first["efficiency"],
                "last": last["efficiency"],
                "change": last["efficiency"] - first["efficiency"],
            }
        )
    return sorted(rows, key=lambda r: r["change"], reverse=True)


def print_report(rows):
    header = (
        f"{'Pool':<24}{'Address':<14}{'Readings':>9}"
        f"{'First':>9}{'Latest':>9}{'Change':>9}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['name']:<24}"
            f"{short_address(r['address']):<14}"
            f"{r['readings']:>9}"
            f"{r['first']:>8.2f}x"
            f"{r['last']:>8.2f}x"
            f"{r['change']:>+8.2f}x"
        )


def main():
    snapshots = load_snapshots(HISTORY_DIR)
    if not snapshots:
        sys.exit("No snapshots found in history/. Run fetch.py first.")

    rows = trend_rows(build_timelines(snapshots))
    if not rows:
        sys.exit("A trend needs at least two snapshots that contain the same pool.")
    print_report(rows)


if __name__ == "__main__":
    main()