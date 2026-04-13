#!/usr/bin/env python3
"""
Iran War Portfolio Tracker — Price Fetcher
Fetches daily adjusted closing prices for all tracked assets via yfinance
and writes/updates tracker.csv (root + docs/ copy for GitHub Pages).

Usage:
    python fetch_prices.py            # fetch from last known date -> today
    python fetch_prices.py --full     # re-fetch full history from START_DATE
"""

import argparse
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# ─── Configuration ────────────────────────────────────────────────────────────

START_DATE = "2026-02-28"   # Thesis inception date (Iran war start)

TICKERS = [
    # Energy — Strait of Hormuz exposure
    "USO", "XLE", "XOM", "CVX",
    # Tanker shipping
    "BWET",
    # LNG
    "LNG",
    # Defense
    "LMT", "NOC", "RTX", "ITA", "PLTR", "KTOS",
    # Commodities / Safe haven
    "GLD", "HGER", "REMX",
    # Hedge / De-escalation
    "SCO", "TAIL",
    # Benchmarks
    "SPY", "QQQ",
]

ROOT_CSV  = Path("tracker.csv")
DOCS_CSV  = Path("docs") / "tracker.csv"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_existing() -> pd.DataFrame:
    """Load existing tracker.csv if present."""
    if ROOT_CSV.exists():
        df = pd.read_csv(ROOT_CSV, index_col="Date", parse_dates=False)
        return df
    return pd.DataFrame()


def fetch_closes(start: str, end: str) -> pd.DataFrame:
    """Download adjusted close prices for all tickers."""
    print(f"  Downloading {len(TICKERS)} tickers from {start} to {end} …")
    raw = yf.download(
        tickers=TICKERS,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    if raw.empty:
        print("  No data returned — markets may be closed or dates out of range.")
        return pd.DataFrame()

    # yfinance returns MultiIndex columns (metric, ticker) for multiple tickers
    if isinstance(raw.columns, pd.MultiIndex):
        closes = raw["Close"].copy()
    else:
        # Single ticker fallback (shouldn't happen with full list)
        closes = raw[["Close"]].copy()
        closes.columns = TICKERS[:1]

    # Reindex to requested tickers (some may be missing)
    for t in TICKERS:
        if t not in closes.columns:
            print(f"  WARNING: no data for {t}")

    closes = closes.reindex(columns=TICKERS)
    closes.index = pd.to_datetime(closes.index).strftime("%Y-%m-%d")
    closes.index.name = "Date"
    return closes.round(4)


def merge(existing: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Merge new data into existing, new rows win on overlap."""
    if existing.empty:
        return new
    combined = existing.combine_first(new)
    combined.update(new)
    combined.sort_index(inplace=True)
    return combined.round(4)


def write(df: pd.DataFrame) -> None:
    """Write tracker.csv to repo root and docs/ copy."""
    DOCS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ROOT_CSV)
    df.to_csv(DOCS_CSV)
    print(f"  Wrote {len(df)} rows × {len(df.columns)} tickers to {ROOT_CSV} and {DOCS_CSV}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch portfolio prices")
    parser.add_argument("--full", action="store_true",
                        help="Re-fetch full history from START_DATE")
    args = parser.parse_args()

    today = date.today().isoformat()
    # Fetch through tomorrow so today's close is included
    end = (date.today() + timedelta(days=1)).isoformat()

    existing = load_existing()

    if args.full or existing.empty:
        fetch_start = START_DATE
        print(f"Full fetch: {fetch_start} -> {today}")
    else:
        # Overlap by 2 days to catch late-arriving data / corrections
        last = existing.index[-1]
        fetch_start = (
            pd.Timestamp(last) - timedelta(days=2)
        ).strftime("%Y-%m-%d")
        print(f"Incremental fetch: {fetch_start} -> {today}")

    new_data = fetch_closes(fetch_start, end)

    if new_data.empty:
        print("Nothing to update.")
        sys.exit(0)

    merged = merge(existing, new_data)
    write(merged)

    # Print quick summary
    last_row = merged.iloc[-1]
    print(f"\nLatest close ({merged.index[-1]}):")
    for ticker in TICKERS:
        if ticker in last_row and pd.notna(last_row[ticker]):
            print(f"  {ticker:6s}  ${last_row[ticker]:>10.2f}")


if __name__ == "__main__":
    main()
