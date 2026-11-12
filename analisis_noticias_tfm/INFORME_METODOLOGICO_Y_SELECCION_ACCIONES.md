# Informe Metodológico y Selección de Acciones para Re-entrenamiento

Este dossier documenta la estructura, auditoría forense y selección de acciones a partir de los dos datasets de noticias financieras del TFM: **Benzinga News Feed** y **FNSPID (NASDAQ)**.

Todos los entregables, documentos Excel y scripts reproducibles se encuentran organizados dentro de esta carpeta (`analisis_noticias_tfm/`).

---

## 1. Mapa de Entregables en esta Carpeta

| Fichero | Formato | Descripción |
| :--- | :---: | :--- |
| [`1_cobertura_noticias_todas_las_acciones.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.xlsx) | Excel (`.xlsx`) | **Documento Maestro Acción por Acción (207 empresas):** Detalla de qué fecha a qué fecha hay noticias, a qué dataset pertenecen (Benzinga, FNSPID o Ambos), desglose de noticias y días por split (Train, Val, Test) y clasificación en Tiers. |
| [`1_cobertura_noticias_todas_las_acciones.csv`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.csv) | CSV plano | Versión en texto plano compatible con scripts y pipelines en Python / Pandas. |
| [`2_mejores_acciones_seleccionadas_entrenamiento.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.xlsx) | Excel (`.xlsx`) | **Documento de Acciones de Élite para Re-entrenamiento (36 empresas Tier 1):** Acciones con flujo ininterrumpido en Train, Val y Test, ordenadas por volumen, representatividad sectorial y ajuste óptimo al patrón de Machine Learning ~70% / 10% / 20%. |
| [`2_mejores_acciones_seleccionadas_entrenamiento.csv`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.csv) | CSV plano | Versión en texto plano para alimentar directamente el entrenamiento multimodal. |
| [`mapa_temporal_noticias_por_compania.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/mapa_temporal_noticias_por_compania.png) | Gráfico Gantt | Línea de tiempo visual continua que muestra de qué fecha a qué fecha cubre cada dataset por acción. |
| [`distribucion_optimizada_70_10_20.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/distribucion_optimizada_70_10_20.png) | Gráfico Barras | Comparativa del reparto temporal de las acciones seleccionadas frente al ideal 70/10/20. |
| [`presentacion_noticias_tfm.pptx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/presentacion_noticias_tfm.pptx) | PowerPoint | Diapositivas ejecutivas para la reunión de seguimiento con el tutor. |

---

## 2. Scripts Disponibles en `analisis_noticias_tfm/scripts/`

Todos los scripts son ejecutables y reproducibles con el entorno virtual del proyecto:

1. **`01_generar_excel_todas_las_acciones.py`:**
   - Lee las particiones temporales (`data/splits/`) y los metadatos de Benzinga y FNSPID.
   - Genera [`1_cobertura_noticias_todas_las_acciones.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.xlsx) y su `.csv`.
   - *Comando:* `.venv\Scripts\python.exe analisis_noticias_tfm/scripts/01_generar_excel_todas_las_acciones.py`

2. **`02_generar_excel_mejores_acciones.py`:**
   - Lee el Documento 1, filtra las compañías continuas en los tres splits (Train, Val, Test), calcula la métrica de ajuste al 70/10/20 y genera [`2_mejores_acciones_seleccionadas_entrenamiento.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.xlsx).
   - *Comando:* `.venv\Scripts\python.exe analisis_noticias_tfm/scripts/02_generar_excel_mejores_acciones.py`

3. **`03_auditoria_fnspid.py`:**
   - Auditoría exhaustiva del dataset FNSPID: esquema, nulos, longitudes de texto, resúmenes LSA/Luhn/TextRank/LexRank y fechas de 199 empresas del S&P 500.
   - *Comando:* `.venv\Scripts\python.exe analisis_noticias_tfm/scripts/03_auditoria_fnspid.py`

4. **`04_auditoria_benzinga.py`:**
   - Auditoría exhaustiva de los 1.4 millones de registros de Benzinga: distribución horaria (97.2% en pre-market), 6.204 tickers, editores y fechas de 2009 a 2020.
   - *Comando:* `.venv\Scripts\python.exe analisis_noticias_tfm/scripts/04_auditoria_benzinga.py`

5. **`05_auditoria_duplicados_y_solape.py`:**
   - Detección de duplicados exactos, sindicación multi-ticker y solape cruzado entre Benzinga y FNSPID.
   - *Comando:* `.venv\Scripts\python.exe analisis_noticias_tfm/scripts/05_auditoria_duplicados_y_solape.py`

---

## 3. Resumen del Documento 1: Cobertura de las 207 Acciones

Al cruzar Benzinga (2009–2020) y FNSPID (2009–2023), el universo de 207 compañías se clasifica objetivamente en:

- **Tier 1: Cobertura Total Continua (36 empresas):** Cuentan con un flujo ininterrumpido de noticias tanto en Train como en Val y Test.
- **Tier 2: Cobertura Parcial Histórica (116 empresas):** Excelente historial en Benzinga (2009–2020) que cubre Train y Val, pero FNSPID no descargó sus artículos en el volcado reciente (2021–2023).
- **Tier 2: Cobertura Parcial Tardía (25 empresas):** Gigantes como Apple (`AAPL`), Microsoft (`MSFT`), Amazon (`AMZN`) o Tesla (`TSLA`) que concentran miles de noticias entre 2021 y 2023 pero carecen de flujo inicial en Train.
- **Tier 3: Silenciosas (30 empresas):** Acciones de sectores regulados (como utilities e inmobiliarias) que cuentan con todos sus precios y balances contables SEC 10-Q/10-K, pero casi nunca emiten alertas en los medios financieros.

---

## 4. Resumen del Documento 2: Selección de Acciones de Élite para el Nuevo Entrenamiento

Para que un modelo de Deep Learning / LLM aprenda de forma consistente y generalice sin sesgos temporales, se exige que las acciones seleccionadas cumplan dos principios:
1. **Presencia simultánea en Train, Validación y Test:** Para poder calibrar los pesos del LLM en el pasado, validar la parada temprana (*early stopping*) durante el shock del COVID y evaluar la rentabilidad en el régimen actual de tipos altos.
2. **Proporción temporal equilibrada:** Que la mayor parte del texto resida en Train (~60%–75%), una fracción en Val (~10%–15%) y una fracción en Test (~20%–30%).

### Top 15 Acciones de Élite Seleccionadas (Documento 2):

| Rank | Ticker | Empresa | Sector GICS | Total Días | % Train | % Val | % Test | Score Idoneidad |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **ORCL** | Oracle Corp. | Information Technology | 2.250 | 68,0% | 10,7% | 21,3% | **96,0 / 100** |
| **2** | **CAT** | Caterpillar Inc. | Industrials | 2.155 | 65,0% | 13,4% | 21,6% | **91,4 / 100** |
| **3** | **EBAY** | eBay Inc. | Consumer Discretionary | 1.563 | 59,9% | 16,5% | 23,6% | **84,8 / 100** |
| **4** | **V** | Visa Inc. | Financials | 2.147 | 60,1% | 13,9% | 26,0% | **84,2 / 100** |
| **5** | **COST** | Costco Wholesale | Consumer Staples | 2.019 | 59,1% | 13,4% | 27,5% | **83,7 / 100** |
| **6** | **KO** | The Coca-Cola Co. | Consumer Staples | 2.240 | 62,4% | 13,3% | 24,4% | **81,2 / 100** |
| **7** | **CRM** | Salesforce, Inc. | Information Technology | 1.930 | 55,6% | 15,8% | 28,7% | **78,3 / 100** |
| **8** | **GILD** | Gilead Sciences | Health Care | 1.730 | 52,9% | 20,1% | 27,0% | **76,1 / 100** |
| **9** | **QCOM** | Qualcomm Inc. | Information Technology | 1.804 | 51,8% | 18,2% | 30,0% | **74,5 / 100** |
| **10** | **NVDA** | NVIDIA Corp. | Information Technology | 1.710 | 49,8% | 16,0% | 34,2% | **71,7 / 100** |
| **11** | **BIIB** | Biogen Inc. | Health Care | 1.323 | 50,1% | 18,4% | 31,4% | **70,4 / 100** |
| **12** | **ADBE** | Adobe Inc. | Information Technology | 1.576 | 49,2% | 17,7% | 33,1% | **60,8 / 100** |
| **13** | **REGN** | Regeneron Pharma | Health Care | 892 | 62,7% | 31,5% | 5,8% | **60,2 / 100** |
| **14** | **CSX** | CSX Corp. | Industrials | 1.117 | 44,9% | 25,3% | 29,8% | **60,1 / 100** |
| **15** | **DLTR** | Dollar Tree, Inc. | Consumer Staples | 1.084 | 44,4% | 23,0% | 32,7% | **59,7 / 100** |

---

## 5. Justificación Metodológica para la Defensa del TFM

1. **Por qué no entrenar con Microsoft (`MSFT`) o Apple (`AAPL`):**
   - Como se demuestra en el Documento 1, `MSFT` tiene **0 días de noticias en Train** (2011–2018) y **0 días en Validación**. Solo aparece en el Test (2022–2023 con 8.737 noticias). Si se incluyera en Train, el modelo sufriría un sesgo de representación masivo; por el contrario, en Test sirve como evaluación *out-of-sample* o *zero-shot*.
2. **Complementariedad Híbrida Benzinga + FNSPID:**
   - **Train y Val (2011 a Junio 2020):** Alimentados por Benzinga con alertas operativas en Pre-Market (97.2% publicadas antes de las 09:00 EDT), garantizando cero sesgo de anticipación (*look-ahead bias*).
   - **Embargo de 14 Meses (Junio 2020 a Agosto 2021):** Zona de cuarentena que aísla las distorsiones de los estímulos post-COVID y absorbe el desfase entre fuentes.
   - **Test Ciego (Agosto 2021 a Diciembre 2023):** Alimentado por FNSPID NASDAQ bajo un nuevo régimen macroeconómico de inflación y subidas de tipos de interés de la Reserva Federal.
