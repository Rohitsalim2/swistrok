"""
Trading Strategies - Collection of trading strategy implementations
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import ta  # Technical Analysis

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""

    def __init__(self, name: str, symbols: List[str], timeframe: str = "1h"):
        """
        Initialize base strategy

        Args:
            name: Strategy name
            symbols: List of trading symbols
            timeframe: Candle timeframe
        """
        self.name = name
        self.symbols = symbols
        self.timeframe = timeframe
        self.data: Dict[str, pd.DataFrame] = {}

    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """Generate trading signals"""
        pass

    def evaluate(self) -> List[Dict]:
        """
        Evaluate strategy and return signals

        Returns:
            List of trading signals
        """
        all_signals = []

        for symbol in self.symbols:
            try:
                # Calculate indicators
                df = self.calculate_indicators(self.data.get(symbol, pd.DataFrame()))

                # Generate signals
                signals = self.generate_signals(df)
                all_signals.extend(signals)

            except Exception as e:
                logger.error(f"Error evaluating {self.name} for {symbol}: {str(e)}")

        return all_signals

    def set_data(self, symbol: str, df: pd.DataFrame) -> None:
        """Set market data for a symbol"""
        self.data[symbol] = df


class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    BUY: Fast MA crosses above Slow MA
    SELL: Fast MA crosses below Slow MA
    """

    def __init__(
        self,
        symbols: List[str],
        fast_period: int = 20,
        slow_period: int = 50,
        timeframe: str = "1h",
    ):
        super().__init__("MovingAverageCrossover", symbols, timeframe)
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages"""
        if df.empty:
            return df

        df = df.copy()
        df["fast_ma"] = ta.trend.sma_indicator(df["close"], window=self.fast_period)
        df["slow_ma"] = ta.trend.sma_indicator(df["close"], window=self.slow_period)

        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """Generate crossover signals"""
        signals = []

        if df.empty or len(df) < 2:
            return signals

        # Get last two rows for crossover detection
        prev_fast = df["fast_ma"].iloc[-2]
        curr_fast = df["fast_ma"].iloc[-1]
        prev_slow = df["slow_ma"].iloc[-2]
        curr_slow = df["slow_ma"].iloc[-1]
        current_price = df["close"].iloc[-1]

        # BUY Signal: Fast MA crosses above Slow MA
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "BUY",
                    "entry_price": current_price,
                    "stop_loss": current_price * 0.98,  # 2% below entry
                    "take_profit": current_price * 1.05,  # 5% above entry
                    "confidence": 0.7,
                    "reason": f"Fast MA ({curr_fast:.2f}) crossed above Slow MA ({curr_slow:.2f})",
                }
            )

        # SELL Signal: Fast MA crosses below Slow MA
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "SELL",
                    "entry_price": current_price,
                    "stop_loss": current_price * 1.02,  # 2% above entry
                    "take_profit": current_price * 0.95,  # 5% below entry
                    "confidence": 0.7,
                    "reason": f"Fast MA ({curr_fast:.2f}) crossed below Slow MA ({curr_slow:.2f})",
                }
            )

        return signals


class RSIStrategy(BaseStrategy):
    """
    RSI Overbought/Oversold Strategy
    BUY: RSI < 30 (oversold)
    SELL: RSI > 70 (overbought)
    """

    def __init__(
        self,
        symbols: List[str],
        period: int = 14,
        oversold: int = 30,
        overbought: int = 70,
        timeframe: str = "1h",
    ):
        super().__init__("RSIStrategy", symbols, timeframe)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator"""
        if df.empty:
            return df

        df = df.copy()
        df["rsi"] = ta.momentum.rsi(df["close"], window=self.period)

        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """Generate RSI signals"""
        signals = []

        if df.empty or len(df) < 1:
            return signals

        current_rsi = df["rsi"].iloc[-1]
        current_price = df["close"].iloc[-1]

        # BUY Signal: RSI < 30 (oversold)
        if current_rsi < self.oversold:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "BUY",
                    "entry_price": current_price,
                    "stop_loss": current_price * 0.97,
                    "take_profit": current_price * 1.04,
                    "confidence": 0.6 + (1 - current_rsi / 30) * 0.2,
                    "reason": f"RSI ({current_rsi:.2f}) indicates oversold condition",
                }
            )

        # SELL Signal: RSI > 70 (overbought)
        elif current_rsi > self.overbought:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "SELL",
                    "entry_price": current_price,
                    "stop_loss": current_price * 1.03,
                    "take_profit": current_price * 0.96,
                    "confidence": 0.6 + ((current_rsi - 70) / 30) * 0.2,
                    "reason": f"RSI ({current_rsi:.2f}) indicates overbought condition",
                }
            )

        return signals


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy
    BUY: Price touches lower band
    SELL: Price touches upper band
    """

    def __init__(
        self,
        symbols: List[str],
        period: int = 20,
        std_dev: int = 2,
        timeframe: str = "1h",
    ):
        super().__init__("BollingerBandsStrategy", symbols, timeframe)
        self.period = period
        self.std_dev = std_dev

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        if df.empty:
            return df

        df = df.copy()
        bollinger = ta.volatility.BollingerBands(
            df["close"], window=self.period, window_dev=self.std_dev
        )
        df["bb_upper"] = bollinger.bollinger_hband()
        df["bb_middle"] = bollinger.bollinger_mavg()
        df["bb_lower"] = bollinger.bollinger_lband()

        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """Generate Bollinger Bands signals"""
        signals = []

        if df.empty or len(df) < 1:
            return signals

        current_price = df["close"].iloc[-1]
        upper_band = df["bb_upper"].iloc[-1]
        lower_band = df["bb_lower"].iloc[-1]
        middle_band = df["bb_middle"].iloc[-1]

        # BUY Signal: Price touches lower band
        if current_price <= lower_band:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "BUY",
                    "entry_price": current_price,
                    "stop_loss": lower_band * 0.99,
                    "take_profit": middle_band * 1.02,
                    "confidence": 0.65,
                    "reason": f"Price touched lower Bollinger Band",
                }
            )

        # SELL Signal: Price touches upper band
        elif current_price >= upper_band:
            signals.append(
                {
                    "symbol": df.get("symbol", "UNKNOWN"),
                    "side": "SELL",
                    "entry_price": current_price,
                    "stop_loss": upper_band * 1.01,
                    "take_profit": middle_band * 0.98,
                    "confidence": 0.65,
                    "reason": f"Price touched upper Bollinger Band",
                }
            )

        return signals
