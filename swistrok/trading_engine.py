"""
Core Trading Engine - Main orchestrator for trading operations
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from .strategies import BaseStrategy
from .data_handler import DataHandler
from .risk_manager import RiskManager
from .portfolio import Portfolio
from .utils.config import Config

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine that orchestrates all trading operations"""

    def __init__(
        self,
        broker_api_key: str,
        broker_api_secret: str,
        initial_capital: float = 10000,
        paper_trading: bool = True,
        config_path: Optional[str] = None,
    ):
        """
        Initialize Trading Engine

        Args:
            broker_api_key: API key for broker
            broker_api_secret: API secret for broker
            initial_capital: Starting capital
            paper_trading: Use paper trading (simulation)
            config_path: Path to config file
        """
        self.config = Config(config_path)
        self.broker_api_key = broker_api_key
        self.broker_api_secret = broker_api_secret
        self.initial_capital = initial_capital
        self.paper_trading = paper_trading

        # Initialize components
        self.data_handler = DataHandler(broker_api_key, broker_api_secret)
        self.portfolio = Portfolio(initial_capital)
        self.risk_manager = RiskManager(self.config)
        self.strategies: List[BaseStrategy] = []
        self.is_running = False

        logger.info(
            f"Trading Engine initialized - Capital: ${initial_capital}, "
            f"Paper Trading: {paper_trading}"
        )

    def add_strategy(self, strategy: BaseStrategy) -> None:
        """Add a trading strategy to the engine"""
        self.strategies.append(strategy)
        logger.info(f"Strategy added: {strategy.name}")

    def remove_strategy(self, strategy_name: str) -> None:
        """Remove a strategy by name"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        logger.info(f"Strategy removed: {strategy_name}")

    def get_market_data(self, symbol: str, timeframe: str = "1h") -> pd.DataFrame:
        """
        Fetch market data for a symbol

        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC/USD')
            timeframe: Time frame (1m, 5m, 15m, 1h, 4h, 1d)

        Returns:
            DataFrame with OHLCV data
        """
        data = self.data_handler.fetch_ohlcv(symbol, timeframe)
        logger.debug(f"Fetched {len(data)} candles for {symbol}")
        return data

    def evaluate_signals(self) -> Dict[str, List[Dict]]:
        """
        Evaluate all strategies and collect trading signals

        Returns:
            Dictionary with signals from each strategy
        """
        signals = {}

        for strategy in self.strategies:
            try:
                strategy_signals = strategy.evaluate()
                signals[strategy.name] = strategy_signals
                logger.info(
                    f"{strategy.name} generated {len(strategy_signals)} signals"
                )
            except Exception as e:
                logger.error(f"Error evaluating {strategy.name}: {str(e)}")

        return signals

    def execute_signals(self, signals: Dict[str, List[Dict]]) -> None:
        """
        Execute trading signals with risk management

        Args:
            signals: Dictionary of signals from strategies
        """
        for strategy_name, strategy_signals in signals.items():
            for signal in strategy_signals:
                try:
                    # Risk checks
                    if not self.risk_manager.can_trade(signal):
                        logger.warning(
                            f"Signal rejected by risk manager: {signal['symbol']}"
                        )
                        continue

                    # Execute trade
                    trade = self._execute_trade(signal)
                    if trade:
                        self.portfolio.add_position(trade)
                        logger.info(f"Trade executed: {trade}")

                except Exception as e:
                    logger.error(f"Error executing signal: {str(e)}")

    def _execute_trade(self, signal: Dict) -> Optional[Dict]:
        """
        Execute a single trade

        Args:
            signal: Trading signal with details

        Returns:
            Trade details if successful
        """
        symbol = signal["symbol"]
        side = signal["side"]  # 'BUY' or 'SELL'
        entry_price = signal.get("entry_price", self.data_handler.get_current_price(symbol))

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss=signal.get("stop_loss"),
        )

        if position_size <= 0:
            logger.warning(f"Invalid position size for {symbol}")
            return None

        # Place order
        order = self.data_handler.place_order(
            symbol=symbol,
            side=side,
            qty=position_size,
            entry_price=entry_price,
        )

        if order:
            trade = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "qty": position_size,
                "stop_loss": signal.get("stop_loss"),
                "take_profit": signal.get("take_profit"),
                "timestamp": datetime.now(),
                "order_id": order.get("id"),
            }
            return trade

        return None

    def update_positions(self) -> None:
        """Update all open positions with latest market prices"""
        for position in self.portfolio.positions:
            current_price = self.data_handler.get_current_price(position["symbol"])
            self.portfolio.update_position(position["symbol"], current_price)

    def check_stop_losses(self) -> None:
        """Check and execute stop loss orders"""
        for position in self.portfolio.positions:
            current_price = self.data_handler.get_current_price(position["symbol"])

            if position.get("stop_loss"):
                if position["side"] == "BUY" and current_price <= position["stop_loss"]:
                    self._close_position(position, current_price, reason="stop_loss")
                elif (
                    position["side"] == "SELL"
                    and current_price >= position["stop_loss"]
                ):
                    self._close_position(position, current_price, reason="stop_loss")

    def check_take_profits(self) -> None:
        """Check and execute take profit orders"""
        for position in self.portfolio.positions:
            current_price = self.data_handler.get_current_price(position["symbol"])

            if position.get("take_profit"):
                if (
                    position["side"] == "BUY"
                    and current_price >= position["take_profit"]
                ):
                    self._close_position(position, current_price, reason="take_profit")
                elif (
                    position["side"] == "SELL"
                    and current_price <= position["take_profit"]
                ):
                    self._close_position(position, current_price, reason="take_profit")

    def _close_position(self, position: Dict, exit_price: float, reason: str) -> None:
        """Close a position"""
        logger.info(
            f"Closing {position['symbol']} - Reason: {reason}, "
            f"Exit Price: ${exit_price}"
        )
        self.portfolio.close_position(position["symbol"], exit_price)

    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""
        return self.portfolio.get_stats()

    def start(self) -> None:
        """Start the trading engine"""
        self.is_running = True
        logger.info("Trading Engine started")

        try:
            while self.is_running:
                # Get signals from all strategies
                signals = self.evaluate_signals()

                # Execute signals with risk management
                self.execute_signals(signals)

                # Update positions
                self.update_positions()

                # Check stop losses and take profits
                self.check_stop_losses()
                self.check_take_profits()

                # Log portfolio stats
                stats = self.get_portfolio_stats()
                logger.info(f"Portfolio: {stats}")

        except KeyboardInterrupt:
            logger.info("Trading engine stopped by user")
            self.stop()

    def stop(self) -> None:
        """Stop the trading engine"""
        self.is_running = False
        logger.info("Trading Engine stopped")
