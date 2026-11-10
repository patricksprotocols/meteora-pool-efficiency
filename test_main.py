import pytest

from main import rank_by_efficiency


def make_pool(name, volume, liquidity):
    return {"name": name, "volume_24h": volume, "liquidity": liquidity}


def test_highest_efficiency_first():
    pools = [make_pool("A", 100, 1000), make_pool("B", 500, 1000)]
    assert [p["name"] for p in rank_by_efficiency(pools)] == ["B", "A"]


def test_efficiency_value():
    ranked = rank_by_efficiency([make_pool("A", 250, 1000)])
    assert ranked[0]["efficiency"] == pytest.approx(0.25)


def test_zero_liquidity_skipped():
    pools = [make_pool("Empty", 100, 0), make_pool("Ok", 100, 1000)]
    assert [p["name"] for p in rank_by_efficiency(pools)] == ["Ok"]


def test_missing_liquidity_skipped():
    pools = [{"name": "NoLiq", "volume_24h": 100}, make_pool("Ok", 100, 1000)]
    assert [p["name"] for p in rank_by_efficiency(pools)] == ["Ok"]

def test_min_liquidity_filters_small_pools():
    pools = [make_pool("Tiny", 1000, 100), make_pool("Big", 1000, 100_000)]
    ranked = rank_by_efficiency(pools, min_liquidity=50_000)
    assert [p["name"] for p in ranked] == ["Big"]