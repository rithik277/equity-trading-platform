# ─────────────────────────────────────────────
# analyzer/trade_analyzer.py
# Phase 3: The TradeAnalyzer OOP Class
# ─────────────────────────────────────────────

import sqlite3
import pandas as pd
import sys
import os

# This lets us import from our queries.py file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import queries


# ── What is a Class? ─────────────────────────
#
# A class is a blueprint for an object.
# Think of it like this:
#
#   Blueprint (Class)  →  TradeAnalyzer
#   Object (Instance)  →  analyzer = TradeAnalyzer()
#
# Once you create the object, it remembers
# its own data and has its own methods (functions).
# That is the core idea of Object Oriented Programming.
# ─────────────────────────────────────────────

class TradeAnalyzer:
    """
    A professional analytics class for the
    Equity Trading Intelligence Platform.

    Wraps all SQL queries into clean, reusable
    methods that can be called by the dashboard.
    """

    # ── __init__: runs automatically when you ──
    # ── create a TradeAnalyzer object          ──

    def __init__(self):
        """
        Called automatically when you do:
            analyzer = TradeAnalyzer()

        Loads all data into memory once,
        so we don't hit the database on every call.
        """

        print("TradeAnalyzer initializing...")

        # Load all data upfront using our queries
        self.algo_perf        = queries.algo_performance()
        self.slippage_symbol  = queries.slippage_by_symbol()
        self.daily_slippage   = queries.daily_slippage_trend()
        self.client_pnl       = queries.client_pnl()
        self.client_activity  = queries.client_symbol_activity()
        self.client_algo_pref = queries.client_algo_preference()
        self.flagged          = queries.flagged_trades()
        self.anomaly_summary  = queries.anomaly_summary()
        self.client_anomalies = queries.client_anomaly_count()

        print("  All data loaded successfully")
        print(f"  Flagged trades: {len(self.flagged)}")
        print(f"  Total clients: {len(self.client_pnl)}")


    # ════════════════════════════════════════════
    # MODULE 1 METHODS — Execution Analytics
    # ════════════════════════════════════════════

    def best_performing_algo(self):
        """
        Returns the algo with the highest avg fill rate.
        This is the single best performer on execution quality.
        """

        best = self.algo_perf.iloc[0]  # first row = highest fill rate

        print("\n── Best Performing Algorithm ──")
        print(f"  Algo     : {best['algo_type']}")
        print(f"  Fill Rate: {best['avg_fill_rate']}%")
        print(f"  Slippage : {best['avg_slippage_bps']} bps")

        return best


    def worst_slippage_symbol(self):
        """
        Returns the stock with the highest average slippage.
        High slippage = expensive to trade = bad execution.
        """

        worst = self.slippage_symbol.iloc[0]  # first row = worst slippage

        print("\n── Worst Slippage Symbol ──")
        print(f"  Symbol  : {worst['symbol']}")
        print(f"  Slippage: {worst['avg_slippage_bps']} bps")

        return worst


    def execution_quality_summary(self):
        """
        Prints a full summary of execution quality
        across all algorithms.
        """

        print("\n── Execution Quality by Algorithm ──")
        print(self.algo_perf.to_string(index=False))

        return self.algo_perf


    # ════════════════════════════════════════════
    # MODULE 2 METHODS — Client Profitability
    # ════════════════════════════════════════════

    def top_clients(self, n=5):
        """
        Returns the top N clients by total P&L.
        Default is top 5 if you don't specify.

        Example:
            analyzer.top_clients()      # top 5
            analyzer.top_clients(n=10)  # top 10
        """

        top = self.client_pnl.head(n)

        print(f"\n── Top {n} Clients by P&L ──")
        print(top[["client_id", "total_pnl",
                    "total_trades", "avg_slippage_bps"]].to_string(index=False))

        return top


    def bottom_clients(self, n=5):
        """
        Returns the bottom N clients by total P&L.
        These are the clients losing the most money.
        """

        bottom = self.client_pnl.tail(n)

        print(f"\n── Bottom {n} Clients by P&L ──")
        print(bottom[["client_id", "total_pnl",
                       "total_trades", "avg_slippage_bps"]].to_string(index=False))

        return bottom


    def client_profile(self, client_id):
        """
        Returns a full profile for one specific client.

        Example:
            analyzer.client_profile("CLIENT_001")
        """

        # Filter down to just this client
        pnl_row = self.client_pnl[
            self.client_pnl["client_id"] == client_id
        ]

        anomaly_row = self.client_anomalies[
            self.client_anomalies["client_id"] == client_id
        ]

        print(f"\n── Client Profile: {client_id} ──")

        if pnl_row.empty:
            print(f"  Client {client_id} not found.")
            return None

        print(f"  Total P&L    : ${pnl_row['total_pnl'].values[0]:,.2f}")
        print(f"  Total Trades : {pnl_row['total_trades'].values[0]}")
        print(f"  Avg Slippage : {pnl_row['avg_slippage_bps'].values[0]} bps")
        print(f"  Avg Fill Rate: {pnl_row['avg_fill_rate'].values[0]}%")

        if not anomaly_row.empty:
            print(f"  Anomaly Count: {anomaly_row['anomaly_count'].values[0]}")
        else:
            print(f"  Anomaly Count: 0")

        return pnl_row


    # ════════════════════════════════════════════
    # MODULE 3 METHODS — Surveillance
    # ════════════════════════════════════════════

    def high_risk_clients(self, n=5):
        """
        Returns the top N clients with the most anomaly flags.
        These are the clients the risk desk should look at first.
        """

        top = self.client_anomalies.head(n)

        print(f"\n── Top {n} High Risk Clients ──")
        print(top.to_string(index=False))

        return top


    def get_flagged_trades(self, reason=None):
        """
        Returns all flagged trades.
        Optionally filter by reason type.

        Example:
            analyzer.get_flagged_trades()
            analyzer.get_flagged_trades(reason="HIGH SLIPPAGE")
        """

        if reason:
            filtered = self.flagged[
                self.flagged["anomaly_reason"] == reason
            ]
            print(f"\n── Flagged Trades ({reason}): {len(filtered)} ──")
            return filtered

        print(f"\n── All Flagged Trades: {len(self.flagged)} ──")
        return self.flagged


    # ════════════════════════════════════════════
    # MASTER SUMMARY — Full Platform Overview
    # ════════════════════════════════════════════

    def summarize(self):
        """
        Prints a full platform summary.
        One method call that gives you the whole picture.
        This is what a desk head would want to see
        first thing in the morning.
        """

        print("\n")
        print("=" * 55)
        print("   EQUITY TRADING INTELLIGENCE PLATFORM")
        print("   Morning Summary Report")
        print("=" * 55)

        # -- Execution --
        best_algo = self.algo_perf.iloc[0]
        worst_slip = self.slippage_symbol.iloc[0]

        print("\n📊 EXECUTION ANALYTICS")
        print(f"  Best Algorithm : {best_algo['algo_type']} "
              f"({best_algo['avg_fill_rate']}% fill rate)")
        print(f"  Worst Slippage : {worst_slip['symbol']} "
              f"({worst_slip['avg_slippage_bps']} bps)")

        # -- Clients --
        top_client    = self.client_pnl.iloc[0]
        bottom_client = self.client_pnl.iloc[-1]

        print("\n👥 CLIENT PROFITABILITY")
        print(f"  Top Client    : {top_client['client_id']} "
              f"(${top_client['total_pnl']:,.2f})")
        print(f"  Bottom Client : {bottom_client['client_id']} "
              f"(${bottom_client['total_pnl']:,.2f})")

        # -- Surveillance --
        total_flags   = len(self.flagged)
        riskiest      = self.client_anomalies.iloc[0]

        print("\n🚨 SURVEILLANCE")
        print(f"  Total Flags   : {total_flags}")
        print(f"  Riskiest Client: {riskiest['client_id']} "
              f"({riskiest['anomaly_count']} flags)")

        print("\n" + "=" * 55)