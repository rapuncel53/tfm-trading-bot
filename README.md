# Trading Bot with NLP and Time Series Analysis

## Overview

This project is a trading bot that combines Natural Language Processing (NLP) with time series analysis to make automated trading decisions.

### What it does

1. **NLP Module** — Processes financial news, social media, and text data to extract sentiment and market-moving signals.
2. **Time Series Module** — Analyzes historical price data and technical indicators to forecast short-term price movements.
3. **Trading Engine** — Combines NLP signals with time series predictions to generate buy/sell/hold orders.
4. **Input Security** — Validates and sanitizes model inputs to prevent adversarial attacks, data poisoning, and injection of malicious signals into the trading logic.

### How it works

The system follows a pipeline approach:

```
News/Social Data --> NLP Sentiment Analysis --\
                                               +--> Signal Fusion --> Order Execution
Historical Data  --> Time Series Forecast   --/
```

Security checks are applied at every stage where external or model-generated data enters the trading pipeline, ensuring that corrupted or adversarial inputs cannot compromise the system.

## Project Structure

```
tfm-trading-bot/
├── notebooks/    # Jupyter notebooks for experiments, tests, and analysis
├── README.md
└── .gitignore
```

The notebooks folder contains:
- Data exploration and preprocessing
- Model training and evaluation
- Backtesting strategies
- Security validation experiments

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install jupyter pandas numpy scikit-learn torch transformers
```

## License

MIT
