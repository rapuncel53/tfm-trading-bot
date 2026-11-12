# Estudio Exhaustivo de Fechas de Noticias — 199 Empresas Tier 1 Gold (S&P 500)

**Fecha de análisis:** 2026-09-20 18:52:07 · **Universo:** 202 acciones con precios limpios hasta dic-2023

## 1. Conclusiones Principales y Origen de las Fechas

### ¿Por qué las noticias más antiguas del dump de NASDAQ empiezan en octubre de 2009 y no en 1999?
1. **Límite del portal web NASDAQ.com:** El archivo `nasdaq_exteral_data.csv` (23.2 GB con texto completo y resúmenes) proviene de un raspado (scraping) del archivo digital de **NASDAQ.com**, el cual comenzó a almacenar artículos periodísticos completos a partir de **octubre de 2009**. La web de NASDAQ no conserva textos de noticias anteriores a esa fecha.
2. **El caso de Accenture (`ACN`):** En 1999 la empresa aún formaba parte de Arthur Andersen bajo el nombre *Andersen Consulting*. Se renombró a *Accenture* el 1 de enero de 2001 y comenzó a cotizar en bolsa el **19 de julio de 2001**. Sus noticias en el dump comienzan el **01 de diciembre de 2009** y llegan hasta el **16 de diciembre de 2023** (14 años continuos de noticias).
3. **Fecha de cierre uniforme (d1_news):** Para prácticamente todas las empresas analizadas, las noticias terminan a mediados de **diciembre de 2023** (coincidiendo con el cierre del dataset FNSPID).

## 2. Distribución de Empresas por Perfil de Cobertura Temporal

| Perfil Temporal | Nº Empresas | % Tier 1 | Noticias Medias Estimadas | Ejemplos Representativos |
|---|---|---|---|---|
| **Histórico Ultra-Largo (2009-2012 -> 2023, 11-14 años)** | **137** | 68.8% | ~1,744 | `ACGL, ACN, AEE, AEP, AES, AIZ` |
| **Histórico Largo (2013-2019 -> 2023, 5-10 años)** | **33** | 16.6% | ~1,588 | `ALLE, ANET, APTV, ARES, BA, BKNG` |
| **Ventana Reciente (2022-2023, 1-2 años)** | **24** | 12.1% | ~130 | `AAPL, AMZN, AVGO, AWK, AZO, DAL` |
| **Ventana Intermedia (2020-2021 -> 2023, 3-4 años)** | **5** | 2.5% | ~755 | `CARR, NCLH, NVDA, PSX, VRT` |

## 3. Distribución del Año de Inicio de Noticias (d0_news)

| Año de Inicio (d0) | Nº Empresas | Tickers |
|---|---|---|
| **2009** | **34** | `ACN, AEE, AEP, AKAM, AMT, BSX, CAT, CMG ... (+26 más)` |
| **2010** | **75** | `ACGL, AES, ALL, APA, ARE, BG, BIIB, BR ... (+67 más)` |
| **2011** | **14** | `ALGN, APH, BLDR, CHTR, HCA, HSIC, INCY, KIM ... (+6 más)` |
| **2012** | **14** | `AIZ, APO, ATO, BNY, CSGP, ERIE, EXR, FANG ... (+6 más)` |
| **2013** | **4** | `ALLE, DOC, TMUS, VEEV` |
| **2014** | **5** | `ANET, ARES, C, CFG, LDOS` |
| **2015** | **5** | `GDDY, HPE, KHC, ON, PYPL` |
| **2016** | **1** | `FTV` |
| **2017** | **5** | `APTV, CVNA, INTC, TPR, VST` |
| **2018** | **4** | `BA, BKNG, GS, WMT` |
| **2019** | **9** | `BKR, CRWD, CTVA, DDOG, DOW, FOX, FOXA, LHX ... (+1 más)` |
| **2020** | **3** | `CARR, PSX, VRT` |
| **2021** | **2** | `NCLH, NVDA` |
| **2022** | **5** | `AAPL, DAL, MSFT, REG, TSLA` |
| **2023** | **19** | `AMZN, AVGO, AWK, AZO, F, GM, GOOG, HIG ... (+11 más)` |

## 4. Tabla Completa de las 202 Empresas Tier 1 Gold

| Ticker | Empresa | Sector | Inicio Noticias (d0) | Fin Noticias (d1) | Años Cubiertos | Noticias Estimadas | Tamaño Bloque |
|---|---|---|---|---|---|---|---|
| **CHTR** | CHARTER COMMUNICATIONS, INC. / | Communication Services | 2011-05-02 | 2023-12-16 | 12.6 | ~2,187 | 13.12 MB |
| **FOX** | Fox Corp | Communication Services | 2019-06-05 | 2023-12-16 | 4.5 | ~338 | 2.03 MB |
| **FOXA** | Fox Corp | Communication Services | 2019-05-24 | 2023-12-16 | 4.6 | ~859 | 5.16 MB |
| **GOOG** | Alphabet Inc. | Communication Services | 2023-01-10 | 2023-12-16 | 0.9 | ~2,916 | 17.5 MB |
| **LYV** | Live Nation Entertainment, Inc | Communication Services | 2023-12-16 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **NWS** | NEWS CORP | Communication Services | 2009-11-25 | 2023-11-13 | 14.0 | ~442 | 2.66 MB |
| **NWSA** | NEWS CORP | Communication Services | 2010-04-27 | 2023-12-13 | 13.6 | ~1,223 | 7.34 MB |
| **TMUS** | T-Mobile US, Inc. | Communication Services | 2013-05-01 | 2023-12-16 | 10.6 | ~5,000 | 30.0 MB |
| **TTWO** | TAKE TWO INTERACTIVE SOFTWARE  | Communication Services | 2010-05-26 | 2023-12-16 | 13.6 | ~3,072 | 18.44 MB |
| **AMZN** | AMAZON COM INC | Consumer Discretionary | 2023-03-09 | 2023-12-16 | 0.8 | ~4,782 | 52.0 MB |
| **APTV** | Aptiv PLC | Consumer Discretionary | 2017-12-06 | 2023-12-16 | 6.0 | ~833 | 5.0 MB |
| **AZO** | AUTOZONE INC | Consumer Discretionary | 2023-12-12 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **BKNG** | Booking Holdings Inc. | Consumer Discretionary | 2018-02-27 | 2023-12-16 | 5.8 | ~2,682 | 16.09 MB |
| **CMG** | CHIPOTLE MEXICAN GRILL INC | Consumer Discretionary | 2009-10-16 | 2023-12-16 | 14.2 | ~6,354 | 38.12 MB |
| **CVNA** | CARVANA CO. | Consumer Discretionary | 2017-04-13 | 2023-12-15 | 6.7 | ~1,562 | 9.38 MB |
| **DPZ** | DOMINOS PIZZA INC | Consumer Discretionary | 2010-05-04 | 2023-12-16 | 13.6 | ~3,229 | 19.38 MB |
| **DRI** | DARDEN RESTAURANTS INC | Consumer Discretionary | 2009-11-23 | 2023-12-13 | 14.1 | ~2,890 | 17.34 MB |
| **EBAY** | EBAY INC | Consumer Discretionary | 2009-10-15 | 2023-12-16 | 14.2 | ~5,260 | 31.56 MB |
| **EXPE** | Expedia Group, Inc. | Consumer Discretionary | 2010-04-28 | 2023-12-15 | 13.6 | ~2,968 | 17.81 MB |
| **F** | FORD MOTOR CO | Consumer Discretionary | 2023-06-09 | 2023-12-16 | 0.5 | ~1,458 | 8.75 MB |
| **GM** | General Motors Co | Consumer Discretionary | 2023-11-30 | 2023-12-16 | 0.0 | ~109 | 0.62 MB |
| **GRMN** | GARMIN LTD | Consumer Discretionary | 2010-02-17 | 2023-12-16 | 13.8 | ~1,640 | 9.84 MB |
| **NCLH** | Norwegian Cruise Line Holdings | Consumer Discretionary | 2021-12-02 | 2023-12-16 | 2.0 | ~755 | 4.53 MB |
| **NVR** | NVR INC | Consumer Discretionary | 2010-03-11 | 2023-12-15 | 13.8 | ~1,250 | 7.5 MB |
| **ORLY** | O REILLY AUTOMOTIVE INC | Consumer Discretionary | 2010-05-20 | 2023-12-16 | 13.6 | ~1,614 | 9.69 MB |
| **RCL** | ROYAL CARIBBEAN CRUISES LTD | Consumer Discretionary | 2023-11-15 | 2023-12-15 | 0.1 | ~130 | 0.78 MB |
| **RL** | RALPH LAUREN CORP | Consumer Discretionary | 2010-04-19 | 2023-12-14 | 13.7 | ~1,927 | 11.56 MB |
| **TPR** | TAPESTRY, INC. | Consumer Discretionary | 2017-11-06 | 2023-12-13 | 6.1 | ~1,276 | 7.66 MB |
| **TSCO** | TRACTOR SUPPLY CO /DE/ | Consumer Discretionary | 2010-08-11 | 2023-12-16 | 13.3 | ~2,317 | 13.91 MB |
| **TSLA** | Tesla, Inc. | Consumer Discretionary | 2022-05-02 | 2023-12-16 | 1.6 | ~8,712 | 78.0 MB |
| **ULTA** | Ulta Beauty, Inc. | Consumer Discretionary | 2011-06-08 | 2023-12-16 | 12.5 | ~3,203 | 19.22 MB |
| **BG** | Bunge Global SA | Consumer Staples | 2010-02-04 | 2023-12-16 | 13.9 | ~1,119 | 6.72 MB |
| **CASY** | CASEYS GENERAL STORES INC | Consumer Staples | 2010-06-02 | 2023-12-16 | 13.5 | ~1,484 | 8.91 MB |
| **COST** | COSTCO WHOLESALE CORP /NEW | Consumer Staples | 2010-02-17 | 2023-12-16 | 13.8 | ~6,781 | 78.0 MB |
| **DLTR** | DOLLAR TREE, INC. | Consumer Staples | 2010-05-20 | 2023-12-12 | 13.6 | ~2,968 | 17.81 MB |
| **KHC** | Kraft Heinz Co | Consumer Staples | 2015-07-08 | 2023-12-16 | 8.4 | ~2,760 | 16.56 MB |
| **SYY** | SYSCO CORP | Consumer Staples | 2010-02-25 | 2023-12-16 | 13.8 | ~1,875 | 11.25 MB |
| **WMT** | Walmart Inc. | Consumer Staples | 2018-12-01 | 2023-12-16 | 5.0 | ~8,675 | 78.0 MB |
| **APA** | APA Corp | Energy | 2010-02-10 | 2023-12-15 | 13.8 | ~2,708 | 16.25 MB |
| **BKR** | Baker Hughes Co | Energy | 2019-10-23 | 2023-12-16 | 4.1 | ~2,630 | 15.78 MB |
| **COP** | CONOCOPHILLIPS | Energy | 2009-11-17 | 2023-12-16 | 14.1 | ~5,989 | 35.94 MB |
| **EOG** | EOG RESOURCES INC | Energy | 2009-12-15 | 2023-12-16 | 14.0 | ~3,515 | 21.09 MB |
| **FANG** | Diamondback Energy, Inc. | Energy | 2012-10-02 | 2023-12-16 | 11.2 | ~2,031 | 12.19 MB |
| **OXY** | OCCIDENTAL PETROLEUM CORP /DE/ | Energy | 2009-11-11 | 2023-12-16 | 14.1 | ~4,791 | 28.75 MB |
| **PSX** | Phillips 66 | Energy | 2020-04-29 | 2023-12-16 | 3.6 | ~1,640 | 9.84 MB |
| **TRGP** | Targa Resources Corp. | Energy | 2012-08-03 | 2023-12-16 | 11.4 | ~781 | 4.69 MB |
| **VLO** | VALERO ENERGY CORP/TX | Energy | 2009-10-09 | 2023-12-16 | 14.2 | ~3,020 | 18.12 MB |
| **XOM** | ExxonMobil Holdings Corp | Energy | 2019-08-25 | 2023-12-16 | 4.3 | ~6,757 | 52.0 MB |
| **ACGL** | ARCH CAPITAL GROUP LTD. | Financials | 2010-06-01 | 2023-12-16 | 13.5 | ~1,536 | 9.22 MB |
| **AIZ** | ASSURANT, INC. | Financials | 2012-06-27 | 2023-12-16 | 11.5 | ~1,197 | 7.19 MB |
| **ALL** | ALLSTATE CORP | Financials | 2010-01-05 | 2023-12-15 | 13.9 | ~1,796 | 10.78 MB |
| **APO** | Apollo Global Management, Inc. | Financials | 2012-03-14 | 2023-12-16 | 11.8 | ~1,588 | 9.53 MB |
| **ARES** | Ares Management Corp | Financials | 2014-04-28 | 2023-12-16 | 9.6 | ~598 | 3.59 MB |
| **BNY** | Bank of New York Mellon Corp | Financials | 2012-04-06 | 2023-06-05 | 11.2 | ~59 | 0.31 MB |
| **BX** | Blackstone Inc. | Financials | 2010-02-22 | 2023-12-16 | 13.8 | ~3,437 | 20.62 MB |
| **C** | CITIGROUP INC | Financials | 2014-11-09 | 2023-12-16 | 9.1 | ~7,656 | 45.94 MB |
| **CBOE** | Cboe Global Markets, Inc. | Financials | 2010-04-27 | 2023-12-16 | 13.6 | ~1,927 | 11.56 MB |
| **CFG** | CITIZENS FINANCIAL GROUP INC/R | Financials | 2014-09-08 | 2023-12-16 | 9.3 | ~1,510 | 9.06 MB |
| **CME** | CME GROUP INC. | Financials | 2010-04-11 | 2023-12-16 | 13.7 | ~2,187 | 13.12 MB |
| **COF** | CAPITAL ONE FINANCIAL CORP | Financials | 2010-04-23 | 2023-12-15 | 13.6 | ~2,369 | 14.22 MB |
| **ERIE** | ERIE INDEMNITY CO | Financials | 2012-05-31 | 2023-12-12 | 11.5 | ~286 | 1.72 MB |
| **FDS** | FACTSET RESEARCH SYSTEMS INC | Financials | 2009-12-18 | 2023-12-16 | 14.0 | ~1,015 | 6.09 MB |
| **FIS** | Fidelity National Information  | Financials | 2010-03-21 | 2023-12-14 | 13.7 | ~1,119 | 6.72 MB |
| **GPN** | GLOBAL PAYMENTS INC | Financials | 2010-04-20 | 2023-12-12 | 13.6 | ~1,197 | 7.19 MB |
| **GS** | GOLDMAN SACHS GROUP INC | Financials | 2018-11-14 | 2023-12-16 | 5.1 | ~7,083 | 42.5 MB |
| **HIG** | HARTFORD INSURANCE GROUP, INC. | Financials | 2023-02-02 | 2023-12-15 | 0.9 | ~1,692 | 10.16 MB |
| **IBKR** | Interactive Brokers Group, Inc | Financials | 2023-12-11 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **ICE** | Intercontinental Exchange, Inc | Financials | 2009-12-08 | 2023-12-16 | 14.0 | ~1,770 | 10.62 MB |
| **KEY** | KEYCORP /NEW/ | Financials | 2010-04-14 | 2023-12-16 | 13.7 | ~1,718 | 10.31 MB |
| **KKR** | KKR & Co. Inc. | Financials | 2010-05-19 | 2023-12-16 | 13.6 | ~2,109 | 12.66 MB |
| **MSCI** | MSCI Inc. | Financials | 2011-08-16 | 2023-12-16 | 12.3 | ~963 | 5.78 MB |
| **NDAQ** | NASDAQ, INC. | Financials | 2010-04-26 | 2023-12-14 | 13.6 | ~1,796 | 10.78 MB |
| **PFG** | PRINCIPAL FINANCIAL GROUP INC | Financials | 2010-04-09 | 2023-12-05 | 13.7 | ~963 | 5.78 MB |
| **PRU** | PRUDENTIAL FINANCIAL INC | Financials | 2010-01-05 | 2023-12-12 | 13.9 | ~2,109 | 12.66 MB |
| **PYPL** | PayPal Holdings, Inc. | Financials | 2015-07-20 | 2023-12-16 | 8.4 | ~8,541 | 51.25 MB |
| **USB** | US BANCORP \DE\ | Financials | 2009-12-28 | 2023-12-16 | 14.0 | ~3,333 | 20.0 MB |
| **V** | VISA INC. | Financials | 2010-04-15 | 2023-12-16 | 13.7 | ~6,945 | 52.0 MB |
| **ALGN** | ALIGN TECHNOLOGY INC | Health Care | 2011-08-01 | 2023-12-16 | 12.4 | ~2,786 | 16.72 MB |
| **BIIB** | BIOGEN INC. | Health Care | 2010-02-09 | 2023-12-16 | 13.8 | ~5,208 | 31.25 MB |
| **BSX** | BOSTON SCIENTIFIC CORP | Health Care | 2009-12-16 | 2023-12-16 | 14.0 | ~2,421 | 14.53 MB |
| **CI** | Cigna Group | Health Care | 2010-02-04 | 2023-12-16 | 13.9 | ~2,890 | 17.34 MB |
| **COR** | Cencora, Inc. | Health Care | 2010-06-23 | 2023-12-16 | 13.5 | ~677 | 4.06 MB |
| **CRL** | CHARLES RIVER LABORATORIES INT | Health Care | 2010-10-11 | 2023-12-16 | 13.2 | ~885 | 5.31 MB |
| **DGX** | QUEST DIAGNOSTICS INC | Health Care | 2010-03-29 | 2023-12-16 | 13.7 | ~1,354 | 8.12 MB |
| **DVA** | DAVITA INC. | Health Care | 2010-08-04 | 2023-12-16 | 13.4 | ~1,614 | 9.69 MB |
| **DXCM** | DEXCOM INC | Health Care | 2010-11-05 | 2023-12-16 | 13.1 | ~2,031 | 12.19 MB |
| **EW** | Edwards Lifesciences Corp | Health Care | 2010-09-10 | 2023-12-16 | 13.3 | ~2,083 | 12.5 MB |
| **GILD** | GILEAD SCIENCES, INC. | Health Care | 2009-10-14 | 2023-12-16 | 14.2 | ~8,932 | 53.59 MB |
| **HCA** | HCA Healthcare, Inc. | Health Care | 2011-04-04 | 2023-12-16 | 12.7 | ~1,822 | 10.94 MB |
| **HSIC** | HENRY SCHEIN INC | Health Care | 2011-08-16 | 2023-12-16 | 12.3 | ~1,510 | 9.06 MB |
| **HUM** | HUMANA INC | Health Care | 2009-12-22 | 2023-12-16 | 14.0 | ~2,864 | 17.19 MB |
| **INCY** | INCYTE CORP | Health Care | 2011-07-21 | 2023-12-13 | 12.4 | ~1,692 | 10.16 MB |
| **LH** | LABCORP HOLDINGS INC. | Health Care | 2023-11-23 | 2023-12-16 | 0.1 | ~26 | 0.16 MB |
| **MRK** | Merck & Co., Inc. | Health Care | 2009-11-04 | 2023-12-16 | 14.1 | ~8,593 | 51.56 MB |
| **MTD** | METTLER TOLEDO INTERNATIONAL I | Health Care | 2011-11-28 | 2023-12-16 | 12.0 | ~442 | 2.66 MB |
| **PODD** | INSULET CORP | Health Care | 2010-05-07 | 2023-12-16 | 13.6 | ~989 | 5.94 MB |
| **REGN** | REGENERON PHARMACEUTICALS, INC | Health Care | 2023-08-28 | 2023-12-16 | 0.3 | ~156 | 0.94 MB |
| **RMD** | RESMED INC | Health Care | 2010-07-12 | 2023-12-11 | 13.4 | ~1,119 | 6.72 MB |
| **VEEV** | VEEVA SYSTEMS INC | Health Care | 2013-10-03 | 2023-12-16 | 10.2 | ~2,031 | 12.19 MB |
| **VRTX** | VERTEX PHARMACEUTICALS INC / M | Health Care | 2010-07-20 | 2023-12-16 | 13.4 | ~4,088 | 24.53 MB |
| **WAT** | WATERS CORP /DE/ | Health Care | 2010-04-20 | 2023-12-13 | 13.6 | ~625 | 3.75 MB |
| **ALLE** | Allegion plc | Industrials | 2013-12-16 | 2023-12-16 | 10.0 | ~885 | 5.31 MB |
| **BA** | BOEING CO | Industrials | 2018-05-24 | 2023-12-16 | 5.6 | ~6,065 | 52.0 MB |
| **BLDR** | Builders FirstSource, Inc. | Industrials | 2011-06-15 | 2023-12-16 | 12.5 | ~1,223 | 7.34 MB |
| **BR** | BROADRIDGE FINANCIAL SOLUTIONS | Industrials | 2010-04-20 | 2023-12-16 | 13.7 | ~1,041 | 6.25 MB |
| **CARR** | CARRIER GLOBAL Corp | Industrials | 2020-04-03 | 2023-12-16 | 3.7 | ~755 | 4.53 MB |
| **CAT** | CATERPILLAR INC | Industrials | 2009-11-04 | 2023-12-16 | 14.1 | ~5,185 | 52.0 MB |
| **CHRW** | C. H. ROBINSON WORLDWIDE, INC. | Industrials | 2010-07-31 | 2023-12-11 | 13.4 | ~1,223 | 7.34 MB |
| **CPRT** | COPART INC | Industrials | 2010-12-16 | 2023-12-15 | 13.0 | ~885 | 5.31 MB |
| **CSX** | CSX CORP | Industrials | 2010-04-15 | 2023-12-16 | 13.7 | ~2,526 | 15.16 MB |
| **DAL** | DELTA AIR LINES, INC. | Industrials | 2022-11-22 | 2023-12-16 | 1.1 | ~1,302 | 7.81 MB |
| **FDX** | FEDEX CORP | Industrials | 2010-05-20 | 2023-12-16 | 13.6 | ~5,234 | 31.41 MB |
| **FIX** | COMFORT SYSTEMS USA INC | Industrials | 2012-01-31 | 2023-12-13 | 11.9 | ~625 | 3.75 MB |
| **FTV** | Fortive Corp | Industrials | 2016-07-25 | 2023-12-12 | 7.4 | ~625 | 3.75 MB |
| **GE** | GENERAL ELECTRIC CO | Industrials | 2012-04-20 | 2023-12-16 | 11.7 | ~9,921 | 59.53 MB |
| **GNRC** | GENERAC HOLDINGS INC. | Industrials | 2010-02-11 | 2023-12-12 | 13.8 | ~859 | 5.16 MB |
| **LDOS** | Leidos Holdings, Inc. | Industrials | 2014-03-27 | 2023-12-16 | 9.7 | ~1,093 | 6.56 MB |
| **LHX** | L3HARRIS TECHNOLOGIES, INC. /D | Industrials | 2019-07-05 | 2023-12-16 | 4.4 | ~703 | 4.22 MB |
| **LII** | LENNOX INTERNATIONAL INC | Industrials | 2023-12-05 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **NOC** | NORTHROP GRUMMAN CORP /DE/ | Industrials | 2010-03-09 | 2023-12-16 | 13.8 | ~4,166 | 25.0 MB |
| **NSC** | NORFOLK SOUTHERN CORP | Industrials | 2009-11-03 | 2023-12-16 | 14.1 | ~2,109 | 12.66 MB |
| **PNR** | PENTAIR plc | Industrials | 2010-02-25 | 2023-12-12 | 13.8 | ~807 | 4.84 MB |
| **PWR** | QUANTA SERVICES, INC. | Industrials | 2010-09-27 | 2023-12-16 | 13.2 | ~1,145 | 6.88 MB |
| **ROK** | ROCKWELL AUTOMATION, INC | Industrials | 2009-11-03 | 2023-12-16 | 14.1 | ~1,093 | 6.56 MB |
| **RSG** | REPUBLIC SERVICES, INC. | Industrials | 2009-11-17 | 2023-12-14 | 14.1 | ~1,093 | 6.56 MB |
| **UBER** | Uber Technologies, Inc | Industrials | 2023-02-08 | 2023-12-16 | 0.9 | ~1,015 | 6.09 MB |
| **UNP** | UNION PACIFIC CORP | Industrials | 2009-11-03 | 2023-12-16 | 14.1 | ~3,177 | 19.06 MB |
| **UPS** | UNITED PARCEL SERVICE INC | Industrials | 2009-11-20 | 2023-12-16 | 14.1 | ~4,427 | 26.56 MB |
| **URI** | UNITED RENTALS, INC. | Industrials | 2011-01-14 | 2023-12-16 | 12.9 | ~1,822 | 10.94 MB |
| **VRSK** | Verisk Analytics, Inc. | Industrials | 2009-10-19 | 2023-12-16 | 14.2 | ~807 | 4.84 MB |
| **VRT** | Vertiv Holdings Co | Industrials | 2020-05-12 | 2023-12-15 | 3.6 | ~390 | 2.34 MB |
| **WAB** | WESTINGHOUSE AIR BRAKE TECHNOL | Industrials | 2011-07-28 | 2023-12-16 | 12.4 | ~781 | 4.69 MB |
| **XYL** | Xylem Inc. | Industrials | 2012-11-30 | 2023-12-13 | 11.0 | ~885 | 5.31 MB |
| **AAPL** | Apple Inc. | Information Technology | 2022-06-03 | 2023-12-16 | 1.5 | ~8,865 | 78.0 MB |
| **ACN** | Accenture plc | Information Technology | 2009-12-01 | 2023-12-16 | 14.0 | ~3,151 | 18.91 MB |
| **AKAM** | AKAMAI TECHNOLOGIES INC | Information Technology | 2009-11-06 | 2023-12-15 | 14.1 | ~1,770 | 10.62 MB |
| **ANET** | Arista Networks, Inc. | Information Technology | 2014-05-28 | 2023-12-16 | 9.6 | ~3,255 | 19.53 MB |
| **APH** | AMPHENOL CORP /DE/ | Information Technology | 2011-02-02 | 2023-12-16 | 12.9 | ~937 | 5.62 MB |
| **AVGO** | Broadcom Inc. | Information Technology | 2023-12-16 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **CIEN** | CIENA CORP | Information Technology | 2010-02-25 | 2023-12-16 | 13.8 | ~1,197 | 7.19 MB |
| **CRM** | Salesforce, Inc. | Information Technology | 2009-12-14 | 2023-12-16 | 14.0 | ~6,105 | 52.0 MB |
| **CRWD** | CrowdStrike Holdings, Inc. | Information Technology | 2019-06-06 | 2023-12-16 | 4.5 | ~3,385 | 20.31 MB |
| **CTSH** | COGNIZANT TECHNOLOGY SOLUTIONS | Information Technology | 2009-11-22 | 2023-12-14 | 14.1 | ~1,432 | 8.59 MB |
| **DDOG** | Datadog, Inc. | Information Technology | 2019-09-18 | 2023-12-16 | 4.2 | ~1,588 | 9.53 MB |
| **DELL** | Dell Technologies Inc. | Information Technology | 2009-10-26 | 2023-12-16 | 14.1 | ~2,083 | 12.5 MB |
| **FFIV** | F5, INC. | Information Technology | 2010-03-18 | 2023-12-07 | 13.7 | ~1,093 | 6.56 MB |
| **FLEX** | FLEX LTD. | Information Technology | 2010-06-01 | 2023-12-16 | 13.5 | ~781 | 4.69 MB |
| **FSLR** | FIRST SOLAR, INC. | Information Technology | 2010-01-09 | 2023-12-16 | 13.9 | ~3,880 | 23.28 MB |
| **FTNT** | Fortinet, Inc. | Information Technology | 2010-11-01 | 2023-12-16 | 13.1 | ~2,161 | 12.97 MB |
| **GDDY** | GoDaddy Inc. | Information Technology | 2015-03-19 | 2023-12-16 | 8.7 | ~729 | 4.38 MB |
| **HPE** | Hewlett Packard Enterprise Co | Information Technology | 2015-11-03 | 2023-12-16 | 8.1 | ~2,135 | 12.81 MB |
| **HPQ** | HP INC | Information Technology | 2009-10-14 | 2023-12-16 | 14.2 | ~4,635 | 27.81 MB |
| **IBM** | INTERNATIONAL BUSINESS MACHINE | Information Technology | 2023-12-16 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **INTC** | INTEL CORP | Information Technology | 2017-12-26 | 2023-12-16 | 6.0 | ~8,682 | 78.0 MB |
| **MPWR** | MONOLITHIC POWER SYSTEMS, INC. | Information Technology | 2010-12-13 | 2023-12-16 | 13.0 | ~729 | 4.38 MB |
| **MRVL** | Marvell Technology, Inc. | Information Technology | 2010-02-18 | 2023-12-12 | 13.8 | ~2,187 | 13.12 MB |
| **MSFT** | MICROSOFT CORP | Information Technology | 2022-04-26 | 2023-12-16 | 1.6 | ~8,737 | 78.0 MB |
| **NOW** | ServiceNow, Inc. | Information Technology | 2011-05-12 | 2023-12-16 | 12.6 | ~1,953 | 11.72 MB |
| **NTAP** | NetApp, Inc. | Information Technology | 2010-04-15 | 2023-12-15 | 13.7 | ~1,744 | 10.47 MB |
| **NVDA** | NVIDIA CORP | Information Technology | 2021-08-17 | 2023-12-16 | 2.3 | ~8,716 | 104.0 MB |
| **ON** | ON SEMICONDUCTOR CORP | Information Technology | 2015-04-14 | 2023-12-15 | 8.7 | ~1,822 | 10.94 MB |
| **ORCL** | ORACLE CORP | Information Technology | 2009-11-22 | 2023-12-16 | 14.1 | ~5,291 | 52.0 MB |
| **PANW** | Palo Alto Networks Inc | Information Technology | 2012-07-17 | 2023-12-16 | 11.4 | ~3,567 | 21.41 MB |
| **QCOM** | QUALCOMM INC/DE | Information Technology | 2010-02-01 | 2023-12-16 | 13.9 | ~7,031 | 42.19 MB |
| **ROP** | ROPER TECHNOLOGIES INC | Information Technology | 2010-08-18 | 2023-12-16 | 13.3 | ~1,119 | 6.72 MB |
| **SWKS** | SKYWORKS SOLUTIONS, INC. | Information Technology | 2010-03-08 | 2023-12-12 | 13.8 | ~1,979 | 11.88 MB |
| **VRSN** | VERISIGN INC/CA | Information Technology | 2010-04-15 | 2023-12-16 | 13.7 | ~598 | 3.59 MB |
| **WDAY** | Workday, Inc. | Information Technology | 2012-10-01 | 2023-12-16 | 11.2 | ~1,901 | 11.41 MB |
| **CTVA** | Corteva, Inc. | Materials | 2019-06-06 | 2023-12-16 | 4.5 | ~703 | 4.22 MB |
| **DOW** | DOW INC. | Materials | 2019-05-24 | 2023-12-16 | 4.6 | ~1,250 | 7.5 MB |
| **LIN** | LINDE PLC | Materials | 2023-12-14 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **LYB** | LyondellBasell Industries N.V. | Materials | 2023-12-11 | 2023-12-16 | 0.0 | ~26 | 0.16 MB |
| **PKG** | PACKAGING CORP OF AMERICA | Materials | 2010-04-20 | 2023-12-16 | 13.7 | ~1,067 | 6.41 MB |
| **AMT** | AMERICAN TOWER CORP /MA/ | Real Estate | 2009-12-02 | 2023-12-16 | 14.0 | ~4,843 | 29.06 MB |
| **ARE** | ALEXANDRIA REAL ESTATE EQUITIE | Real Estate | 2010-04-26 | 2023-12-16 | 13.6 | ~1,197 | 7.19 MB |
| **BXP** | BXP, Inc. | Real Estate | 2010-04-19 | 2023-12-16 | 13.7 | ~1,067 | 6.41 MB |
| **CCI** | CROWN CASTLE INC. | Real Estate | 2010-02-23 | 2023-12-16 | 13.8 | ~1,744 | 10.47 MB |
| **CPT** | CAMDEN PROPERTY TRUST | Real Estate | 2010-09-26 | 2023-12-12 | 13.2 | ~651 | 3.91 MB |
| **CSGP** | COSTAR GROUP, INC. | Real Estate | 2012-04-12 | 2023-12-13 | 11.7 | ~677 | 4.06 MB |
| **DOC** | HEALTHPEAK PROPERTIES, INC. | Real Estate | 2013-07-05 | 2023-12-14 | 10.4 | ~468 | 2.81 MB |
| **ESS** | ESSEX PROPERTY TRUST, INC. | Real Estate | 2009-11-06 | 2023-12-16 | 14.1 | ~885 | 5.31 MB |
| **EXR** | Extra Space Storage Inc. | Real Estate | 2012-01-04 | 2023-12-14 | 11.9 | ~1,067 | 6.41 MB |
| **FRT** | FEDERAL REALTY INVESTMENT TRUS | Real Estate | 2010-02-25 | 2023-12-12 | 13.8 | ~963 | 5.78 MB |
| **KIM** | KIMCO REALTY CORP | Real Estate | 2011-02-11 | 2023-12-14 | 12.8 | ~1,067 | 6.41 MB |
| **PLD** | Prologis, Inc. | Real Estate | 2010-06-24 | 2023-12-16 | 13.5 | ~2,135 | 12.81 MB |
| **PSA** | Public Storage | Real Estate | 2010-05-03 | 2023-12-14 | 13.6 | ~1,953 | 11.72 MB |
| **REG** | REGENCY CENTERS CORP | Real Estate | 2022-11-28 | 2023-12-15 | 1.0 | ~130 | 0.78 MB |
| **VICI** | VICI PROPERTIES INC. | Real Estate | 2023-05-18 | 2023-12-12 | 0.6 | ~1,067 | 6.41 MB |
| **VTR** | Ventas, Inc. | Real Estate | 2009-11-23 | 2023-12-14 | 14.1 | ~1,223 | 7.34 MB |
| **WY** | WEYERHAEUSER CO | Real Estate | 2010-07-12 | 2023-12-01 | 13.4 | ~1,145 | 6.88 MB |
| **AEE** | AMEREN CORP | Utilities | 2009-10-27 | 2023-12-16 | 14.1 | ~1,276 | 7.66 MB |
| **AEP** | AMERICAN ELECTRIC POWER CO INC | Utilities | 2009-10-09 | 2023-12-16 | 14.2 | ~1,953 | 11.72 MB |
| **AES** | AES CORP | Utilities | 2010-06-07 | 2023-12-16 | 13.5 | ~1,223 | 7.34 MB |
| **ATO** | ATMOS ENERGY CORP | Utilities | 2012-02-22 | 2023-12-16 | 11.8 | ~989 | 5.94 MB |
| **AWK** | American Water Works Company,  | Utilities | 2023-12-12 | 2023-12-15 | 0.0 | ~26 | 0.16 MB |
| **CNP** | CENTERPOINT ENERGY INC | Utilities | 2010-02-19 | 2023-12-16 | 13.8 | ~1,197 | 7.19 MB |
| **NRG** | NRG ENERGY, INC. | Utilities | 2010-02-17 | 2023-12-16 | 13.8 | ~1,588 | 9.53 MB |
| **PEG** | PUBLIC SERVICE ENTERPRISE GROU | Utilities | 2010-01-04 | 2023-12-14 | 13.9 | ~1,614 | 9.69 MB |
| **VST** | Vistra Corp. | Utilities | 2017-05-19 | 2023-12-14 | 6.6 | ~598 | 3.59 MB |
