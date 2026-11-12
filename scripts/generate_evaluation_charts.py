"""Generador de Gráficos y Visualizaciones de Evaluación Cuantitativa del TFM.

Genera figuras de alta resolución (300 DPI) para la memoria y presentación del TFM:
1. Curvas de Convergencia del Entrenamiento (500 Pasos).
2. Distribución y Monotonicidad por Deciles de Cartera (Réplica EMNLP 2024 Fig. 3).
3. Dispersión Predicción vs Retorno Real y Cuadrantes Direccionales.
4. Precisión Direccional (Hit Ratio) y Distribución del Error.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, pearsonr

# Estilo visual moderno y formal para publicaciones científicas
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def generate_training_curves(history_csv: str, output_path: str):
    """Genera el panel de 4 cuadrantes con la evolución del entrenamiento a lo largo de 500 pasos."""
    if not os.path.exists(history_csv):
        print(f"[Aviso] No se encontró {history_csv}")
        return

    df = pd.read_csv(history_csv)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    max_steps_val = int(df['step'].max())
    fig.suptitle(f"Evolución del Entrenamiento Qwen3.5-9B (QLoRA) - {max_steps_val} Pasos de Optimización\n"
                 "TFM: Fine-Tuning LLMs for Stock Return Prediction (EMNLP 2024)", fontsize=14, fontweight='bold', y=0.98)

    # 1. Train Loss
    ax = axes[0, 0]
    ax.plot(df['step'], df['train_loss'], marker='o', color='#1f77b4', linewidth=2, markersize=5, label='Train Loss (MSE)')
    ax.set_title("A. Pérdida de Entrenamiento (MSE Loss)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Paso de Optimización")
    ax.set_ylabel("Pérdida (MSE)")
    ax.set_yscale('log')
    ax.grid(True, linestyle='--', alpha=0.6)
    min_loss_row = df.loc[df['train_loss'].idxmin()]
    ax.annotate(f"Mínimo: {min_loss_row['train_loss']:.4f}\n(Paso {int(min_loss_row['step'])})",
                xy=(min_loss_row['step'], min_loss_row['train_loss']),
                xytext=(min_loss_row['step'] - 70, min_loss_row['train_loss'] * 3),
                arrowprops=dict(facecolor='#1f77b4', shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight='semibold')
    ax.legend(loc='upper right')

    # 2. Validation RMSE
    ax = axes[0, 1]
    ax.plot(df['step'], df['val_rmse'], marker='s', color='#2ca02c', linewidth=2, markersize=5, label='Val RMSE')
    best_row = df.loc[df['val_rmse'].idxmin()]
    ax.axhline(best_row['val_rmse'], color='#d62728', linestyle=':', alpha=0.7, label=f'Récord: {best_row["val_rmse"]:.4f}')
    ax.scatter([best_row['step']], [best_row['val_rmse']], color='#d62728', s=100, zorder=5)
    ax.annotate(f"Récord Histórico: {best_row['val_rmse']:.4f}\n(Paso {int(best_row['step'])})",
                xy=(best_row['step'], best_row['val_rmse']),
                xytext=(best_row['step'] - 90, best_row['val_rmse'] + 0.025),
                arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight='semibold', color='#d62728')
    ax.set_title("B. Error de Generalización en Validación (RMSE)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Paso de Optimización")
    ax.set_ylabel("RMSE")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')

    # 3. Validation Rank IC (Spearman rho)
    ax = axes[1, 0]
    colors = ['#2ca02c' if v > 0 else '#d62728' for v in df['val_rank_ic']]
    ax.plot(df['step'], df['val_rank_ic'], color='#ff7f0e', linewidth=2, alpha=0.7)
    ax.scatter(df['step'], df['val_rank_ic'], c=colors, s=50, zorder=4, label='Rank IC (Spearman)')
    ax.axhline(0.0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.axhline(0.03, color='#2ca02c', linestyle='--', linewidth=1.2, alpha=0.8, label='Umbral Señal Fuerte (+0.03)')
    ax.set_title("C. Coeficiente de Información por Ranking (Val Rank IC)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Paso de Optimización")
    ax.set_ylabel("Rank IC (Spearman ρ)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')

    # 4. Learning Rate Schedule
    ax = axes[1, 1]
    ax.plot(df['step'], df['lr'], color='#9467bd', linewidth=2, label='Learning Rate (AdamW)')
    ax.set_title("D. Programa de Tasa de Aprendizaje (Warmup + Decaimiento)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Paso de Optimización")
    ax.set_ylabel("Tasa de Aprendizaje (LR)")
    ax.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Gráfico Guardado] {output_path}")


def generate_deciles_chart(predictions_csv: str, output_path: str, title_suffix: str = "Validation"):
    """Genera el gráfico de barras por deciles de retorno pronosticado vs retorno real."""
    if not os.path.exists(predictions_csv):
        print(f"[Aviso] No se encontró {predictions_csv}")
        return

    df = pd.read_csv(predictions_csv)
    if 'decile' not in df.columns:
        df['decile'] = pd.qcut(df['pred_return'], q=min(10, len(df)), labels=False, duplicates='drop')

    decile_stats = []
    for d in sorted(df['decile'].unique()):
        sub = df[df['decile'] == d]
        decile_stats.append({
            'decile': f"D{d}",
            'pred_mean': sub['pred_return'].mean() * 100,
            'actual_mean': sub['actual_return'].mean() * 100,
            'count': len(sub)
        })
    stats_df = pd.DataFrame(decile_stats)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(stats_df))
    width = 0.38

    rects1 = ax.bar(x - width/2, stats_df['pred_mean'], width, label='Retorno Medio Pronosticado (%)', color='#4a90e2', alpha=0.9, edgecolor='white')
    rects2 = ax.bar(x + width/2, stats_df['actual_mean'], width, label='Retorno Medio Real de Mercado (%)', color='#50e3c2', alpha=0.9, edgecolor='white')

    ax.set_title(f"Monotonicidad de la Estrategia por Deciles (EMNLP 2024 Fig. 3) - {title_suffix}\n"
                 f"Comparativa: Decil 0 (Más Pesimista / Short) vs Decil 9 (Más Optimista / Long)",
                 fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Decil de Señal de Inversión", fontsize=11, fontweight='semibold')
    ax.set_ylabel("Retorno Medio (%)", fontsize=11, fontweight='semibold')
    ax.set_xticks(x)
    ax.set_xticklabels(stats_df['decile'], fontsize=10, fontweight='bold')
    ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.legend(fontsize=10, loc='best', frameon=True)

    # Anotar valores en las barras
    for r in rects1:
        h = r.get_height()
        va = 'bottom' if h >= 0 else 'top'
        ax.annotate(f"{h:+.2f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2 if h >= 0 else -6),
                    textcoords="offset points", ha='center', va=va, fontsize=8, color='#1f4788', fontweight='bold')
    for r in rects2:
        h = r.get_height()
        va = 'bottom' if h >= 0 else 'top'
        ax.annotate(f"{h:+.2f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2 if h >= 0 else -6),
                    textcoords="offset points", ha='center', va=va, fontsize=8, color='#0f7864', fontweight='bold')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Gráfico Guardado] {output_path}")


def generate_scatter_and_hit_ratio(predictions_csv: str, output_scatter: str, output_hit: str, split_name: str = "Validation"):
    """Genera el scatter plot con recta de regresión y el gráfico de acierto direccional (Hit Ratio)."""
    if not os.path.exists(predictions_csv):
        return

    df = pd.read_csv(predictions_csv)
    y_pred = df['pred_return'].values * 100
    y_true = df['actual_return'].values * 100

    # 1. Scatter Plot
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    sp_corr, _ = spearmanr(y_pred, y_true)
    pe_corr, _ = pearsonr(y_pred, y_true)

    sns.regplot(x=y_pred, y=y_true, ax=ax,
                color='#1f77b4',
                scatter_kws={'alpha': 0.5, 's': 35, 'color': '#2b5c8f'},
                line_kws={'color': '#e74c3c', 'linewidth': 2, 'label': f'Ajuste Lineal (Pearson r={pe_corr:+.3f})'})

    # Línea ideal y=x
    min_v = min(np.percentile(y_pred, 1), np.percentile(y_true, 1))
    max_v = max(np.percentile(y_pred, 99), np.percentile(y_true, 99))
    ax.plot([min_v, max_v], [min_v, max_v], 'k--', alpha=0.5, label='Pronóstico Perfecto (y = x)')

    # Ejes cero y cuadrantes
    ax.axhline(0, color='gray', linestyle=':', alpha=0.7)
    ax.axvline(0, color='gray', linestyle=':', alpha=0.7)

    # Cuadrantes direccionales
    correct_up = ((y_pred > 0) & (y_true > 0)).sum()
    correct_down = ((y_pred < 0) & (y_true < 0)).sum()
    total_valid = (y_true != 0).sum()
    hit_ratio = (correct_up + correct_down) / total_valid * 100 if total_valid > 0 else 50.0

    ax.text(0.04, 0.93, f"Aciertos Cortos (Pred < 0 & Real < 0): {correct_down}", transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#81c784", alpha=0.8))
    ax.text(0.55, 0.05, f"Aciertos Largos (Pred > 0 & Real > 0): {correct_up}", transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#81c784", alpha=0.8))

    ax.set_title(f"Dispersión de Pronóstico vs Retorno Real - {split_name} ({len(df)} muestras)\n"
                 f"Rank IC (Spearman): {sp_corr:+.4f} | Precisión Direccional: {hit_ratio:.2f}%",
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Retorno Pronosticado por LLM (%)", fontsize=11, fontweight='semibold')
    ax.set_ylabel("Retorno Realizado de Mercado (%)", fontsize=11, fontweight='semibold')
    ax.set_xlim([np.percentile(y_pred, 0.5) - 1, np.percentile(y_pred, 99.5) + 1])
    ax.set_ylim([np.percentile(y_true, 0.5) - 1, np.percentile(y_true, 99.5) + 1])
    ax.legend(loc='lower right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_scatter), exist_ok=True)
    plt.savefig(output_scatter, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Gráfico Guardado] {output_scatter}")

    # 2. Gráfico de Hit Ratio y Distribución de Errores
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # Donut de Hit Ratio
    ax1 = axes[0]
    sizes = [hit_ratio, 100 - hit_ratio]
    colors = ['#2ecc71', '#e74c3c']
    explode = (0.05, 0)
    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=['Acierto Direccional (Hit)', 'Fallo'],
                                       autopct='%1.2f%%', startangle=90, colors=colors,
                                       textprops=dict(color="black", fontweight='bold', fontsize=11),
                                       wedgeprops=dict(width=0.4, edgecolor='white'))
    ax1.set_title(f"Acierto Direccional vs Paseo Aleatorio\n(Benchmark Mercado: 50.0%)", fontsize=11, fontweight='bold')

    # Histograma de errores de predicción
    ax2 = axes[1]
    errors = (df['pred_return'] - df['actual_return']) * 100
    sns.histplot(errors, bins=35, kde=True, ax=ax2, color='#3498db', edgecolor='white', alpha=0.7)
    ax2.axvline(0, color='red', linestyle='--', linewidth=1.5, label=f'Media: {errors.mean():+.2f}%')
    ax2.axvline(errors.median(), color='green', linestyle=':', linewidth=1.5, label=f'Mediana: {errors.median():+.2f}%')
    ax2.set_title("Distribución del Error Residual de Predicción (Pred - Actual)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Error de Predicción (%)", fontsize=10, fontweight='semibold')
    ax2.set_ylabel("Frecuencia", fontsize=10, fontweight='semibold')
    ax2.set_xlim([np.percentile(errors, 1), np.percentile(errors, 99)])
    ax2.legend(loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_hit), exist_ok=True)
    plt.savefig(output_hit, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Gráfico Guardado] {output_hit}")


if __name__ == '__main__':
    charts_dir = "checkpoints/llm_return_regressor/charts"
    history_file = "checkpoints/llm_return_regressor/training_history.csv"
    val_preds_file = "checkpoints/llm_return_regressor/val_predictions_best500.csv"
    if not os.path.exists(val_preds_file):
        val_preds_file = "checkpoints/llm_return_regressor/val_predictions_step200.csv"

    print("Generando suite completa de gráficos...")
    generate_training_curves(history_file, f"{charts_dir}/1_training_convergence_700steps.png")
    generate_training_curves(history_file, f"{charts_dir}/1_training_convergence_500steps.png")
    generate_deciles_chart(val_preds_file, f"{charts_dir}/2_portfolio_deciles_return.png", "Validation Set")
    generate_scatter_and_hit_ratio(val_preds_file,
                                   f"{charts_dir}/3_pred_vs_actual_scatter.png",
                                   f"{charts_dir}/4_directional_accuracy_hit_ratio.png",
                                   "Validation Set")
    print("Suite de gráficos completada exitosamente.")
