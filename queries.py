# ─────────────────────────────────────────────
# queries.py
# Phase 2: All SQL analytical queries
# One function per business question
# ─────────────────────────────────────────────

import sqlite3
import pandas as pd

# ── Helper: connect to database ───────────────

def get_connection():
    return sqlite3.connect("database/trading.db")


# ════════════════════════════════════════════════
# MODULE 1 QUERIES — Execution Analytics
# ════════════════════════════════════════════════

def algo_performance():
    """
    Question: Which algorithm performs best?
    Measures: Average fill rate and average slippage per algo type
    Used in: Module 1 — Execution Analytics tab
    """

    conn = get_connection()

    query = """
        SELECT
            algo_type,
            ROUND(AVG(fill_rate), 2)      AS avg_fill_rate,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps,
            COUNT(*)                       AS total_trades
        FROM trades
        GROUP BY algo_type
        ORDER BY avg_fill_rate DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def slippage_by_symbol():
    """
    Question: Which stocks have the worst slippage?
    Measures: Average slippage per symbol
    Used in: Module 1 — Execution Analytics tab
    """

    conn = get_connection()

    query = """
        SELECT
            symbol,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps,
            ROUND(AVG(fill_rate), 2)       AS avg_fill_rate,
            COUNT(*)                        AS total_trades
        FROM trades
        GROUP BY symbol
        ORDER BY avg_slippage_bps DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def daily_slippage_trend():
    """
    Question: How does slippage change over time?
    Measures: Average daily slippage across all trades
    Used in: Module 1 — line chart over time
    """

    conn = get_connection()

    query = """
        SELECT
            date,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps
        FROM trades
        GROUP BY date
        ORDER BY date ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ════════════════════════════════════════════════
# MODULE 2 QUERIES — Client Profitability
# ════════════════════════════════════════════════

def client_pnl():
    """
    Question: Which clients are most profitable?
    Measures: Total P&L, trade count, avg slippage per client
    Used in: Module 2 — Client Profitability tab
    """

    conn = get_connection()

    query = """
        SELECT
            client_id,
            ROUND(SUM(pnl), 2)            AS total_pnl,
            COUNT(*)                        AS total_trades,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps,
            ROUND(AVG(fill_rate), 2)       AS avg_fill_rate
        FROM trades
        GROUP BY client_id
        ORDER BY total_pnl DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def client_symbol_activity():
    """
    Question: Which stocks does each client trade most?
    Measures: Number of trades per client per symbol
    Used in: Module 2 — heatmap
    """

    conn = get_connection()

    query = """
        SELECT
            client_id,
            symbol,
            COUNT(*)          AS trade_count,
            ROUND(SUM(pnl), 2) AS total_pnl
        FROM trades
        GROUP BY client_id, symbol
        ORDER BY client_id, trade_count DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def client_algo_preference():
    """
    Question: Which algorithm does each client prefer?
    Measures: Trade count per client per algo
    Used in: Module 2 — stacked bar chart
    """

    conn = get_connection()

    query = """
        SELECT
            client_id,
            algo_type,
            COUNT(*)            AS trade_count
        FROM trades
        GROUP BY client_id, algo_type
        ORDER BY client_id, trade_count DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ════════════════════════════════════════════════
# MODULE 3 QUERIES — Surveillance & Anomalies
# ════════════════════════════════════════════════

def flagged_trades():
    """
    Question: Which trades were flagged as anomalies?
    Measures: All trades where is_anomaly = True
    Used in: Module 3 — flagged trades table
    """

    conn = get_connection()

    query = """
        SELECT
            trade_id,
            date,
            symbol,
            client_id,
            algo_type,
            side,
            order_qty,
            slippage_bps,
            pnl,
            anomaly_reason
        FROM trades
        WHERE is_anomaly = 1
        ORDER BY slippage_bps DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def anomaly_summary():
    """
    Question: How many anomalies per type?
    Measures: Count of each anomaly reason
    Used in: Module 3 — summary bar chart
    """

    conn = get_connection()

    query = """
        SELECT
            anomaly_reason,
            COUNT(*)                      AS count,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps,
            ROUND(SUM(pnl), 2)            AS total_pnl
        FROM trades
        WHERE is_anomaly = 1
        GROUP BY anomaly_reason
        ORDER BY count DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def client_anomaly_count():
    """
    Question: Which clients trigger the most anomalies?
    Measures: Anomaly count per client
    Used in: Module 3 — risk ranking table
    """

    conn = get_connection()

    query = """
        SELECT
            client_id,
            COUNT(*)                        AS anomaly_count,
            ROUND(AVG(slippage_bps), 2)   AS avg_slippage_bps,
            ROUND(SUM(pnl), 2)            AS total_pnl
        FROM trades
        WHERE is_anomaly = 1
        GROUP BY client_id
        ORDER BY anomaly_count DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ════════════════════════════════════════════════
# TEST — Run all queries and preview results
# ════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 50)
    print("MODULE 1 — Execution Analytics")
    print("=" * 50)

    print("\nAlgo Performance:")
    print(algo_performance().to_string(index=False))

    print("\nSlippage by Symbol (Top 5):")
    print(slippage_by_symbol().head().to_string(index=False))

    print("\n" + "=" * 50)
    print("MODULE 2 — Client Profitability")
    print("=" * 50)

    print("\nTop 5 Clients by P&L:")
    print(client_pnl().head().to_string(index=False))

    print("\n" + "=" * 50)
    print("MODULE 3 — Surveillance")
    print("=" * 50)

    print("\nAnomaly Summary:")
    print(anomaly_summary().to_string(index=False))

    print("\nTop 5 Clients by Anomaly Count:")
    print(client_anomaly_count().head().to_string(index=False))

    print("\nAll queries working correctly!")
