"""Evaluación profunda del Validation Set (2019-2020) y Test Set (2021-2023) a 1 mes (20 días).

Compara sobre el horizonte mensual:
- Factors Alone
- News Alone
- Fusion Combination (Eq. 3)
- Mixture Decoupled (Eq. 12-15)

Genera métricas de predicción, carteras decílicas y gráficos comparativos.
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
from torch.utils.data import TensorDataset, DataLoader

from scripts.train_and_evaluate_improved import (
    build_enhanced_factors_and_targets, train_single_model, compute_metrics
)
from src.multimodal_models import (
    FactorsAlone, NewsAlone, FusionCombination, MixtureModel
)


def main():
    parser = argparse.ArgumentParser(description="Evaluación de Validación a 1 mes (20d)")
    parser.add_argument("--features_path", type=str, default="checkpoints/multimodal/features.pt")
    parser.add_argument("--output_dir", type=str, default="checkpoints/multimodal/val_20d_results")
    parser.add_argument("--epochs", type=int, default=45)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Val 20d] Dispositivo: {device}")

    # 1. Cargar bundle de representaciones latentes
    bundle = torch.load(args.features_path, map_location='cpu', weights_only=False)
    news_dim = bundle['train']['x_n'].shape[1]

    # 2. Factores cuantitativos pasados y objetivos forward a 20 días
    print("[Val 20d] Construyendo factores pasados y objetivos ret_20d...")
    train_xf, train_targets, factor_names, scaler = build_enhanced_factors_and_targets(
        'train', bundle['train']['dates'], bundle['train']['tickers'], scaler_dict=None
    )
    val_xf, val_targets, _, _ = build_enhanced_factors_and_targets(
        'val', bundle['val']['dates'], bundle['val']['tickers'], scaler_dict=scaler
    )
    test_xf, test_targets, _, _ = build_enhanced_factors_and_targets(
        'test', bundle['test']['dates'], bundle['test']['tickers'], scaler_dict=scaler
    )

    target_key = 'ret_20d'
    y_train = train_targets[target_key]
    y_val = val_targets[target_key]
    y_test = test_targets[target_key]

    print(f"[Val 20d] Target: {target_key} (Retorno forward a 20 días / 1 mes)")
    print(f"[Val 20d] Muestras: Train={len(y_train)}, Val={len(y_val)}, Test={len(y_test)}")
    print(f"[Val 20d] Estadísticas de ret_20d en Val (%): Media={y_val.mean()*100:.2f}%, Std={y_val.std()*100:.2f}%")
    print(f"[Val 20d] Estadísticas de ret_20d en Test (%): Media={y_test.mean()*100:.2f}%, Std={y_test.std()*100:.2f}%")

    # 3. DataLoaders
    train_ds = TensorDataset(train_xf, bundle['train']['x_n'], y_train)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)

    models = {
        'Factors Alone': FactorsAlone(num_factors=len(factor_names), hidden_dim=64),
        'News Alone': NewsAlone(news_dim=news_dim),
        'Fusion Combination': FusionCombination(num_factors=len(factor_names), news_dim=news_dim, bottleneck_dim=256, fusion_dim=128),
        'Mixture Decoupled': MixtureModel(num_factors=len(factor_names), news_dim=news_dim, bottleneck_dim=256, fusion_dim=128)
    }

    val_metrics = {}
    test_metrics = {}
    predictions_val = {'ticker': bundle['val']['tickers'], 'date': bundle['val']['dates'], 'actual_return': y_val.numpy()}
    predictions_test = {'ticker': bundle['test']['tickers'], 'date': bundle['test']['dates'], 'actual_return': y_test.numpy()}

    print("\n" + "="*85)
    print("                 ENTRENANDO ARQUITECTURAS A 1 MES (20 DÍAS)              ")
    print("="*85)

    for name, m in models.items():
        print(f"\n[Entrenando] {name}...")
        is_mix = (name == 'Mixture Decoupled')
        trained = train_single_model(
            m, train_loader, val_xf, bundle['val']['x_n'], y_val,
            device=device, epochs=args.epochs, lr=args.lr, use_directional_loss=False, is_mixture=is_mix
        )
        trained.eval()
        with torch.no_grad():
            if is_mix:
                vp = trained(val_xf.to(device), bundle['val']['x_n'].to(device))['pred_mix'].cpu().numpy()
                tp = trained(test_xf.to(device), bundle['test']['x_n'].to(device))['pred_mix'].cpu().numpy()
            elif isinstance(trained, FactorsAlone):
                vp = trained(val_xf.to(device)).cpu().numpy()
                tp = trained(test_xf.to(device)).cpu().numpy()
            elif isinstance(trained, NewsAlone):
                vp = trained(bundle['val']['x_n'].to(device)).cpu().numpy()
                tp = trained(bundle['test']['x_n'].to(device)).cpu().numpy()
            else:
                vp = trained(val_xf.to(device), bundle['val']['x_n'].to(device)).cpu().numpy()
                tp = trained(test_xf.to(device), bundle['test']['x_n'].to(device)).cpu().numpy()

        val_m = compute_metrics(vp, y_val.numpy())
        test_m = compute_metrics(tp, y_test.numpy())

        val_metrics[name] = val_m
        test_metrics[name] = test_m

        predictions_val[name.replace(' ', '_')] = vp
        predictions_test[name.replace(' ', '_')] = tp

        print(f"  -> Val:  Hit={val_m['hit_ratio']:.2f}% | Rank IC={val_m['rank_ic']:+.4f} | L/S Spread={val_m['ls_spread']:+.2f}% | Sharpe={val_m['ls_sharpe']:.2f}")
        print(f"  -> Test: Hit={test_m['hit_ratio']:.2f}% | Rank IC={test_m['rank_ic']:+.4f} | L/S Spread={test_m['ls_spread']:+.2f}% | Sharpe={test_m['ls_sharpe']:.2f}")

    # Guardar predicciones en CSV
    pd.DataFrame(predictions_val).to_csv(os.path.join(args.output_dir, "val_predictions_20d.csv"), index=False)
    pd.DataFrame(predictions_test).to_csv(os.path.join(args.output_dir, "test_predictions_20d.csv"), index=False)

    # 4. Tablas Comparativas Oficiales
    print("\n" + "="*105)
    print("          TABLA 1: RESULTADOS EN VALIDATION SET (2019-2020) — HORIZONTE 1 MES (20 DÍAS)        ")
    print("="*105)
    print(f"{'Modelo':<24} | {'Hit Ratio%':<11} {'Rank IC':<10} {'Pearson r':<11} {'L/S Spread':<11} {'Sharpe L/S':<10} {'RMSE%':<7}")
    print("-" * 105)
    for name, m in val_metrics.items():
        print(f"{name:<24} | {m['hit_ratio']:>9.2f}% {m['rank_ic']:>+9.4f} {m['pearson']:>+10.4f} {m['ls_spread']:>+10.2f}% {m['ls_sharpe']:>9.2f} {m['rmse']*100:>6.2f}%")
    print("="*105)

    print("\n" + "="*105)
    print("              TABLA 2: RESULTADOS EN TEST SET (2021-2023) — HORIZONTE 1 MES (20 DÍAS)          ")
    print("="*105)
    print(f"{'Modelo':<24} | {'Hit Ratio%':<11} {'Rank IC':<10} {'Pearson r':<11} {'L/S Spread':<11} {'Sharpe L/S':<10} {'RMSE%':<7}")
    print("-" * 105)
    for name, m in test_metrics.items():
        print(f"{name:<24} | {m['hit_ratio']:>9.2f}% {m['rank_ic']:>+9.4f} {m['pearson']:>+10.4f} {m['ls_spread']:>+10.2f}% {m['ls_sharpe']:>9.2f} {m['rmse']*100:>6.2f}%")
    print("="*105)

    # 5. Desglose Detallado por Deciles en Validation Set
    print("\n" + "="*85)
    print("            DESGLOSE POR DECILES EN VALIDATION SET (RETORNO REAL % EN 20D)             ")
    print("="*85)
    dec_df = pd.DataFrame({name: [val_metrics[name]['decile_returns'][d]*100 for d in range(10)] for name in models.keys()},
                          index=[f"D{d}" for d in range(10)])
    print(dec_df.round(3))
    print("="*85)

    # 6. Gráficos Comparativos: Val vs Test
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    model_names = list(models.keys())
    x = np.arange(len(model_names))
    width = 0.35

    # Hit Ratio Val vs Test
    val_hits = [val_metrics[m]['hit_ratio'] for m in model_names]
    test_hits = [test_metrics[m]['hit_ratio'] for m in model_names]

    b1 = ax1.bar(x - width/2, val_hits, width, label='Validación (2019-2020)', color='#337ab7', alpha=0.85)
    b2 = ax1.bar(x + width/2, test_hits, width, label='Test Ciego (2021-2023)', color='#f0ad4e', alpha=0.85)
    ax1.axhline(50.0, color='black', linestyle='--', linewidth=0.8, label='Paseo Aleatorio')
    ax1.set_title("Acierto Direccional (Hit Ratio %) a 1 Mes (20d)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Hit Ratio (%)", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_names, rotation=15)
    ax1.set_ylim(40, 75)
    ax1.legend(loc='lower right')
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 0.8, f"{h:.1f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Rank IC Val vs Test
    val_ics = [val_metrics[m]['rank_ic'] for m in model_names]
    test_ics = [test_metrics[m]['rank_ic'] for m in model_names]

    b3 = ax2.bar(x - width/2, val_ics, width, label='Validación (2019-2020)', color='#337ab7', alpha=0.85)
    b4 = ax2.bar(x + width/2, test_ics, width, label='Test Ciego (2021-2023)', color='#f0ad4e', alpha=0.85)
    ax2.axhline(0.0, color='black', linestyle='--', linewidth=0.8)
    ax2.axhline(0.03, color='gray', linestyle=':', linewidth=0.8, label='Umbral Institucional (+0.03)')
    ax2.set_title("Poder de Ordenación (Rank IC) a 1 Mes (20d)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Rank IC de Spearman", fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(model_names, rotation=15)
    ax2.legend()
    for b in list(b3) + list(b4):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + (0.01 if h>=0 else -0.02), f"{h:+.3f}", ha='center', va='bottom' if h>=0 else 'top', fontsize=8, fontweight='bold')

    plt.tight_layout()
    chart_path = os.path.join(args.output_dir, "val_vs_test_20d_comparison.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"\n[Gráfico Comparativo Val vs Test] Guardado en: {chart_path}")

    # Copiar gráfico a la carpeta de artefactos
    art_dir = r"C:\Users\julia\.gemini\antigravity\brain\9f7a61e6-afb4-4584-a3e5-1f6d74df8639"
    dst = os.path.join(art_dir, "val_vs_test_20d_comparison.png")
    import shutil
    shutil.copyfile(chart_path, dst)
    print(f"[Copia en Artefactos] Guardado en: {dst}")


if __name__ == "__main__":
    main()
