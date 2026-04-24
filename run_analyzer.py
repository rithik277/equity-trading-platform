from analyzer.trade_analyzer import TradeAnalyzer

analyzer = TradeAnalyzer()
analyzer.summarize()
analyzer.best_performing_algo()
analyzer.top_clients(n=5)
analyzer.high_risk_clients(n=5)
analyzer.client_profile("CLIENT_001")
analyzer.get_flagged_trades(reason="HIGH SLIPPAGE")