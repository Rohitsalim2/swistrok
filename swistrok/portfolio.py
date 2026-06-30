"""
Portfolio - Manages trading portfolio and positions
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class Portfolio:
    """Manages trading portfolio and open positions"""

    def __init__(self, initial_capital: float):
        """
        Initialize Portfolio

        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
        self.current_balance = initial_capital
        self.positions: List[Dict] = []
        self.closed_trades: List[Dict] = []
        self.total_profit_loss = 0.0
        self.trades_count = 0
        self.winning_trades = 0
        self.losing_trades = 0

    def add_position(self, trade: Dict) -> None:
        """
        Add a new position to portfolio

        Args:
            trade: Trade details
        """
        self.positions.append(trade)
        self.trades_count += 1

        logger.info(
            f"Position opened: {trade['symbol']} - {trade['side']} "
            f"{trade['qty']} @ ${trade['entry_price']:.2f}"
        )

    def close_position(self, symbol: str, exit_price: float) -> Optional[Dict]:
        """
        Close a position

        Args:
            symbol: Symbol to close
            exit_price: Exit price

        Returns:
            Closed trade details
        """
        for i, position in enumerate(self.positions):
            if position["symbol"] == symbol:
                position = self.positions.pop(i)
                trade_result = self._calculate_trade_result(position, exit_price)

                self.closed_trades.append(trade_result)
                self.total_profit_loss += trade_result["profit_loss"]

                if trade_result["profit_loss"] > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1

                logger.info(
                    f"Position closed: {symbol} - "
                    f"P/L: ${trade_result['profit_loss']:.2f} "
                    f"({trade_result['profit_loss_pct']:.2f}%)"
                )

                return trade_result

        logger.warning(f"No position found for {symbol}")
        return None

    def update_position(self, symbol: str, current_price: float) -> None:
        """
        Update position with current market price

        Args:
            symbol: Symbol to update
            current_price: Current market price
        """
        for position in self.positions:
            if position["symbol"] == symbol:
                position["current_price"] = current_price

                # Calculate unrealized P/L
                if position["side"] == "BUY":
                    position["unrealized_pl"] = (
                        (current_price - position["entry_price"]) * position["qty"]
                    )
                else:
                    position["unrealized_pl"] = (
                        (position["entry_price"] - current_price) * position["qty"]
                    )

                position["unrealized_pl_pct"] = (
                    (current_price - position["entry_price"]) / position["entry_price"] * 100
                )

    def _calculate_trade_result(self, position: Dict, exit_price: float) -> Dict:
        """
        Calculate trade profit/loss

        Args:
            position: Position details
            exit_price: Exit price

        Returns:
            Trade result with P/L
        """
        entry_price = position["entry_price"]
        qty = position["qty"]
        side = position["side"]

        # Calculate P/L
        if side == "BUY":
            profit_loss = (exit_price - entry_price) * qty
        else:
            profit_loss = (entry_price - exit_price) * qty

        profit_loss_pct = (profit_loss / (entry_price * qty) * 100) if entry_price != 0 else 0
        duration = (
            datetime.now() - position.get("timestamp", datetime.now())
        ).total_seconds() / 3600

        trade_result = {
            "symbol": position["symbol"],
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "qty": qty,
            "entry_time": position.get("timestamp", datetime.now()),
            "exit_time": datetime.now(),
            "duration_hours": duration,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "stop_loss": position.get("stop_loss"),
            "take_profit": position.get("take_profit"),
        }

        return trade_result

    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        return self.positions.copy()

    def get_closed_trades(self) -> List[Dict]:
        """Get all closed trades"""
        return self.closed_trades.copy()

    def get_stats(self) -> Dict:
        """
        Get portfolio statistics

        Returns:
            Dictionary with portfolio metrics
        """
        total_invested = sum(
            [p["entry_price"] * p["qty"] for p in self.positions]
        )
        total_unrealized_pl = sum(
            [p.get("unrealized_pl", 0) for p in self.positions]
        )

        win_rate = (
            (self.winning_trades / self.trades_count * 100)
            if self.trades_count > 0
            else 0
        )

        avg_win = (
            sum([t["profit_loss"] for t in self.closed_trades if t["profit_loss"] > 0])
            / self.winning_trades
            if self.winning_trades > 0
            else 0
        )

        avg_loss = (
            sum([abs(t["profit_loss"]) for t in self.closed_trades if t["profit_loss"] < 0])
            / self.losing_trades
            if self.losing_trades > 0
            else 0
        )

        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0

        return {
            "initial_capital": self.initial_capital,
            "current_balance": self.current_balance,
            "total_profit_loss": self.total_profit_loss,
            "total_return_pct": (self.total_profit_loss / self.initial_capital * 100),
            "open_positions": len(self.positions),
            "total_invested": total_invested,
            "unrealized_pl": total_unrealized_pl,
            "closed_trades": self.trades_count,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate_pct": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
        }

    def get_performance_dataframe(self) -> pd.DataFrame:
        """Get closed trades as DataFrame for analysis"""
        if not self.closed_trades:
            return pd.DataFrame()

        df = pd.DataFrame(self.closed_trades)
        return df

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio

        Args:
            risk_free_rate: Risk-free rate (annual)

        Returns:
            Sharpe Ratio
        """
        if len(self.closed_trades) < 2:
            return 0.0

        df = self.get_performance_dataframe()
        returns = df["profit_loss_pct"].values / 100

        if returns.std() == 0:
            return 0.0

        # Annualized Sharpe Ratio (assuming daily returns, 252 trading days)
        excess_returns = returns.mean() - (risk_free_rate / 252)
        sharpe = (excess_returns / returns.std()) * (252 ** 0.5)

        return sharpe
