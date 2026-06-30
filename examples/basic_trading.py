"""
Basic Trading Example
Demonstrates how to use Swistrok for simple trading
"""

from swistrok.trading_engine import TradingEngine
from swistrok.strategies import MovingAverageCrossover, RSIStrategy
from swistrok.utils.config import Config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main trading example"""

    # Load configuration
    config = Config(".env.local")

    # Initialize trading engine with paper trading (simulation)
    engine = TradingEngine(
        broker_api_key=config.get("BROKER_API_KEY"),
        broker_api_secret=config.get("BROKER_API_SECRET"),
        initial_capital=config.get("INITIAL_CAPITAL", 10000),
        paper_trading=True,
    )

    # Create strategies
    symbols = ["AAPL", "GOOGL", "MSFT"]

    # Moving Average Crossover Strategy
    ma_strategy = MovingAverageCrossover(
        symbols=symbols,
        fast_period=20,
        slow_period=50,
        timeframe="1h",
    )
    engine.add_strategy(ma_strategy)

    # RSI Strategy
    rsi_strategy = RSIStrategy(
        symbols=symbols,
        period=14,
        oversold=30,
        overbought=70,
        timeframe="1h",
    )
    engine.add_strategy(rsi_strategy)

    # Get sample market data
    logger.info("Fetching market data...")
    for symbol in symbols:
        data = engine.get_market_data(symbol, "1h")
        ma_strategy.set_data(symbol, data)
        rsi_strategy.set_data(symbol, data)

    # Evaluate signals
    logger.info("Evaluating trading signals...")
    signals = engine.evaluate_signals()

    # Display signals
    for strategy_name, strategy_signals in signals.items():
        logger.info(f"\n{strategy_name} Signals:")
        for signal in strategy_signals:
            logger.info(
                f"  Symbol: {signal['symbol']}, "
                f"Side: {signal['side']}, "
                f"Price: ${signal['entry_price']:.2f}, "
                f"Confidence: {signal['confidence']:.2%}"
            )

    # Get portfolio statistics
    stats = engine.get_portfolio_stats()
    logger.info("\nPortfolio Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main()
