# Informe de inspección — FNSPID (Zihan1004/FNSPID)

Fecha de inspección: 15/09/2026 · Actualizado: 16/09/2026 (segunda pasada exhaustiva).
Verificado descargando y leyendo datos reales (no documentación).
Repo: https://huggingface.co/datasets/Zihan1004/FNSPID · Paper: arXiv 2402.06698 · Código: github.com/Zdong104/FNSPID_Financial_News_Dataset
**Licencia: CC BY-NC-4.0 — uso comercial prohibido.** Válido para TFM académico; hay que citarlo y declararlo.

## 1. Estructura real del repo (3 ficheros, ~29.5 GB)

| Fichero | Tamaño real (bytes) | Contenido |
|---|---|---|
| `Stock_news/All_external.csv` | 5,731,397,037 (5.7 GB) | Noticias multi-fuente (Benzinga, Reuters, otras). **Heterogéneo** |
| `Stock_news/nasdaq_exteral_data.csv` | 23,232,979,597 (23.2 GB) | Noticias NASDAQ.com con **texto completo** + 4 resúmenes extractivos |
| `Stock_price/full_history.zip` | 589,525,596 (590 MB) | 7,693 CSV, uno por ticker |

Nótese el typo oficial `nasdaq_exteral_data.csv`.

## 2. Esquema de las noticias

`All_external.csv` (11 columnas):
`Date, Article_title, Stock_symbol, Url, Publisher, Author, Article, Lsa_summary, Luhn_summary, Textrank_summary, Lexrank_summary`

`nasdaq_exteral_data.csv` = las mismas 11 + un índice extra sin nombre al principio (12 columnas).

## 3. Estadísticas medidas en muestras

| Métrica | `nasdaq_exteral_data` | `All_external` |
|---|---|---|
| `Article` con texto | **100 %** (bloque muestreado) | varía por bloques (ver §4) |
| Longitud artículo | media 4,194 chars · máx 77,785 | — |
| Resúmenes LSA/Luhn/Textrank/Lexrank | ~100 % llenos | 0 % en bloque 0-200MB |
| `Publisher` / `Author` | **0 %** (vacíos) | contaminado (ver §4) |
| Rango de fechas | 2009-10-07 → 2023-12-16 | 2009-04-29 → 2020-06-10 |
| Orden del fichero | **por ticker** (A→Z, verificado: bloque 200 MB = A..ABM) | **NO uniformemente ordenado** (3,863 tickers distintos en los primeros 200 MB) |
| Duplicados título+fecha | 165 / 7,175 en bloque AAL (2.3 %) | presente |

## 4. ⚠️ Hallazgo A — `All_external.csv` es un collage inconsistente

Sondeando en distintos desplazamientos de bytes:

| Offset | Periodo | `Article` lleno | `Publisher` |
|---|---|---|---|
| 0 MB | 2009-04 → 2020-06 | **0 / 60,000** | contiene *nombres de autor*: "Lisa Levin", "Vick Meyer" |
| 500 MB | 2003-07 → 2004-03 | **14,878 / 14,878** | `Все` (ruso: "todo") |
| 3,000 MB | 2007-02 → 2016-08 | **0 / 225,600** | vacío |
| 4,800 MB | 2006-12 → 2013-11 | **12,743 / 12,744** | vacío |

Además el fichero **no está ordenado por ticker** (a diferencia del nasdaq): en sus primeros 200 MB aparecen ya 3,863 tickers distintos. Parece ordenado por fuente-lote. Cualquier corte por bytes mezcla épocas y emisores.

## 5. ⚠️⚠️ Hallazgo B (AMPLIADO) — los precios provienen de AL MENOS DOS fuentes fusionadas con escalas incompatibles

Auditoría exhaustiva de los **7,693 ficheros completos** (`scripts/audit_precios.py`, resultado en `data/audit_precios.csv`):

| Métrica | Valor |
|---|---|
| Fechas duplicadas | **0** en todo el dataset |
| Tickers con nulos | 147 |
| Tickers con violaciones OHLC (open fuera de high/low, high<low) | **900 (11.7 %)** |
| Tickers con días de volumen = 0 | 3,375 — **1.16 M de filas** |
| `adj close == close` siempre (ni siquiera ajusta dividendos) | 2,645 (34.4 %) |
| Último día = **2023-12-28** | 4,429 tickers |
| Último día = **2020-07-02** (± días vecinos) | **3,163 tickers (41 %)** |
| Tickers que terminan antes de 2023-12-01 | 3,244 |
| Historial < 100 filas | 211 |
| Rango máximo | AA, BA, CVX, DIS desde 1962-01-02 (15,605 filas) |

### B.1 — La costura del 2020-07-06
**364 tickers tienen un salto > 45 % exactamente el 2020-07-06**, primer día tras un hueco de 1 día natural (3-jul era festivo). Los ficheros acaban en 2020-07-02 o continúan desde 2020-07-06: el dataset fusiona una fuente que muere el 2 de julio de 2020 con otra que nace el 6.

### B.2 — Las escalas NO coinciden en la costura
- **AAPL**: cierre 2020-07-02 = 364.11; cierre 2020-07-06 = 93.46. El mercado real ya venía cotizando post-split 4:1 **desde el 2020-06-12** (~94 USD). La fuente antigua siguió publicando precios pre-split ~3 semanas más. El "-74.9 %" no es un split sin ajustar: es **la frontera entre dos fuentes con 3 semanas de solape en escalas distintas**.
- **TSLA**: 2020-07-02 = 1,208.66 → 2020-07-06 = 91.44 (**÷13.2**, volumen ×18). Ningún split de Tesla justifica eso; la escala previa es ~3.3× la real y la posterior ÷4. Su split real (5:1, 31-ago-2020) ni aparece como salto.
- 2,062 tickers tienen además saltos >45 % en otras fechas: mezcla de splits reales sin ajustar, crashes legítimos de microcaps y caídas de delisting.

### B.3 — Las colas muertas NO son todos delistings
**TWTR** acaba el 2020-07-02 (cotó hasta abril-2022), **ABMD** ídem (adquirida en 2022), **ABB** ídem (sigue cotizando). Los 2,351 tickers que mueren el 2020-07-02 tienen **la cola truncada por la fuente**, no por su historia.

### B.4 — Consecuencia para el etiquetado
1. **Solo 4,429 tickers tienen precios hasta dic-2023.** Las noticias llegan hasta dic-2023, pero para ~3,200 tickers no hay precios después de jul-2020: **el universo backtesteable post-2020 son ~4,400 tickers como máximo**, y la intersección con noticias aún menor.
2. Antes de etiquetar dirección hay que: (a) reparar la costura de jul-2020 (detectar el patrón: último día 2020-07-02 + salto en el siguiente), (b) reconstruir splits con ratios casi-enteros (2,3,4,5,6,7,10,20,25,50), (c) tratar 900 ficheros con OHLC inconsistente y 147 con nulos, (d) desconfiar de 1.16 M de filas con volume=0.

## 6. ⚠️ Hallazgo C (CUANTIFICADO con fuente externa) — universos desalineados

Cruzado con el registro oficial **SEC EDGAR** (`company_tickers.json`, 10,422 tickers, descarga 16/09/2026):

| Intersección | Tamaño |
|---|---|
| Precios ∩ SEC | 3,391 → **44.1 %** de los CSV de precios son companies SEC; el 56 % restante son ETFs, preferentes, warrants |
| Noticias(head) ∩ SEC | 1,545 → 40.0 % |
| **Precios ∩ Noticias** | **2,534 → solo el 32.9 % de los tickers con precio tiene noticias** |
| Noticias sin precio | 1,329 |

## 7. ⚠️ Hallazgo D (NUEVO) — el nombre oficial registrales casi nunca es el nombre periodístico

Sobre 1,540 tickers con ≥1 noticia y nombre oficial en SEC: los titulares usan el **nombre legal SEC** solo el **35.4 % de las veces** (media ponderada). 164 tickers (con ≥30 noticias) **nunca** son mencionados por su nombre SEC en ningún titular:

```
ACT   SEC="Enact Holdings, Inc."          → la prensa dice "Enact"
ABX   SEC="Abacus Global Management"      → la prensa dice "Abacus"
API   SEC="Agora, Inc."                   → la prensa dice "Agora" / "GoDaddy" (histórico)
AGQ   SEC="ProShares Trust II"            → la prensa dice "ProShares Silver"
AAC   SEC="Ares Acquisition Corp III"     → SPAC, casi nunca nombrada
```

Consecuencia: un entity linking que compare contra nombres legales (SEC/Wikipedia) falla ~65 % de las veces. Hace falta un **mapa de alias minado del propio corpus** (patrón `Nombre (SYM)`) + marca comercial. Demo de factibilidad: con una regla simple se extrajeron 146–347 nombres estables solo del bloque de 200 MB (`data/name_map*.json`) — AAPL→"Apple", ABBV→"AbbVie", ABM→"ABM Industries".

## 8. ⚠️ Hallazgo E (CONFIRMADO a escala) — el ticker asignado no es la empresa de la noticia

**Microestudio AAL** (7,010 noticias reales, `MICROESTUDIO_AAL.md`, clasificación manual + regex): solo **43 %** son de American Airlines; 6 % robadas por subcadena (`AAL.L`=Anglo American, Air Canada), 7 % macro, 44 % de sector aéreo genérico. Ejemplos auditados a mano: "Anglo's iron ore unit plans to cut 100-plus jobs" → AAL (mina de hierro).

**Extensión multi-ticker** (bloque nasdaq 200 MB = A..ABM, 29,233 filas, verificación automática de mención — `scripts/estudio_longitud.py`):

| Ticker | n | % con mención verificable de la empresa | % sin ninguna pista | % con nombre de OTRA empresa |
|---|---|---|---|---|
| AAL | 6,715 | 23.1 | 38.3 | 38.6 |
| AAPL | 8,865 | 19.1 | 36.1 | 44.8 |
| ABBV | 5,698 | 59.1 | 22.2 | 18.7 |
| AA (Alcoa) | 1,525 | 65.1 | 29.8 | 5.0 |
| A (Agilent) | 379 | 58.6 | 7.9 | 33.5 |

(La columna "otra empresa" es un proxy: artículo que no menciona al ticker-objeto pero sí otra company; incluye sectoriales y erróneas. La auditoría manual de AAL descompone: ~6 % subcadena pura + resto sectorial/macro.)

El agregado por longitud de símbolo no muestra un gradiente limpio — la contaminación no depende de que el ticker sea corto, sino de **colisiones** (`AAL` vs `AAL.L`) y de que el asignador usó búsqueda de texto libre.

## 9. ⚠️ Hallazgo F (CONFIRMADO) — saturación de boilerplate y auto-generado

`scripts/estudio_AAL_2.py`: sobre las 3,010 noticias verdaderas de AAL, **59.7 % son casi-repetidas** (similitud >0.65 con otra previa). Parejas reales: "Goldman Sachs Initiates Coverage on American Airlines at Buy" ← "CRT Capital Initiates Coverage on American Airlines at Buy". Plantillas Zacks/Validea ("AAL Quantitative Stock Analysis") y contenido de opciones repetitivo dominan el volumen.
**Cuidado medido**: la similitud léxica confunde plantillas gemelas de eventos distintos (Barclays vs CRT Capital) — justifica novedad semántica con LLM, no con strings.
Baseline direccional del dataset para AAL: **51.0 % / 49.0 %** (764 sube / 804 baja sobre 1,577 días-empresa) — umbral a batir.

## 10. Timestamps con hora real y hora falsa

Se ven `2023-12-16 23:00:00 UTC` (hora plausible, fuente nasdaq) y `2023-12-05 00:00:00 UTC` (hora perdida, fuente Benzinga/Reuters del collage). Protocolo anti-lookahead: `00:00:00` → "fecha sin hora" → predecir t+1 conservador.

## 11. Decisiones de ingeniería

1. **Fuente primaria de texto: `nasdaq_exteral_data.csv`** (ordenado por ticker → extracción por rangos HTTP viable; ver `scripts/fetch_windows.py` con búsqueda binaria). `All_external.csv` solo aporta titulares multi-fuente y cobertura 2009-2020.
2. **Universo backtesteable: ≤ 4,429 tickers** (los que llegan a dic-2023) ∩ tickers con noticias. Declararlo explícitamente en el plan.
3. **Reparación obligatoria de precios antes de etiquetar**: costura jul-2020, splits por ratios enteros, filtrar los 900 ficheros OHLC-inconsistentes y los 147 con nulos.
4. **Entity linking = alias mining propio** (patrón `(SYM)` del corpus) + verificación de mención con borde de palabra; no fiarse del `Stock_symbol` del dataset ni del nombre SEC.
5. **Novedad semántica (LLM)** obligatoria: la léxica confunde plantillas y no tiene señal direccional (medido: 49.1 % vs 48.4 %).
6. **Split temporal explícito** tras ordenar por fecha; el orden físico del fichero no sirve.

## 13. ⚠️⚠️ Hallazgo G (NUEVO, investigación por rangos HTTP 16/09) — `nasdaq_exteral_data.csv` son DUMPS CONCATENADOS con cobertura por ticker limitada

Mapeando el fichero de 23.2 GB con ~120 sondas de 250 KB (`scripts/dump_map.py`, `data/dump_map.json`):

1. **Cada ticker ocupa un bloque contiguo** (verificado: …TSL→**TSLA**→TSLF…) — extraer un ticker cuesta solo ~26 MB de descarga vía `Range:` (`scripts/fetch_windows.py`). ✔️
2. **PERO cada bloque solo cubre una VENTANA temporal que varía por ticker** — medido descargando bloques reales:

| Ticker | Noticias | Ventana cubierta |
|---|---|---|
| A (Agilent) | 379 | 2009 → 2023 (histórico completo) |
| AAPL | 8,865 | **solo 2022-06 → 2023-12** |
| MSFT | 8,737 | **solo 2022-04 → 2023-12** |
| TSLA | 1,875 | **solo 2019-07 → 2020-06** |

   El fichero es la concatenación de varios dumps anuales/creeper: un ticker puede tener histórico completo o solo 11-18 meses según cuándo lo capturó cada dump. **Obliga a auditar la ventana temporal ticker a ticker antes de entrenar** (ni train/test ni cobertura son homogéneos).
3. **Después de ~17.5 GB el fichero cambia de naturaleza**: frontier alfabética (YGYIP→APC), luego una zona de ~5 GB (≈22 %) donde el `Stock_symbol` está VACÍO y el contenido es de fuentes heterogéneas: **noticias en RUSO de lenta.ru**, Reuters genéricos ("FACTBOX-U.S. military fatalities…"), Bloomberg sin ticker… y filas Benzinga con URL de benzinga.com. Es decir: el fichero "nasdaq" contiene ~5 GB de noticias macro/exóticas sin asignar — utilizables como **feed macro** (¡justo lo que tu clasificador específico-vs-macro necesita!), pero no son noticias de empresa.
4. En la zona sin ticker también viven las noticias de mercado general que en el microestudio AAL clasificamos como "macro" — su origen queda explicado.

Implicaciones: (a) extraer el texto completo de cualquier ticker es barato (búsqueda binaria + 1 rango HTTP); (b) el perfil de cobertura temporal debe medirse por ticker (plan: script que sondee el bloque de cada ticker y registre su rango de fechas); (c) el paper del dataset no documenta nada de esto.

## 14. Impacto en la narrativa del TFM

Capítulo "Data quality audit of FNSPID" con números propios y reproducibles:
- 56 % de ficheros de precios sin validar contra SEC (ETFs/warrants) — hay que filtrar
- **41 % de tickers con la serie truncada en jul-2020** (colisiona con noticias hasta 2023)
- 2 escalas incompatibles fusionadas + 364 saltos-frontera fechados idénticamente
- ≤33 % de tickers tienen noticias; 43 % de precisión de ticker en AAL (auditoría manual)
- nombre oficial SEC usado solo 35 % del tiempo → necesidad de mapa de alias
- 60 % casi-duplicados; baseline 51 % → la aportación (memoria temporal + novedad semántica + entity linking) está justificada empíricamente

## Anexo — artefactos reproducibles

```
data/audit_precios.csv              auditoría 7,693 ficheros de precios
data/sec_tickers.json               registro oficial SEC (10,422)
data/sec_nombre_vs_uso.csv          nombre SEC vs nombre periodístico, 1,540 tickers
data/estudio_AAL_clasificadas.csv   7,010 noticias AAL clasificadas
data/estudio_AAL_verdaderas.csv     3,010 limpias + novedad
data/estudio_AAL_dias.csv           1,577 días-empresa etiquetados
data/longitud_tickers.csv           verificación de mención multi-ticker
data/name_map*.json                 mapa ticker→nombre minado del corpus
scripts/{fetch_windows,estudio_AAL,estudio_AAL_2,estudio_longitud,entity_mining,sec_cross,audit_precios}.py
```
