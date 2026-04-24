# 🏦 Equity Trading Intelligence Platform

A Python + SQL analytics platform simulating the core workflows 
of an Equity Electronic Trading desk — execution quality analysis, 
client profitability tracking, and trade surveillance.

---

## 📸 Dashboard Preview

Three-tab Plotly Dash dashboard with real-time filtering:
- Tab 1: Execution Analytics
- Tab 2: Client Profitability  
- Tab 3: Surveillance & Alerts

---

## 🎯 What This Project Covers

| Trading Desk Concept      | Implementation                              |
|---------------------------|---------------------------------------------|
| Algorithm performance     | Fill rate & slippage by VWAP/TWAP/IS/POV   |
| Execution quality         | Slippage in basis points vs VWAP benchmark  |
| Client profitability      | P&L per client, algo preference analysis    |
| Liquidity flow monitoring | Daily slippage trends across 20 S&P stocks  |
| Trade surveillance        | Anomaly detection — high slippage & size    |

---

## 🗂️ Project Structure


equity_trading_platform/
│
├── data/                     # Raw and processed data
│   ├── prices.csv            # Real S&P 500 OHLCV data (Yahoo Finance)
│   └── trades.csv            # 5,000 engineered execution records
│
├── database/
│   └── trading.db            # SQLite database
│
├── analyzer/
│   └── trade_analyzer.py     # OOP analytics class
│
├── dashboard/
│   └── app.py                # Plotly Dash dashboard (3 tabs)
│
├── data_builder.py           # Builds dataset from real prices
├── db_builder.py             # Loads data into SQLite
├── queries.py                # All SQL analytical queries
└── run_analyzer.py           # CLI summary report

---

## 📊 Dataset

- **Price data**: Real 2023 daily OHLCV for 20 S&P 500 stocks 
  sourced via Yahoo Finance (yfinance)
- **Execution layer**: Engineered on top of real prices
  - 4 algorithm types: VWAP, TWAP, IS, POV
  - 20 simulated institutional clients
  - Realistic slippage (0.01 to 0.50%) calculated against real prices
  - P&L measured against VWAP benchmark
  - Anomaly flags for high slippage (>40 bps) and large orders (>40,000 shares)

---

## 🔍 Key Metrics Produced

**Execution Analytics**
- Average fill rate per algorithm
- Average slippage in basis points per stock
- Daily slippage trend over full year

**Client Profitability**
- Total P&L vs VWAP benchmark per client
- Algorithm preference breakdown per client
- Average execution cost per client

**Surveillance**
- 1,891 anomaly flags across 5,000 trades
- Riskiest clients ranked by anomaly count
- Filterable flagged trades table with alert reasons

---

## 🛠️ Tech Stack

| Tool          | Purpose                              |
|---------------|--------------------------------------|
| Python 3.13   | Core language                        |
| SQLite3       | Embedded SQL database (built-in)     |
| Pandas        | Data manipulation                    |
| yfinance      | Real market data download            |
| Plotly Dash   | Interactive web dashboard            |
| OOP (classes) | TradeAnalyzer analytics engine       |

---

## 🚀 How to Run

**1. Install dependencies**
```bash
pip install yfinance pandas plotly dash
```

**2. Build the dataset**
```bash
python data_builder.py
```

**3. Load the database**
```bash
python db_builder.py
```

**4. Run the CLI summary**
```bash
python run_analyzer.py
```

**5. Launch the dashboard**
```bash
python dashboard/app.py
```
Then open `http://127.0.0.1:8050/` in your browser.

---

## 💡 Business Context

Electronic trading desks at investment banks monitor three things 
constantly: how well their algorithms execute orders, which clients 
generate the most value, and which trades need risk review.

This platform replicates that monitoring workflow using real market 
prices as the benchmark, giving execution metrics genuine grounding 
in actual 2023 S&P 500 market conditions.