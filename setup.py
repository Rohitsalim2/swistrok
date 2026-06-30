from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="swistrok",
    version="0.1.0",
    author="Rohitsalim2",
    description="Automated skill trading platform with advanced risk management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rohitsalim2/swistrok",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "requests>=2.26.0",
        "python-dotenv>=0.19.0",
        "pydantic>=1.8.0",
        "sqlalchemy>=1.4.0",
        "ta>=0.10.2",  # Technical Analysis
        "ccxt>=1.76.0",  # Cryptocurrency Exchange Trading
        "pytest>=6.2.0",
    ],
    extras_require={
        "dev": [
            "black>=21.9b0",
            "flake8>=3.9.0",
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "pre-commit>=2.14.0",
            "sphinx>=4.1.0",
        ],
        "broker": [
            "alpaca-trade-api>=1.6.0",
            "yfinance>=0.1.70",
        ],
    },
    entry_points={
        "console_scripts": [
            "swistrok=swistrok.cli:main",
        ],
    },
)
