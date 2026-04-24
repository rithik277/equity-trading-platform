# ─────────────────────────────────────────────
# data_builder.py
# Phase 1: Build the dataset for our platform
# ─────────────────────────────────────────────

import yfinance as yf
import pandas as pd
import random
import numpy as np
from datetime import datetime

# ── STEP A: Define our universe ──────────────

# 20 real S&P 500 stocks across different sectors
SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",   # Tech
    "JPM", "BAC", "GS", "MS", "C",              # Finance
    "JNJ", "PFE", "MRK", "ABT", "UNH",          # Healthcare
    "XOM", "CVX", "BA", "CAT", "GE"             # Energy/Industrial
]

# 4 real algorithm types used on equity desks
ALGO_TYPES = ["VWAP", "TWAP", "IS", "POV"]
# VWAP = Volume Weighted Average Price
# TWAP = Time Weighted Average Price
# IS   = Implementation Shortfall
# POV  = Percentage of Volume

# 20 simulated institutional clients
CLIENTS = [f"CLIENT_{str(i).zfill(3)}" for i in range(1, 21)]
# This creates: CLIENT_001, CLIENT_002 ... CLIENT_020

print("Step A done — universe defined")
print(f"  {len(SYMBOLS)} stocks, {len(ALGO_TYPES)} algos, {len(CLIENTS)} clients")  

# ── STEP B: Download real historical prices ──

def download_prices(symbols, start="2023-01-01", end="2024-01-01"):
    """
    Downloads one full year of daily OHLCV data
    for every stock in our symbols list.

    OHLCV = Open, High, Low, Close, Volume
    These are real market prices from Yahoo Finance.
    """

    print("\nStep B — Downloading real price data...")
    
    all_data = []   # empty list, we will fill it stock by stock

    for symbol in symbols:

        #print(f"  Fetching {symbol}...")

        # Download data for this one stock
        df = yf.download(symbol, start=start, end=end, progress=False)

        # yfinance gives us multi-level columns, flatten them
        df.columns = [col[0].lower() if isinstance(col, tuple) 
                      else col.lower() for col in df.columns]

        # Reset index so 'Date' becomes a regular column
        df = df.reset_index()

        # Rename 'Date' to 'date' (lowercase, consistent style)
        df = df.rename(columns={"Date": "date"})

        # Add a column so we know which stock this row belongs to
        df["symbol"] = symbol

        # Keep only the columns we actually need
        df = df[["date", "symbol", "open", "high", "low", "close", "volume"]]

        # Add to our growing list
        all_data.append(df)

    # Stack all stocks into one big table
    prices = pd.concat(all_data, ignore_index=True)

    # Calculate VWAP for each row (we need this later for slippage)
    # VWAP approximation: (High + Low + Close) / 3
    prices["vwap"] = (prices["high"] + prices["low"] + prices["close"]) / 3

    print(f"\n  Done! Downloaded {len(prices)} rows of price data")
    print(f"  Date range: {prices['date'].min()} to {prices['date'].max()}")

    return prices


# Run it
prices = download_prices(SYMBOLS)

# Save a copy so we don't re-download every time
prices.to_csv("data/prices.csv", index=False)
print("\n  Saved to data/prices.csv")


# ── STEP C: Build trade execution records ────

def build_trades(prices):
    """
    For each row of real price data we simulate a trade execution.
    This is where we engineer the execution layer on top of real prices.

    Each trade record will have:
    - Which client placed the order
    - Which algorithm was used
    - How much they wanted to buy/sell (order_qty)
    - How much actually got filled (filled_qty)
    - What price they wanted (order_price)
    - What price they actually got (exec_price)
    - The slippage (difference between what they wanted vs got)
    """

    print("\nStep C — Building trade execution records...")

    random.seed(42)   # makes results reproducible every time you run
    np.random.seed(42)

    trades = []   # empty list, we fill row by row

    for _, row in prices.iterrows():
        # Each day + stock becomes one trade record

        # ── Assign a random client and algo ──
        client  = random.choice(CLIENTS)
        algo    = random.choice(ALGO_TYPES)
        side    = random.choice(["BUY", "SELL"])

        # ── Order size: realistic institutional sizes ──
        # Institutions trade in thousands of shares
        order_qty = random.randint(500, 50000)

        # ── Fill rate: how much of the order actually got filled ──
        # VWAP and TWAP algos tend to fill better than IS and POV
        if algo in ["VWAP", "TWAP"]:
            fill_pct = np.random.uniform(0.85, 1.00)  # 85% to 100% filled
        else:
            fill_pct = np.random.uniform(0.60, 0.95)  # 60% to 95% filled

        filled_qty = int(order_qty * fill_pct)

        # ── Order price: what the client wanted ──
        # Use the open price as the intended/arrival price
        order_price = round(float(row["open"]), 4)

        # ── Execution price: what they actually got ──
        # Real execution is never perfect — there is always slippage
        # Slippage = small random % deviation from order price
        # BUY orders tend to get slightly worse prices (pay more)
        # SELL orders tend to get slightly worse prices (receive less)

        if side == "BUY":
            # Slippage adds cost — execution price is slightly higher
            slippage_pct = np.random.uniform(0.0001, 0.0050)
            exec_price = round(order_price * (1 + slippage_pct), 4)
        else:
            # Slippage reduces proceeds — execution price is slightly lower
            slippage_pct = np.random.uniform(0.0001, 0.0050)
            exec_price = round(order_price * (1 - slippage_pct), 4)

        # ── Slippage in basis points (bps) ──
        # Basis points is the standard unit on trading desks
        # 1 bps = 0.01% — traders never say "0.05%", they say "5 bps"
        slippage_bps = round(slippage_pct * 10000, 2)

        # ── P&L per trade ──
        # For BUY: P&L = (VWAP - exec_price) * filled_qty
        # If we bought below VWAP, that is good execution (positive P&L)
        # For SELL: P&L = (exec_price - VWAP) * filled_qty
        # If we sold above VWAP, that is good execution (positive P&L)

        vwap = float(row["vwap"])

        if side == "BUY":
            pnl = round((vwap - exec_price) * filled_qty, 2)
        else:
            pnl = round((exec_price - vwap) * filled_qty, 2)

        # ── Anomaly flag (for Module 3 — Surveillance) ──
        # Flag a trade if slippage is unusually high (above 40 bps)
        # OR if the order is unusually large (above 40,000 shares)
        is_anomaly = slippage_bps > 40 or order_qty > 40000

        # ── Anomaly reason ──
        if slippage_bps > 40 and order_qty > 40000:
            anomaly_reason = "HIGH SLIPPAGE + LARGE ORDER"
        elif slippage_bps > 40:
            anomaly_reason = "HIGH SLIPPAGE"
        elif order_qty > 40000:
            anomaly_reason = "LARGE ORDER"
        else:
            anomaly_reason = None

        # ── Append this trade to our list ──
        trades.append({
            "trade_id"       : f"TRD-{len(trades)+1:05d}",
            "date"           : row["date"],
            "symbol"         : row["symbol"],
            "client_id"      : client,
            "algo_type"      : algo,
            "side"           : side,
            "order_qty"      : order_qty,
            "filled_qty"     : filled_qty,
            "fill_rate"      : round(fill_pct * 100, 2),
            "order_price"    : order_price,
            "exec_price"     : exec_price,
            "vwap"           : round(vwap, 4),
            "slippage_bps"   : slippage_bps,
            "pnl"            : pnl,
            "is_anomaly"     : is_anomaly,
            "anomaly_reason" : anomaly_reason
        })

    # Convert list to a DataFrame (table)
    trades_df = pd.DataFrame(trades)

    print(f"  Built {len(trades_df)} trade records")
    print(f"  Anomalies flagged: {trades_df['is_anomaly'].sum()}")
    print(f"  Total P&L across all trades: ${trades_df['pnl'].sum():,.2f}")

    return trades_df


# Run it
trades = build_trades(prices)

# Save to CSV
trades.to_csv("data/trades.csv", index=False)
print("\n  Saved to data/trades.csv")

print(trades.head())