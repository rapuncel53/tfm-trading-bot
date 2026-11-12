import json
import pandas as pd

df = pd.read_csv('data/resumen_cobertura_y_huecos.csv', sep=';')
with open('data/catalog/companies_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

cat_map = {c['sym']: c for c in catalog}

md = []
md.append("# Catálogo Maestro de Empresas, Periodos de Noticias y Visor de Titulares (TFM)\n")
md.append("> **Propósito:** Definir el universo de empresas elegibles para el Trabajo de Fin de Máster (TFM), detallando la calidad de los datos bursátiles (OHLCV 2000–2023), los periodos exactos de noticias disponibles (FNSPID y Benzinga) y la auditoría rigurosa de huecos temporales.\n")
md.append("---\n")

md.append("## 1. Resumen Ejecutivo del Universo de Datos\n")
md.append("* **Activos de bolsa auditados inicialmente:** 7.693 tickers.")
md.append("* **Filtros de calidad aplicados:**")
md.append("  * Eliminación del corte abrupto de julio de 2020 (*seam* de Yahoo Finance).")
md.append("  * Verificación física del OHLC (Low <= Open/Close/High, High >= Low, Vol >= 0).")
md.append("  * Pertenencia oficial al índice S&P 500 (SEC CIK verificado).")
md.append("* **Empresas Tier 1 Gold resultantes:** **199 empresas** con más de 20 años de precios diarios limpios (2000 a 2023).\n")

md.append("### Clasificación de Cobertura de Noticias\n")
md.append("| Categoría | Nº Empresas | Periodo Noticias | Existencia de Huecos | Idoneidad TFM |")
md.append("| :--- | :---: | :---: | :---: | :--- |")
md.append("| **Grupo 1: Continua Total** | **136** | **2009/2012 – 2023** | **0 huecos estructurales** | **Máxima (Recomendada)** |")
md.append("| **Grupo 2: Big Tech Híbrida** | **22** | **2010/2019 – 2023** | **Hueco central (14 a 33 meses)** | Condicional (tratamiento de salto) |")
md.append("| **Grupo 3: Continua Media** | **33** | **2013/2019 – 2023** | **0 huecos** | Alta (empresas más jóvenes) |")
md.append("| **Grupo 4: Reciente / Fragmentada** | **8** | **2022/2023** | Fragmentada | Desaconsejada |")
md.append("\n---\n")

md.append("## 2. Visor Interactivo HTML\n")
md.append("Se ha generado un cuadro de mando interactivo autónomo que permite filtrar, buscar y visualizar titulares reales:")
md.append("👉 **[Abrir Dashboard Interactivo (catalogo_empresas_y_noticias.html)](file:///C:/Users/julia/.gemini/antigravity/brain/9f7a61e6-afb4-4584-a3e5-1f6d74df8639/catalogo_empresas_y_noticias.html)**\n")
md.append("---\n")

md.append("## 3. Grupo 1: Las 136 Empresas con Cobertura Continua (Sin Huecos)\n")
md.append("Estas empresas son el núcleo óptimo para el entrenamiento y backtesting del modelo. Tienen cotizaciones diarias completas (2000–2023) y un flujo de noticias continuo mes a mes desde 2009 hasta finales de 2023.\n")

c1 = df[df['categoria'] == '1. CONTINUA_TOTAL_SIN_HUECOS']
for sec in sorted(c1['sector'].unique()):
    sec_df = c1[c1['sector'] == sec].sort_values(by='total_noticias', ascending=False)
    md.append(f"### Sector: {sec} ({len(sec_df)} empresas)")
    md.append("| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |")
    md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    for idx, r in sec_df.iterrows():
        md.append(f"| **`{r['sym']}`** | {r['sec_name']} | {r['n_prices']} | {r['fn_count']:,} | {r['bz_count']:,} | **{r['total_noticias']:,}** | {r['uni_start']} a {r['uni_end']} |")
    md.append("")

md.append("---\n")
md.append("## 4. Grupo 2: Big Tech Híbridas (Detalle del Hueco Central)\n")
md.append("Para estas 22 empresas, Benzinga cubre el periodo histórico hasta el **10 de junio de 2020**, y FNSPID comienza más tarde debido al límite de 8.700 noticias del scraper de NASDAQ. Existe un hueco intermedio que debe tenerse en cuenta si se utilizan:\n")

c2 = df[df['categoria'] == '2. HIBRIDA_CON_HUECO'].sort_values(by='gap_days', ascending=True)
md.append("| Ticker | Empresa | Sector | Fin Benzinga | Inicio FNSPID | Duración del Hueco | Meses Vacíos |")
md.append("| :--- | :--- | :--- | :---: | :---: | :---: | :---: |")
for idx, r in c2.iterrows():
    meses = r['gap_days'] / 30.4
    md.append(f"| **`{r['sym']}`** | {r['sec_name']} | {r['sector']} | {r['bz_end']} | {r['fn_start']} | **{r['gap_days']} días** | **{meses:.1f} meses** |")

md.append("\n---\n")
md.append("## 5. Muestras de Noticias Reales Extraídas\n")
md.append("A continuación se presentan muestras reales de noticias representativas para empresas emblemáticas de cada grupo, demostrando la naturaleza del texto disponible:\n")

sample_tickers = ['NVDA', 'QCOM', 'V', 'CAT', 'MRK', 'COST', 'TSLA', 'AAPL']
for sym in sample_tickers:
    if sym not in cat_map: continue
    comp = cat_map[sym]
    md.append(f"### `{sym}` — {comp['name']} ({comp['sector']})")
    md.append(f"* **Total Noticias Disponibles:** {comp['total_noticias']:,} (Benzinga: {comp['bz_count']:,}, FNSPID: {comp['fn_count']:,})")
    md.append(f"* **Periodo:** {comp['uni_start']} a {comp['uni_end']}")
    if comp['has_bridge_gap']:
        md.append(f"* ⚠️ **Hueco detectado:** {comp['gap_days']} días ({comp['gap_days']/30:.1f} meses)")
    md.append("\n| Fecha | Fuente | Titular de la Noticia | Editor |")
    md.append("| :--- | :---: | :--- | :--- |")
    for s in comp['samples'][:6]:
        md.append(f"| `{s['date'][:10]}` | {s['source']} | {s['headline'][:90]}... | {s['publisher']} |")
    md.append("\n")

md.append("---\n")
md.append("## 6. Recomendaciones para la Configuración Final del Dataset del TFM\n")
md.append("1. **Cesta Principal de Experimentación (Recomendada):** Seleccionar 20 a 30 líderes del **Grupo 1** (como `QCOM`, `ORCL`, `CRM`, `V`, `JPM`, `MRK`, `GILD`, `CAT`, `GE`, `COST`, `COP`). Garantiza 14 años continuos (2009–2023) sin necesidad de imputación ni saltos temporales.")
md.append("2. **Uso de Nvidia / Big Tech:** Si se incluye a `NVDA` o `TSLA`, se recomienda evaluarlas en su ventana reciente continua (agosto 2021 – diciembre 2023), o bien documentar explícitamente en el TFM el salto temporal de 2020-2021.")

content = "\n".join(md)
with open('CATALOGO_EMPRESAS_Y_NOTICIAS.md', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Generated CATALOGO_EMPRESAS_Y_NOTICIAS.md ({len(content)} chars)")
