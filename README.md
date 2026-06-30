# Swistrok - Automated Skill Trading Platform

**Swistrok** adalah platform trading otomatis yang dirancang untuk mengeksekusi strategi trading dengan manajemen risiko yang ketat dan analisis real-time.

## 🚀 Features

- ✅ Multi-strategy trading engine
- ✅ Real-time market data handling
- ✅ Advanced risk management
- ✅ Portfolio optimization
- ✅ Backtesting support
- ✅ Performance analytics
- ✅ REST API integration

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Rohitsalim2/swistrok.git
cd swistrok

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.local.example .env.local
```

## 📝 Configuration

Edit `.env.local` dengan credentials API broker:

```env
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret
BROKER_BASE_URL=https://api.broker.com
DATABASE_URL=sqlite:///./trading.db
LOG_LEVEL=INFO
```

## 🎯 Quick Start

```python
from swistrok.trading_engine import TradingEngine
from swistrok.strategies import MovingAverageCrossover

# Inisialisasi engine
engine = TradingEngine(broker_api_key="xxx", broker_api_secret="xxx")

# Setup strategi
strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
engine.add_strategy(strategy)

# Jalankan trading
engine.start()
```

## 📂 Project Structure

```
swistrok/
├── swistrok/
│   ├── __init__.py
│   ├── trading_engine.py       # Core trading logic
│   ├── strategies.py           # Trading strategies
│   ├── data_handler.py         # Market data handling
│   ├── risk_manager.py         # Risk management
│   ├── portfolio.py            # Portfolio management
│   ├── brokers/
│   │   ├── __init__.py
│   │   └── broker_base.py      # Base broker interface
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration loader
│   │   └── logger.py           # Logging setup
│   └── models/
│       ├── __init__.py
│       ├── trade.py            # Trade data model
│       └── order.py            # Order data model
├── tests/
│   ├── __init__.py
│   ├── test_strategies.py
│   ├── test_risk_manager.py
│   └── test_integration.py
├── examples/
│   ├── basic_trading.py
│   └── backtest_example.py
├── setup.py
├── .env.local.example
├── requirements.txt
└── README.md
```

## 🔧 Development

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=swistrok tests/

# Format code
black swistrok/

# Lint
flake8 swistrok/
```

## 📊 Supported Strategies

- Moving Average Crossover
- RSI Overbought/Oversold
- MACD Signal
- Bollinger Bands
- Custom Strategy Builder

## ⚠️ Risk Management

- Position sizing berbasis Kelly Criterion
- Stop-loss dan take-profit otomatis
- Daily drawdown limits
- Correlation-based portfolio balancing
- Maximum leverage constraints

## 📈 Performance Metrics

- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor

## 🤝 Contributing

Contributions welcome! Silakan buat pull request dengan:
1. Feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push ke branch (`git push origin feature/AmazingFeature`)
4. Open Pull Request

## 📄 License

MIT License - lihat `LICENSE` file untuk details

## 📞 Support

Untuk issues, silakan buat GitHub Issue atau hubungi developer.

---

**⚠️ DISCLAIMER**: Aplikasi ini untuk educational purposes. Trading otomatis memiliki risiko finansial yang signifikan. Gunakan dengan hati-hati dan hanya dengan capital yang bisa Anda rugikan.
