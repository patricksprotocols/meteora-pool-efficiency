# Meteora Pool Efficiency

Quite a small Python pipeline that pulls in Meteora pool data from the GeckoTerminal API,
ranks pools by their capital efficiency (24h volume divided by liquidity) and tracks
how the ratio changes from day to day.

## How it works

- `fetch.py` requests up to 60 pools (3 pages) from the API, saves them to
  `meteora_data.json` and copies a timestamped snapshot into `history/`, though I initially started by requesting 20 pools (1 page) from the API.
- `main.py` reads the data, drops pools below a minimum liquidity, and prints a
  ranked table.
- `trend.py` reads every snapshot in `history/` and compares each pool's
  efficiency over time, matching pools by address.
- `history.py` holds the snapshot-copy function used by `fetch.py`.

## Run it

    pip install requests pytest
    python fetch.py
    python main.py
    python trend.py
    pytest

`trend.py` needs at least two snapshots that contain the same pool, so run
`fetch.py` on separate days before expecting output.

## The metric

Volume / liquidity shows how much trading a pool handles for each dollar of
capital in it. A high value suggests more fee potential for liquidity providers.
It is not profit: it ignores fee rates, impermanent loss and rewards.

## Choices I made

- **Minimum liquidity of \$100,000.** Small pools with a spike in volume kept climbing the rankings.
  I tested both \$50,000 and \$100,000 and stuck with the higher amount.
  A single cutoff number doesn't tell the whole story.
- **Matching pools by address.** Several pairs show up more than once with different results, so the name
  can't be trusted to identify the pool correctly.

## Data

Data comes from the GeckoTerminal API (DEX id `meteora`). I have not confirmed
that every pool returned is a DLMM pool, so I describe them as Meteora pools.
An early version ran on handwritten sample data. My first live attempt
failed because I called the GeckoTerminal website instead of the API.

## Findings from 10 November 2026

- 25 of 60 pools passed the \$100,000 filter. MUSK / USDC ranked first at 15.43x
  with about \$106,800 of liquidity, just above the cutoff.
- The largest pools had low ratios. ANTFUN / USDT has about \$14.7M of liquidity
  and a 0.09x ratio.
- The same pair can be very different pools. One HYPE / SOL pool shows 10.74x
  and another 0.62x. I don't yet know why.
- This is one snapshot, so it shows no trend yet. 

## Limitations and next steps

- I only have a few days of snapshots, so the trends don't mean much yet.
- If a pool's liquidity moves across the cutoff between days, it drops out of the trend.
- There's no fee, impermanent loss or reward data yet.
- Next, I want to load the data into pandas, see how pool size relates to
  efficiency, and add fee yield.

## Tests

Run `pytest` to run all 11 tests. They cover the ranking, the liquidity filter,
the snapshot copy and the trend logic.

## Note on tools

I used AI assistants (Claude and Google AI) to review my code and help with
drafts. I made the decisions myself: the liquidity cutoff, matching pools by
address, which data to pull, and running the tests.
