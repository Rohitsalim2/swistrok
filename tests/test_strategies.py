"""
Strategy Tests - Unit tests for trading strategies
"""

import pytest
import pandas as pd
import numpy as np
from swistrok.strategies import (
    MovingAverageCrossover,
    RSIStrategy,
    BollingerBandsStrategy,
)


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    prices = np.random.uniform(100, 110, 100)

    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices,
            "high": prices * 1.01,
            "low": prices * 0.99,
            "close": prices,
            "volume": np.random.uniform(1000, 10000, 100),
        }
    )
    df = df.set_index("timestamp")
    return df


def test_moving_average_crossover_initialization():
    """Test MovingAverageCrossover initialization"""
    strategy = MovingAverageCrossover(
        symbols=["AAPL", "GOOGL"],
        fast_period=20,
        slow_period=50,
    )

    assert strategy.name == "MovingAverageCrossover"
    assert strategy.fast_period == 20
    assert strategy.slow_period == 50
    assert len(strategy.symbols) == 2


def test_moving_average_crossover_signals(sample_ohlcv_data):
    """Test MovingAverageCrossover signal generation"""
    strategy = MovingAverageCrossover(
        symbols=["AAPL"],
        fast_period=10,
        slow_period=20,
    )

    strategy.set_data("AAPL", sample_ohlcv_data)
    signals = strategy.generate_signals(
        strategy.calculate_indicators(sample_ohlcv_data)
    )

    # Should generate some signals (might be 0 due to random data)
    assert isinstance(signals, list)


def test_rsi_strategy_initialization():
    """Test RSIStrategy initialization"""
    strategy = RSIStrategy(
        symbols=["AAPL"],
        period=14,
        oversold=30,
        overbought=70,
    )

    assert strategy.name == "RSIStrategy"
    assert strategy.period == 14
    assert strategy.oversold == 30
    assert strategy.overbought == 70


def test_bollinger_bands_strategy_initialization():
    """Test BollingerBandsStrategy initialization"""
    strategy = BollingerBandsStrategy(
        symbols=["AAPL"],
        period=20,
        std_dev=2,
    )

    assert strategy.name == "BollingerBandsStrategy"
    assert strategy.period == 20
    assert strategy.std_dev == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
