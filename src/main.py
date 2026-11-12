#!/usr/bin/env python3
"""
TFM Multimodal Stock Return Forecasting Engine
Forecasting Cross-Sectional Stock Returns via Multimodal Fusion of Financial Newsflow (LLMs) and SEC Accounting Factors.
"""

from src.config import Config
from src.multimodal_models import FusionCombination, FactorsAlone, NewsAlone

def main():
    print("=" * 70)
    print("TFM: Multimodal Stock Return Forecasting Engine")
    print("Reference Literature: RAM Active Investments (Tian Guo & Emmanuel Hauptmann)")
    print("Backbone: Qwen/Qwen3.5-9B QLoRA | Horizon: 20 Trading Days (1-Month Forward PEAD)")
    print("=" * 70)

if __name__ == "__main__":
    main()
