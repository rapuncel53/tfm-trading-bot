"""Script de ejecución principal del experimento de Predicción de Retornos con LLMs.
"""

import sys, os
sys.path.insert(0, '.')
import argparse

from src.config import ModelConfig, DataConfig, TrainingConfig
from src.dataset import StockReturnNewsDataset
from src.financial_context import FinancialContextEngine
from src.metrics import PortfolioEvaluator

def main():
    parser = argparse.ArgumentParser(description="TFM: Fine-Tuning LLMs for Stock Return Prediction (EMNLP 2024)")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3.5-9B", help="Backbone LLM en Hugging Face")
    parser.add_argument("--target", type=str, default="ret_1d", choices=["ret_1d", "ret_3d", "ret_5d"], help="Horizonte de retorno a predecir")
    parser.add_argument("--pooling", type=str, default="aggregated", choices=["aggregated", "bottleneck"], help="Tipo de pooling (aggregated=Eq.5 mean pooling)")
    parser.add_argument("--batch_size", type=int, default=4, help="Tamaño de batch por paso")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas")
    parser.add_argument("--max_steps", type=int, default=None, help="Límite máximo de pasos de optimización (para pruebas piloto)")
    parser.add_argument("--max_hours", type=float, default=None, help="Límite máximo de horas de entrenamiento continuo")
    parser.add_argument("--eval_limit", type=int, default=None, help="Límite de muestras a evaluar en val/test (para pruebas piloto)")
    parser.add_argument("--eval_steps", type=int, default=50, help="Frecuencia de validación en pasos de optimización")
    parser.add_argument("--save_steps", type=int, default=25, help="Frecuencia de guardado de checkpoints en pasos")
    parser.add_argument("--resume", action="store_true", help="Reanudar entrenamiento desde checkpoint previo")
    parser.add_argument("--dry_run", action="store_true", help="Modo de prueba rápida sin entrenamiento completo")
    args = parser.parse_args()

    print("=================================================================")
    print("   TFM: PREDICCIÓN DE RETORNOS BURSÁTILES MEDIANTE LLMs (EMNLP 2024)")
    print("=================================================================")
    print(f"Modelo seleccionado : {args.model}")
    print(f"Horizonte Target    : {args.target}")
    print(f"Estrategia Pooling  : {args.pooling} (Eq. 5 Mean Pooling)")
    print(f"Pasos máximos       : {args.max_steps}")
    print(f"Horas máximas       : {args.max_hours}")
    print(f"Límite evaluación   : {args.eval_limit}")
    print(f"Eval steps          : {args.eval_steps}")
    print(f"Reanudar (Resume)   : {args.resume}")
    print(f"Modo Dry-Run        : {args.dry_run}")
    print("-----------------------------------------------------------------")

    # 1. Configurar
    model_cfg = ModelConfig(
        model_name_or_path=args.model,
        pooling_type=args.pooling,
        use_qlora=True
    )
    data_cfg = DataConfig(target_return=args.target)
    train_cfg = TrainingConfig(
        batch_size=args.batch_size,
        epochs=args.epochs,
        max_steps=args.max_steps,
        max_hours=args.max_hours,
        eval_limit=args.eval_limit,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        resume=args.resume
    )

    if args.dry_run:
        print("\n[Dry-Run] Verificando carga de datos y generación de prompts...")
        ds_train = StockReturnNewsDataset(data_cfg.train_path, target_col=args.target)
        sample = ds_train[0]
        print(f"  Ticker: {sample['ticker']} | Fecha: {sample['date']} | Target {args.target}: {sample['target']*100:+.2f}%")
        print("\n--- Muestra del Prompt Generado ---")
        print(sample['prompt_text'][:600] + "\n...")

        print("\n[Dry-Run] Verificando evaluador de carteras (deciles y Sharpe)...")
        evaluator = PortfolioEvaluator()
        # Test simulado
        import pandas as pd
        import numpy as np
        sim_df = pd.DataFrame({
            'date': ['2023-01-01'] * 20 + ['2023-01-02'] * 20,
            'ticker': [f'STK{i}' for i in range(20)] * 2,
            'pred': np.random.randn(40),
            'target': np.random.randn(40) * 0.02
        })
        res = evaluator.evaluate_deciles(sim_df)
        print("  Evaluador de cartera operativo:")
        print(f"    Long-Only Sharpe (simulado): {res['long_only']['sharpe_ratio']:.2f}")
        print(f"    Rank IC (Spearman): {res['rank_ic']:+.4f}")
        print("\n[Dry-Run] Todos los componentes verificados con éxito.")
        return

    # Si no es dry_run, importar Trainer e iniciar
    try:
        from src.train import StockReturnTrainer
        trainer = StockReturnTrainer(model_cfg, data_cfg, train_cfg)
        trainer.train()
    except ImportError as e:
        print(f"\n[Aviso] Se requiere instalar torch, transformers, peft para ejecutar el entrenamiento completo en GPU.")
        print(f"Detalle del error: {e}")

if __name__ == '__main__':
    main()
