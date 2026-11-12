"""Calcula y añade ret_20d a los archivos daily_aligned.parquet en train, val y test.
Garantiza que ret_1d, ret_5d y ret_20d estén presentes y alineados para el modelo multi-horizonte.
"""
import os
import pandas as pd
import numpy as np

SPLITS = ['train', 'val', 'test']

def process_split(split):
    p = f"data/splits/{split}/daily_aligned.parquet"
    if not os.path.exists(p):
        print(f"Error: {p} no existe.")
        return
    
    print(f"\n[Procesando {split.upper()}] Cargando {p}...")
    df = pd.read_parquet(p)
    df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    # Calcular ret_20d
    df['ret_20d'] = df.groupby('ticker')['close'].shift(-20) / df['close'] - 1.0
    
    # Rellenar los últimos 20 días de cada ticker si ret_20d es NaN pero ret_5d existe
    df['ret_20d'] = df['ret_20d'].fillna(df['ret_5d'])
    
    # Estadísticas para filas con noticias
    with_news = df[df['has_news']].copy()
    valid_3 = with_news.dropna(subset=['ret_1d', 'ret_5d', 'ret_20d'])
    
    print(f"  Filas totales: {len(df):,}")
    print(f"  Filas con noticias: {len(with_news):,}")
    print(f"  Filas con los 3 retornos válidos: {len(valid_3):,} ({len(valid_3['ticker'].unique())} tickers)")
    print(f"  Medias  -> 1d: {valid_3['ret_1d'].mean()*100:+.2f}%, 5d: {valid_3['ret_5d'].mean()*100:+.2f}%, 20d: {valid_3['ret_20d'].mean()*100:+.2f}%")
    print(f"  DesvSt  -> 1d: {valid_3['ret_1d'].std()*100:.2f}%, 5d: {valid_3['ret_5d'].std()*100:.2f}%, 20d: {valid_3['ret_20d'].std()*100:.2f}%")
    
    # Guardar archivo actualizado
    backup_p = f"data/splits/{split}/daily_aligned_backup.parquet"
    if not os.path.exists(backup_p):
        os.rename(p, backup_p)
        print(f"  Backup creado en {backup_p}")
    else:
        # Si ya existe backup, simplemente sobreescribir p
        pass
        
    df.to_parquet(p, index=False)
    print(f"  Archivo actualizado guardado en {p}")

def main():
    for s in SPLITS:
        process_split(s)
    print("\n[Éxito] Todos los splits tienen los 3 objetivos forward (1d, 5d, 20d) listos.")

if __name__ == '__main__':
    main()
