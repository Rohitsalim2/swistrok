"""
Configuration - Load and manage application configuration
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration loader from environment variables"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to .env file
        """
        if config_path:
            load_dotenv(config_path)
        else:
            load_dotenv(".env.local")

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment"""
        return {
            "BROKER_TYPE": os.getenv("BROKER_TYPE", "alpaca"),
            "BROKER_API_KEY": os.getenv("BROKER_API_KEY", ""),
            "BROKER_API_SECRET": os.getenv("BROKER_API_SECRET", ""),
            "BROKER_BASE_URL": os.getenv("BROKER_BASE_URL", "https://api.alpaca.markets"),
            "BROKER_PAPER_TRADING": os.getenv("BROKER_PAPER_TRADING", "true").lower() == "true",
            "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./trading.db"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_FILE": os.getenv("LOG_FILE", "logs/swistrok.log"),
            "DEFAULT_SYMBOL": os.getenv("DEFAULT_SYMBOL", "AAPL"),
            "INITIAL_CAPITAL": float(os.getenv("INITIAL_CAPITAL", "10000")),
            "MAX_POSITION_SIZE": float(os.getenv("MAX_POSITION_SIZE", "0.05")),
            "MAX_DAILY_LOSS": float(os.getenv("MAX_DAILY_LOSS", "0.02")),
            "MAX_LEVERAGE": float(os.getenv("MAX_LEVERAGE", "1.0")),
            "STOP_LOSS_PERCENT": float(os.getenv("STOP_LOSS_PERCENT", "2.0")),
            "TAKE_PROFIT_PERCENT": float(os.getenv("TAKE_PROFIT_PERCENT", "5.0")),
            "POSITION_SIZING": os.getenv("POSITION_SIZING", "kelly"),
            "ENABLE_BACKTESTING": os.getenv("ENABLE_BACKTESTING", "true").lower() == "true",
            "ENABLE_PAPER_TRADING": os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true",
            "ENABLE_LIVE_TRADING": os.getenv("ENABLE_LIVE_TRADING", "false").lower() == "true",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
