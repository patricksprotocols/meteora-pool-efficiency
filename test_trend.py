from datetime import datetime
from pathlib import Path

import pytest

from trend import build_timelines, snapshot_time, trend_rows


def pool(address, volume, liquidity, name="A / B"):
    return {"name": name, "address": address, "volume_24h": volume, "liquidity": liquidity}


def test_snapshot_time_from_filename():
    path = Path("meteora_data_2026-11-09_13-19-20.json")
    assert snapshot_time(path) == datetime(2026, 11, 9, 13, 19, 20)


def test_pools_without_address_are_ignored():
    snapshots = [(datetime(2026, 11, 9), [{"name": "X", "volume_24h": 1, "liquidity": 100_000}])]
    assert build_timelines(snapshots) == {}


def test_trend_needs_two_readings():
    snapshots = [(datetime(2026, 11, 9), [pool("addr1", 100_000, 100_000)])]
    assert trend_rows(build_timelines(snapshots)) == []


def test_trend_change_and_order():
    day1, day2 = datetime(2026, 11, 9), datetime(2026, 11, 10)
    snapshots = [
        (day1, [pool("up", 100_000, 100_000), pool("down", 300_000, 100_000)]),
        (day2, [pool("up", 300_000, 100_000), pool("down", 100_000, 100_000)]),
    ]
    rows = trend_rows(build_timelines(snapshots))
    assert [r["address"] for r in rows] == ["up", "down"]
    assert rows[0]["change"] == pytest.approx(2.0)