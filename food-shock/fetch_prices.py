#!/usr/bin/env python3
"""
Food Shock Portfolio Tracker — Price Fetcher
Post-ceasefire delayed food/fertilizer shock thesis (Santiago Capital / Milkshakes pod).

Fetches daily OHLCV for all tracked tickers and appends to tracker.csv (long format).
Each row: date, ticker, open, high, low, close, volume, side

Usage:
    python fetch_prices.py            # incremental from last known date
    python fetch_prices.py --full     # full re-fetch from START_DATE
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

START_DATE = "2026-04-13"

ASSETS = {
    "WEAT": {"name": "Teucrium Wheat ETF",           "cat": "Agriculture",      "side": "LONG",      "target": "+20-40%",        "tf": "6-9 months"},
    "CORN": {"name": "Teucrium Corn ETF",             "cat": "Agriculture",      "side": "LONG",      "target": "+15-30%",        "tf": "6-9 months"},
    "CF":   {"name": "CF Industries",                 "cat": "Fertilizer",       "side": "LONG",      "target": "momentum",       "tf": "1-3 months"},
    "NTR":  {"name": "Nutrien",                       "cat": "Fertilizer",       "side": "LONG",      "target": "+20%",           "tf": "1-3 months"},
    "MOS":  {"name": "Mosaic",                        "cat": "Fertilizer",       "side": "LONG",      "target": "+25%",           "tf": "1-3 months"},
    "DBA":  {"name": "Invesco DB Agriculture ETF",    "cat": "Soft Commodities", "side": "LONG",      "target": "+15%",           "tf": "6-9 months"},
    "PDBA": {"name": "Invesco Agriculture ETF (noK1)","cat": "Soft Commodities", "side": "LONG",      "target": "+15%",           "tf": "6-9 months"},
    "ADM":  {"name": "Archer-Daniels-Midland",        "cat": "Merchants",        "side": "WATCH",     "target": "pullback entry", "tf": "TBD"},
    "BG":   {"name": "Bunge",                         "cat": "Merchants",        "side": "WATCH",     "target": "pullback entry", "tf": "TBD"},
    "UNG":  {"name": "US Natural Gas ETF",            "cat": "Natural Gas",      "side": "SHORT",     "target": "-20%",           "tf": "spread"},
    "GLD":  {"name": "SPDR Gold Shares",              "cat": "Metals",           "side": "WATCH",     "target": "low $4,000s",    "tf": "200DMA entry"},
    "SLV":  {"name": "iShares Silver Trust",          "cat": "Metals",           "side": "WATCH",     "target": "~$60",           "tf": "200DMA entry"},
    "XLY":  {"name": "Consumer Discretionary ETF",    "cat": "Hedge/Short",      "side": "SHORT",     "target": "-15%",           "tf": "6-9 months"},
    "VIXY": {"name": "ProShares VIX ETF",             "cat": "Hedge/Short",      "side": "WATCH",     "target": "VIX < 20",       "tf": "tactical"},
    "SPY":  {"name": "S&P 500",                       "cat": "Benchmark",        "side": "BENCHMARK", "target": "200DMA resist.",  "tf": "N/A"},
    "QQQ":  {"name": "Nasdaq 100",                    "cat": "Benchmark",        "side": "BENCHMARK", "target": "200DMA resist.",  "tf": "N/A"},
    "DIA":  {"name": "Dow Jones ETF",                 "cat": "Benchmark",        "side": "BENCHMARK", "target": "200DMA resist.",  "tf": "N/A"},
}

VIX_TICKER = "^VIX"
ROOT_CSV  = Path("tracker.csv")
DOCS_CSV  = Path("..") / "docs" / "food-shock" / "tracker.csv"


def load_existing() -> pd.DataFrame:
    if ROOT_CSV.exists() and ROOT_CSV.stat().st_size > 50:
        return pd.read_csv(ROOT_CSV, parse_dates=False)
    return pd.DataFrame(columns=["date","ticker","open","high","low","close","volume","side"])


def fetch_ohlcv(tickers: list, start: str, end: str) -> pd.DataFrame:
    print(f"  Downloading {len(tickers)} tickers from {start} to {end} ...")
    raw = yf.download(tickers=tickers, start=start, end=end,
                      auto_adjust=True, progress=False, threads=True)
    if raw.empty:
        print("  No data returned.")
        return pd.DataFrame()
    rows = []
    for ticker in tickers:
        try:
            df_t = raw.xs(ticker, axis=1, level=1).dropna(how="all") \
                   if isinstance(raw.columns, pd.MultiIndex) else raw.dropna(how="all")
            for dt, row in df_t.iterrows():
                if pd.isna(row.get("Close")): continue
                rows.append({
                    "date":   pd.Timestamp(dt).strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "open":   round(float(row["Open"]),  4),
                    "high":   round(float(row["High"]),  4),
                    "low":    round(float(row["Low"]),   4),
                    "close":  round(float(row["Close"]), 4),
                    "volume": int(row["Volume"]) if not pd.isna(row.get("Volume")) else 0,
                    "side":   ASSETS[ticker]["side"] if ticker in ASSETS else "WATCH",
                })
        except Exception as e:
            print(f"  WARNING: skipping {ticker}: {e}")
    return pd.DataFrame(rows)


def merge(existing: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
    if existing.empty: return new_data.copy()
    combined = pd.concat([existing, new_data], ignore_index=True)
    combined.drop_duplicates(subset=["date","ticker"], keep="last", inplace=True)
    combined.sort_values(["date","ticker"], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


def write(df: pd.DataFrame) -> None:
    DOCS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ROOT_CSV, index=False)
    df.to_csv(DOCS_CSV, index=False)
    print(f"  Wrote {len(df)} rows ({df['ticker'].nunique()} tickers)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    today = date.today().isoformat()
    end   = (date.today() + timedelta(days=1)).isoformat()
    existing = load_existing()
    all_tickers = list(ASSETS.keys()) + [VIX_TICKER]
    if args.full or existing.empty:
        fetch_start = START_DATE
    else:
        last = existing["date"].max()
        fetch_start = (pd.Timestamp(last) - timedelta(days=2)).strftime("%Y-%m-%d")
    new_data = fetch_ohlcv(all_tickers, fetch_start, end)
    if new_data.empty:
        print("Nothing to update.")
        sys.exit(0)
    merged = merge(existing, new_data)
    write(merged)


if __name__ == "__main__":
    main()
