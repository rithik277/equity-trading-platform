# ─────────────────────────────────────────────
# dashboard/app.py
# Phase 4: Plotly Dash Dashboard
# ─────────────────────────────────────────────

import sys
import os

# Allow imports from the root project folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from analyzer.trade_analyzer import TradeAnalyzer

# ── Initialize the analyzer (loads all data) ─
analyzer = TradeAnalyzer()

# ── Initialize the Dash app ───────────────────
app = dash.Dash(__name__)
app.title = "Equity Trading Intelligence Platform"

# ── Color scheme ─────────────────────────────
# Professional dark finance theme
COLORS = {
    "background" : "#0d1117",
    "surface"    : "#161b22",
    "border"     : "#30363d",
    "text"       : "#e6edf3",
    "subtext"    : "#8b949e",
    "green"      : "#2ea043",
    "red"        : "#f85149",
    "blue"       : "#388bfd",
    "yellow"     : "#d29922",
    "purple"     : "#8957e5",
}

# ── Tab style definitions ─────────────────────
TAB_STYLE = {
    "backgroundColor" : COLORS["surface"],
    "color"           : COLORS["subtext"],
    "border"          : f"1px solid {COLORS['border']}",
    "padding"         : "12px 20px",
    "fontWeight"      : "500",
    "fontSize"        : "14px",
}

TAB_SELECTED_STYLE = {
    "backgroundColor" : COLORS["background"],
    "color"           : COLORS["blue"],
    "border"          : f"1px solid {COLORS['blue']}",
    "borderBottom"    : "none",
    "padding"         : "12px 20px",
    "fontWeight"      : "600",
    "fontSize"        : "14px",
}

# ════════════════════════════════════════════════
# LAYOUT — The full page structure
# ════════════════════════════════════════════════

# ── Helper: KPI Card ──────────────────────────
# Add this ABOVE app.layout

def kpi_card(label, value, color):
    """
    Creates one KPI summary box at the top of the page.
    Each card shows a single key metric.
    """
    return html.Div(
        style={
            "flex"            : "1",
            "backgroundColor" : COLORS["surface"],
            "padding"         : "16px 24px",
        },
        children=[
            html.P(
                label,
                style={
                    "margin"   : "0",
                    "fontSize" : "11px",
                    "color"    : COLORS["subtext"],
                    "textTransform" : "uppercase",
                    "letterSpacing" : "0.5px",
                }
            ),
            html.H3(
                value,
                style={
                    "margin"   : "4px 0 0 0",
                    "fontSize" : "22px",
                    "color"    : color,
                    "fontWeight": "700",
                }
            ),
        ]
    )

app.layout = html.Div(
    style={
        "backgroundColor" : COLORS["background"],
        "minHeight"       : "100vh",
        "fontFamily"      : "system-ui, -apple-system, sans-serif",
        "color"           : COLORS["text"],
    },
    children=[

        # ── Header ───────────────────────────
        html.Div(
            style={
                "backgroundColor" : COLORS["surface"],
                "borderBottom"    : f"1px solid {COLORS['border']}",
                "padding"         : "20px 40px",
            },
            children=[
                html.H1(
                    "🏦 Equity Trading Intelligence Platform",
                    style={
                        "margin"   : "0",
                        "fontSize" : "24px",
                        "color"    : COLORS["text"],
                    }
                ),
                html.P(
                    "Execution Analytics · Client Profitability · Surveillance",
                    style={
                        "margin"   : "4px 0 0 0",
                        "color"    : COLORS["subtext"],
                        "fontSize" : "13px",
                    }
                ),
            ]
        ),

        # ── KPI Summary Bar ───────────────────
        html.Div(
            style={
                "display"         : "flex",
                "gap"             : "1px",
                "backgroundColor" : COLORS["border"],
                "borderBottom"    : f"1px solid {COLORS['border']}",
            },
            children=[
                kpi_card("Total Trades",
                    f"{analyzer.client_pnl['total_trades'].sum():,}",
                    COLORS["blue"]),
                kpi_card("Total Clients",
                    f"{len(analyzer.client_pnl)}",
                    COLORS["purple"]),
                kpi_card("Flagged Trades",
                    f"{len(analyzer.flagged):,}",
                    COLORS["red"]),
                kpi_card("Best Algo",
                    f"{analyzer.algo_perf.iloc[0]['algo_type']}",
                    COLORS["green"]),
                kpi_card("Avg Slippage",
                    f"{analyzer.algo_perf['avg_slippage_bps'].mean():.1f} bps",
                    COLORS["yellow"]),
            ]
        ),

        # ── Tabs ─────────────────────────────
        html.Div(
            style={"padding" : "0 40px"},
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="execution",
                    style={"marginTop" : "20px"},
                    children=[
                        dcc.Tab(
                            label="📊 Execution Analytics",
                            value="execution",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="👥 Client Profitability",
                            value="clients",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="🚨 Surveillance & Alerts",
                            value="surveillance",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                    ]
                ),
                # Tab content renders here
                html.Div(id="tab-content", style={"paddingTop": "24px"})
            ]
        )
    ]
)

# ════════════════════════════════════════════════
# TAB CONTENT LAYOUTS
# ════════════════════════════════════════════════

def execution_tab():
    """Module 1 — Execution Analytics layout"""

    # ── Chart 1: Algo Performance Bar Chart ──
    fig_algo = px.bar(
        analyzer.algo_perf,
        x="algo_type",
        y="avg_fill_rate",
        color="avg_slippage_bps",
        color_continuous_scale="RdYlGn_r",
        labels={
            "algo_type"       : "Algorithm",
            "avg_fill_rate"   : "Avg Fill Rate (%)",
            "avg_slippage_bps": "Avg Slippage (bps)"
        },
        title="Algorithm Performance — Fill Rate vs Slippage",
    )
    fig_algo.update_layout(
        plot_bgcolor  = COLORS["surface"],
        paper_bgcolor = COLORS["surface"],
        font_color    = COLORS["text"],
        title_font_size = 14,
    )

    # ── Chart 2: Slippage by Symbol ──
    fig_slip = px.bar(
        analyzer.slippage_symbol.head(10),
        x="symbol",
        y="avg_slippage_bps",
        color="avg_slippage_bps",
        color_continuous_scale="Reds",
        labels={
            "symbol"          : "Stock",
            "avg_slippage_bps": "Avg Slippage (bps)"
        },
        title="Top 10 Stocks by Slippage Cost",
    )
    fig_slip.update_layout(
        plot_bgcolor  = COLORS["surface"],
        paper_bgcolor = COLORS["surface"],
        font_color    = COLORS["text"],
        title_font_size = 14,
    )

    # ── Chart 3: Daily Slippage Trend ──
    fig_trend = px.line(
        analyzer.daily_slippage,
        x="date",
        y="avg_slippage_bps",
        labels={
            "date"            : "Date",
            "avg_slippage_bps": "Avg Slippage (bps)"
        },
        title="Daily Slippage Trend — Full Year",
    )
    fig_trend.update_traces(line_color=COLORS["blue"])
    fig_trend.update_layout(
        plot_bgcolor  = COLORS["surface"],
        paper_bgcolor = COLORS["surface"],
        font_color    = COLORS["text"],
        title_font_size = 14,
    )

    return html.Div([
        # Top two charts side by side
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(dcc.Graph(figure=fig_algo),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
                html.Div(dcc.Graph(figure=fig_slip),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
            ]
        ),
        # Full width trend line
        html.Div(
            dcc.Graph(figure=fig_trend),
            style={"backgroundColor": COLORS["surface"],
                   "borderRadius": "8px", "padding": "8px"}
        ),
    ])


def clients_tab():
    """Module 2 — Client Profitability layout"""

    # ── Chart 1: Client P&L Bar Chart ──
    fig_pnl = px.bar(
        analyzer.client_pnl,
        x="client_id",
        y="total_pnl",
        color="total_pnl",
        color_continuous_scale="RdYlGn",
        labels={
            "client_id" : "Client",
            "total_pnl" : "Total P&L ($)"
        },
        title="Client P&L Ranking — All Clients",
    )
    fig_pnl.update_layout(
        plot_bgcolor  = COLORS["surface"],
        paper_bgcolor = COLORS["surface"],
        font_color    = COLORS["text"],
        title_font_size = 14,
        xaxis_tickangle = -45,
    )

    # ── Chart 2: Client Algo Preference ──
    fig_algo_pref = px.bar(
        analyzer.client_algo_pref,
        x="client_id",
        y="trade_count",
        color="algo_type",
        labels={
            "client_id"   : "Client",
            "trade_count" : "Number of Trades",
            "algo_type"   : "Algorithm"
        },
        title="Algorithm Preference by Client",
        barmode="stack",
    )
    fig_algo_pref.update_layout(
        plot_bgcolor  = COLORS["surface"],
        paper_bgcolor = COLORS["surface"],
        font_color    = COLORS["text"],
        title_font_size = 14,
        xaxis_tickangle = -45,
    )

    # ── Table: Full Client Profitability Table ──
    table = dash_table.DataTable(
        data=analyzer.client_pnl.to_dict("records"),
        columns=[
            {"name": "Client ID",        "id": "client_id"},
            {"name": "Total P&L ($)",    "id": "total_pnl"},
            {"name": "Total Trades",     "id": "total_trades"},
            {"name": "Avg Slippage bps", "id": "avg_slippage_bps"},
            {"name": "Avg Fill Rate %",  "id": "avg_fill_rate"},
        ],
        style_table={"overflowX": "auto"},
        style_cell={
            "backgroundColor" : COLORS["surface"],
            "color"           : COLORS["text"],
            "border"          : f"1px solid {COLORS['border']}",
            "padding"         : "10px 14px",
            "fontSize"        : "13px",
            "textAlign"       : "left",
        },
        style_header={
            "backgroundColor" : COLORS["background"],
            "color"           : COLORS["blue"],
            "fontWeight"      : "600",
            "border"          : f"1px solid {COLORS['border']}",
        },
        style_data_conditional=[
            {
                "if"    : {"filter_query": "{total_pnl} > 0"},
                "color" : COLORS["green"],
            },
            {
                "if"    : {"filter_query": "{total_pnl} < 0"},
                "color" : COLORS["red"],
            },
        ],
        sort_action="native",
        page_size=10,
    )

    return html.Div([
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(dcc.Graph(figure=fig_pnl),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
                html.Div(dcc.Graph(figure=fig_algo_pref),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
            ]
        ),
        html.Div(
            style={"backgroundColor": COLORS["surface"],
                   "borderRadius": "8px", "padding": "16px"},
            children=[
                html.H3("Full Client Profitability Table",
                        style={"color": COLORS["text"],
                               "fontSize": "14px", "marginTop": "0"}),
                table
            ]
        )
    ])


def surveillance_tab():
    """Module 3 — Surveillance & Alerts layout"""

    # ── Chart 1: Anomaly Type Breakdown ──
    fig_anomaly = px.bar(
        analyzer.anomaly_summary,
        x="anomaly_reason",
        y="count",
        color="anomaly_reason",
        labels={
            "anomaly_reason" : "Anomaly Type",
            "count"          : "Number of Flags"
        },
        title="Anomaly Breakdown by Type",
    )
    fig_anomaly.update_layout(
        plot_bgcolor    = COLORS["surface"],
        paper_bgcolor   = COLORS["surface"],
        font_color      = COLORS["text"],
        title_font_size = 14,
        showlegend      = False,
    )

    # ── Chart 2: Riskiest Clients ──
    fig_risk = px.bar(
        analyzer.client_anomalies.head(10),
        x="client_id",
        y="anomaly_count",
        color="anomaly_count",
        color_continuous_scale="Reds",
        labels={
            "client_id"     : "Client",
            "anomaly_count" : "Anomaly Count"
        },
        title="Top 10 Riskiest Clients by Anomaly Count",
    )
    fig_risk.update_layout(
        plot_bgcolor    = COLORS["surface"],
        paper_bgcolor   = COLORS["surface"],
        font_color      = COLORS["text"],
        title_font_size = 14,
    )

    # ── Table: Flagged Trades ──
    flagged_table = dash_table.DataTable(
        data=analyzer.flagged.head(100).to_dict("records"),
        columns=[
            {"name": "Trade ID",      "id": "trade_id"},
            {"name": "Date",          "id": "date"},
            {"name": "Symbol",        "id": "symbol"},
            {"name": "Client",        "id": "client_id"},
            {"name": "Algo",          "id": "algo_type"},
            {"name": "Side",          "id": "side"},
            {"name": "Order Qty",     "id": "order_qty"},
            {"name": "Slippage bps",  "id": "slippage_bps"},
            {"name": "P&L ($)",       "id": "pnl"},
            {"name": "Alert Reason",  "id": "anomaly_reason"},
        ],
        style_table={"overflowX": "auto"},
        style_cell={
            "backgroundColor" : COLORS["surface"],
            "color"           : COLORS["text"],
            "border"          : f"1px solid {COLORS['border']}",
            "padding"         : "10px 14px",
            "fontSize"        : "12px",
            "textAlign"       : "left",
        },
        style_header={
            "backgroundColor" : COLORS["background"],
            "color"           : COLORS["red"],
            "fontWeight"      : "600",
            "border"          : f"1px solid {COLORS['border']}",
        },
        style_data_conditional=[
            {
                "if": {
                    "filter_query": '{anomaly_reason} = "HIGH SLIPPAGE + LARGE ORDER"'
                },
                "backgroundColor": "#2d1515",
            },
            {
                "if": {
                    "filter_query": '{anomaly_reason} = "HIGH SLIPPAGE"'
                },
                "backgroundColor": "#1f1a10",
            },
        ],
        sort_action="native",
        filter_action="native",
        page_size=15,
    )

    return html.Div([
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "16px"},
            children=[
                html.Div(dcc.Graph(figure=fig_anomaly),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
                html.Div(dcc.Graph(figure=fig_risk),
                         style={"flex": "1", "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px", "padding": "8px"}),
            ]
        ),
        html.Div(
            style={"backgroundColor": COLORS["surface"],
                   "borderRadius": "8px", "padding": "16px"},
            children=[
                html.H3("🚨 Flagged Trades — Top 100 by Slippage",
                        style={"color": COLORS["red"],
                               "fontSize": "14px", "marginTop": "0"}),
                html.P("Use the filter row to search by client, symbol or alert type.",
                       style={"color": COLORS["subtext"], "fontSize": "12px",
                              "marginTop": "0"}),
                flagged_table
            ]
        )
    ])


# ════════════════════════════════════════════════
# CALLBACK — Switches tab content when tab clicked
# ════════════════════════════════════════════════

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab(tab):
    """
    This function runs automatically every time
    the user clicks a different tab.

    Dash callbacks work like this:
      Input  = something the user does (clicks a tab)
      Output = something that updates on the page
    """
    if tab == "execution":
        return execution_tab()
    elif tab == "clients":
        return clients_tab()
    elif tab == "surveillance":
        return surveillance_tab()

if __name__ == '__main__':  
    app.run(debug=True)  