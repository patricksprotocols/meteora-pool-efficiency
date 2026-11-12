import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "meteora_data.json"
MIN_LIQUIDITY = 100000


def load_pools(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def rank_by_efficiency(pools, min_liquidity=0):
    ranked = []
    for pool in pools:
        liquidity = pool.get("liquidity", 0)
        if liquidity <= 0 or liquidity < min_liquidity:
            continue
        ranked.append({**pool, "efficiency": pool["volume_24h"] / liquidity})
    return sorted(ranked, key=lambda p: p["efficiency"], reverse=True)


def short_address(address):
    return f"{address[:4]}...{address[-4:]}" if address else "-"


def print_report(ranked):
    header = (
        f"{'Pool':<24}{'Address':<14}"
        f"{'24h Volume':>18}{'Liquidity':>18}{'Vol/Liq':>10}"
    )
    print(header)
    print("-" * len(header))
    for p in ranked:
        print(
            f"{p['name']:<24}"
            f"{short_address(p.get('address')):<14}"
            f"{p['volume_24h']:>18,.2f}"
            f"{p['liquidity']:>18,.2f}"
            f"{p['efficiency']:>9.2f}x"
        )
    top = ranked[0]
    print(f"\nHighest capital efficiency: {top['name']} ({top['efficiency']:.2f}x)")


def main():
    try:
        pools = load_pools(DATA_FILE)
    except FileNotFoundError:
        sys.exit(f"Data file not found: {DATA_FILE}")

    ranked = rank_by_efficiency(pools, MIN_LIQUIDITY)
    if not ranked:
        sys.exit(f"No pools with at least ${MIN_LIQUIDITY:,} in liquidity.")

    print_report(ranked)
    print(f"\nPools shown: {len(ranked)} of {len(pools)} (min liquidity ${MIN_LIQUIDITY:,})")


if __name__ == "__main__":
    main()