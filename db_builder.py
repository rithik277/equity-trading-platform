# ─────────────────────────────────────────────
# db_builder.py
# Phase 2: Load our data into a SQLite database
# ─────────────────────────────────────────────

import sqlite3
import pandas as pd

# ── STEP 2A: Connect to (or create) the database ──

def create_database():
    """
    Creates a SQLite database file and loads our
    trades and prices data into it as proper SQL tables.

    SQLite is a lightweight database that lives as a
    single file on your computer — no server needed.
    Perfect for a project like this.
    """

    print("Step 2A — Creating database...")

    # This creates the file if it doesn't exist
    # If it already exists, it just connects to it
    conn = sqlite3.connect("database/trading.db")

    print("  Connected to database/trading.db")

    return conn


# ── STEP 2B: Load CSVs into SQL tables ───────

def load_tables(conn):
    """
    Reads our CSV files and writes them into the
    database as proper SQL tables.

    Think of each table like a spreadsheet tab
    inside the database file.
    """

    print("\nStep 2B — Loading data into tables...")

    # -- Load trades --
    trades = pd.read_csv("data/trades.csv")

    # Write to SQL table called 'trades'
    # if_exists='replace' means: if table already exists, overwrite it
    trades.to_sql("trades", conn, if_exists="replace", index=False)

    print(f"  trades table loaded — {len(trades)} rows")

    # -- Load prices --
    prices = pd.read_csv("data/prices.csv")

    prices.to_sql("prices", conn, if_exists="replace", index=False)

    print(f"  prices table loaded — {len(prices)} rows")


# ── STEP 2C: Verify the tables exist ─────────

def verify_tables(conn):
    """
    Runs a quick check to confirm both tables
    were created correctly inside the database.
    """

    print("\nStep 2C — Verifying tables...")

    cursor = conn.cursor()

    # This SQL query lists all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    tables = cursor.fetchall()

    print(f"  Tables found: {[t[0] for t in tables]}")

    # Preview first 2 rows of trades table
    cursor.execute("SELECT * FROM trades LIMIT 2")
    rows = cursor.fetchall()

    print("\n  Preview of trades table:")
    for row in rows:
        print(f"    {row}")


# ── Run everything ────────────────────────────

conn = create_database()
load_tables(conn)
verify_tables(conn)

# Always close the connection when done
conn.close()

print("\n  Database ready. Phase 2A complete!")