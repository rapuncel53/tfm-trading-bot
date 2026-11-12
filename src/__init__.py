"""Módulo principal del proyecto TFM: Predicción de retornos mediante Fine-Tuning de LLMs.
"""

from src.config import ModelConfig, DataConfig, TrainingConfig
from src.financial_context import FinancialContextEngine
from src.dataset import StockReturnNewsDataset, build_stock_prompt
from src.model import LLMReturnRegressor, MaskedMeanPooling, ForecastingHead
from src.metrics import PortfolioEvaluator

__all__ = [
    "ModelConfig",
    "DataConfig",
    "TrainingConfig",
    "FinancialContextEngine",
    "StockReturnNewsDataset",
    "build_stock_prompt",
    "LLMReturnRegressor",
    "MaskedMeanPooling",
    "ForecastingHead",
    "PortfolioEvaluator"
]
