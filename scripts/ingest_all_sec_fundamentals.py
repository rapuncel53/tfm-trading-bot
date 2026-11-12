import sys, os
sys.path.insert(0, '.')
import pandas as pd
from src.financial_context import FinancialContextEngine

def main():
    print("Iniciando ingestión completa de fundamentales SEC EDGAR para todas las empresas de Tier 1...")
    
    # Cargar lista completa de empresas Tier 1
    df_t1 = pd.read_csv('data/tier1_fechas_noticias.csv', sep=';')
    all_tickers = sorted(df_t1['sym'].unique().tolist())
    print(f"Total empresas objetivo: {len(all_tickers)}")
    
    engine = FinancialContextEngine()
    
    # Ingestar XBRL JSONs faltantes
    downloaded = engine.ingest_tickers(all_tickers)
    print(f"Descargados {len(downloaded)} nuevos archivos XBRL de la SEC.")
    
    # Parsear todos los estados trimestrales
    print("Parseando estados trimestrales oficiales (10-Q / 10-K)...")
    df_fund = engine.parse_quarterly_fundamentals(all_tickers)
    print(f"Total estados financieros parseados: {len(df_fund):,} registros para {df_fund['ticker'].nunique()} empresas.")
    
    # Enriquecer los splits oficiales con fundamentales ASOF
    splits = ['train', 'val', 'test']
    for sp in splits:
        p_path = f"data/splits/{sp}/daily_aligned.parquet"
        if not os.path.exists(p_path): continue
        print(f"Enriqueciendo {sp} set con fundamentales...")
        df_sp = pd.read_parquet(p_path)
        df_enr = engine.enrich_dataframe_asof(df_sp)
        df_enr.to_parquet(p_path, index=False)
        # guardar también en csv comprimido
        df_enr.to_csv(f"data/splits/{sp}/daily_aligned.csv.gz", index=False, compression='gzip')
        print(f"  {sp.upper()} actualizado: {len(df_enr):,} filas, {len(df_enr.columns)} columnas.")

    print("\nProceso de contexto financiero completado al 100%.")

if __name__ == '__main__':
    import os
    main()
