# Inventario y Censo Global de Tickers en FNSPID (Fase 1)

**Fecha:** 2026-09-20 13:23:24 · **Total tickers evaluados:** 7,693

## 1. Resumen Ejecutivo del Universo Global (7,693 Tickers)

| Clasificación / Tier | Nº Tickers | % del Total | Descripción |
|---|---|---|---|
| **DESCARTADO_COSTURA_2020** | **3,244** | 42.2% | Truncados por la costura del 2020-07-02 o con fin antes de dic-2023 |
| **TIER_2_SEC_PENDIENTE_NOTICIAS** | **1,895** | 24.6% | Empresa SEC fuera de S&P 500 con precios limpios hasta 2023 |
| **DESCARTADO_NO_OPERATIVO_SEC** | **1,660** | 21.6% | ETFs, warrants, preferentes o notas no registradas como empresa operativa |
| **DESCARTADO_ANOMALIA_OHLC** | **630** | 8.2% | Inconsistencias físicas en precios (High < Low o Open fuera de rango) |
| **TIER_1_SP500_GOLD** | **202** | 2.6% | S&P 500 con precios limpios hasta dic-2023 y noticias verificadas en FNSPID |
| **DESCARTADO_NULOS** | **49** | 0.6% | Presencia de valores nulos o corruptos en precios |
| **TIER_1_SP500_SIN_NOTICIAS** | **11** | 0.1% | S&P 500 con precios limpios pero sin noticias en el dump nasdaq |
| **DESCARTADO_POCO_HISTORIAL** | **2** | 0.0% | Historial de cotización insuficiente (< 500 días) |

## 2. Anatomía del Índice S&P 500 en FNSPID (503 Tickers Oficiales)

- **Encontrados en el dataset de precios:** 448 de 503 (89.1%)
- **Con precios limpios hasta dic-2023:** 213 (47.5% de los presentes)
- **TIER 1 GOLD (Precios limpios + Noticias confirmadas):** **202 tickers**

### Desglose de bajas en el S&P 500:
- **Truncados por la costura de julio 2020:** 92 tickers
- **Violaciones de OHLC:** 158 tickers
- **Nulos en precios:** 37 tickers

## 3. Distribución Sectorial del Tier 1 S&P 500 Gold

| Sector GICS | Nº Tickers Tier 1 | Tickers de muestra |
|---|---|---|
| **Information Technology** | 36 | `AAPL, ACN, AKAM, ANET, APH` |
| **Industrials** | 33 | `ALLE, BA, BLDR, BR, CARR` |
| **Financials** | 29 | `ACGL, AIZ, ALL, APO, ARES` |
| **Health Care** | 24 | `ALGN, BIIB, BSX, CI, COR` |
| **Consumer Discretionary** | 22 | `AMZN, APTV, AZO, BKNG, CMG` |
| **Real Estate** | 17 | `AMT, ARE, BXP, CCI, CPT` |
| **Energy** | 10 | `APA, BKR, COP, EOG, FANG` |
| **Utilities** | 9 | `AEE, AEP, AES, ATO, AWK` |
| **Communication Services** | 9 | `CHTR, FOX, FOXA, GOOG, LYV` |
| **Consumer Staples** | 7 | `BG, CASY, COST, DLTR, KHC` |
| **Materials** | 6 | `CF, CTVA, DOW, LIN, LYB` |

## 4. Tickers Tier 1 S&P 500 Gold (Candidatos Óptimos para el TFM)

| Ticker | Empresa | Sector | Días Cotizados | Ventana Noticias (Sondeo) | Muestra Noticias |
|---|---|---|---|---|---|
| **CHTR** | CHARTER COMMUNICATIONS, INC. /MO/ | Communication Services | 3,520 | 2021-11-12 -> 2023-12-16 | 495 |
| **FOX** | Fox Corp | Communication Services | 1,209 | 2019-06-05 -> 2023-12-16 | 313 |
| **FOXA** | Fox Corp | Communication Services | 1,210 | 2021-11-07 -> 2023-12-16 | 487 |
| **GOOG** | Alphabet Inc. | Communication Services | 4,874 | 2023-10-23 -> 2023-12-16 | 409 |
| **LYV** | Live Nation Entertainment, Inc. | Communication Services | 4,535 | 2023-12-16 -> 2023-12-16 | 7 |
| **NWS** | NEWS CORP | Communication Services | 2,651 | 2009-11-25 -> 2023-11-13 | 510 |
| **NWSA** | NEWS CORP | Communication Services | 2,651 | 2019-08-19 -> 2023-12-13 | 498 |
| **TMUS** | T-Mobile US, Inc. | Communication Services | 4,204 | 2023-04-27 -> 2023-12-16 | 426 |
| **TTWO** | TAKE TWO INTERACTIVE SOFTWARE INC | Communication Services | 6,722 | 2022-08-08 -> 2023-12-16 | 452 |
| **AMZN** | AMAZON COM INC | Consumer Discretionary | 6,700 | 2023-03-09 -> 2023-12-16 | 4782 |
| **APTV** | Aptiv PLC | Consumer Discretionary | 3,047 | 2020-06-10 -> 2023-12-16 | 431 |
| **AZO** | AUTOZONE INC | Consumer Discretionary | 8,249 | 2023-12-12 -> 2023-12-16 | 7 |
| **BKNG** | Booking Holdings Inc. | Consumer Discretionary | 6,228 | 2023-04-29 -> 2023-12-16 | 453 |
| **CMG** | CHIPOTLE MEXICAN GRILL INC | Consumer Discretionary | 4,512 | 2023-05-30 -> 2023-12-16 | 430 |
| **CVNA** | CARVANA CO. | Consumer Discretionary | 1,679 | 2023-02-21 -> 2023-12-15 | 480 |
| **DPZ** | DOMINOS PIZZA INC | Consumer Discretionary | 4,901 | 2022-12-29 -> 2023-12-16 | 431 |
| **DRI** | DARDEN RESTAURANTS INC | Consumer Discretionary | 7,211 | 2021-11-01 -> 2023-12-13 | 441 |
| **EBAY** | EBAY INC | Consumer Discretionary | 6,357 | 2022-08-10 -> 2023-12-16 | 411 |
| **EXPE** | Expedia Group, Inc. | Consumer Discretionary | 4,642 | 2022-03-01 -> 2023-12-15 | 414 |
| **F** | FORD MOTOR CO | Consumer Discretionary | 13,006 | 2023-10-02 -> 2023-12-16 | 468 |
| **GM** | General Motors Co | Consumer Discretionary | 3,299 | 2023-11-30 -> 2023-12-16 | 109 |
| **GRMN** | GARMIN LTD | Consumer Discretionary | 5,799 | 2020-10-28 -> 2023-12-16 | 439 |
| **NCLH** | Norwegian Cruise Line Holdings Ltd. | Consumer Discretionary | 2,755 | 2022-06-30 -> 2023-12-16 | 431 |
| **NVR** | NVR INC | Consumer Discretionary | 9,688 | 2021-05-21 -> 2023-12-15 | 372 |
| **ORLY** | O REILLY AUTOMOTIVE INC | Consumer Discretionary | 7,727 | 2021-06-18 -> 2023-12-16 | 443 |
| **RCL** | ROYAL CARIBBEAN CRUISES LTD | Consumer Discretionary | 7,724 | 2023-11-15 -> 2023-12-15 | 89 |
| **RL** | RALPH LAUREN CORP | Consumer Discretionary | 6,681 | 2022-02-09 -> 2023-12-14 | 455 |
| **TPR** | TAPESTRY, INC. | Consumer Discretionary | 5,843 | 2022-02-10 -> 2023-12-13 | 479 |
| **TSCO** | TRACTOR SUPPLY CO /DE/ | Consumer Discretionary | 7,518 | 2022-10-14 -> 2023-12-16 | 473 |
| **TSLA** | Tesla, Inc. | Consumer Discretionary | 3,399 | 2022-05-02 -> 2023-12-16 | 8712 |
| **ULTA** | Ulta Beauty, Inc. | Consumer Discretionary | 4,072 | 2023-02-07 -> 2023-12-16 | 436 |
| **BG** | Bunge Global SA | Consumer Staples | 5,637 | 2021-09-01 -> 2023-12-16 | 478 |
| **CASY** | CASEYS GENERAL STORES INC | Consumer Staples | 10,130 | 2022-06-08 -> 2023-12-16 | 390 |
| **COST** | COSTCO WHOLESALE CORP /NEW | Consumer Staples | 9,445 | 2010-02-17 -> 2023-12-16 | 6781 |
| **DLTR** | DOLLAR TREE, INC. | Consumer Staples | 7,255 | 2022-09-06 -> 2023-12-12 | 444 |
| **KHC** | Kraft Heinz Co | Consumer Staples | 2,137 | 2023-01-26 -> 2023-12-16 | 478 |
| **SYY** | SYSCO CORP | Consumer Staples | 12,773 | 2022-04-28 -> 2023-12-16 | 432 |
| **WMT** | Walmart Inc. | Consumer Staples | 12,946 | 2018-12-01 -> 2023-12-16 | 8675 |
| **APA** | APA Corp | Energy | 11,252 | 2022-05-23 -> 2023-12-15 | 470 |
| **BKR** | Baker Hughes Co | Energy | 9,257 | 2023-06-29 -> 2023-12-16 | 391 |
| **COP** | CONOCOPHILLIPS | Energy | 10,587 | 2023-04-21 -> 2023-12-16 | 452 |
| **EOG** | EOG RESOURCES INC | Energy | 8,625 | 2022-12-23 -> 2023-12-16 | 429 |
| **FANG** | Diamondback Energy, Inc. | Energy | 2,820 | 2022-10-13 -> 2023-12-16 | 449 |
| **OXY** | OCCIDENTAL PETROLEUM CORP /DE/ | Energy | 10,587 | 2023-06-23 -> 2023-12-16 | 415 |
| **PSX** | Phillips 66 | Energy | 2,948 | 2023-01-19 -> 2023-12-16 | 431 |
| **TRGP** | Targa Resources Corp. | Energy | 3,287 | 2019-01-29 -> 2023-12-16 | 418 |
| **VLO** | VALERO ENERGY CORP/TX | Energy | 10,586 | 2023-02-16 -> 2023-12-16 | 463 |
| **XOM** | ExxonMobil Holdings Corp | Energy | 13,618 | 2019-08-25 -> 2023-12-16 | 6757 |
| **ACGL** | ARCH CAPITAL GROUP LTD. | Financials | 7,122 | 2022-05-08 -> 2023-12-16 | 431 |
| **AIZ** | ASSURANT, INC. | Financials | 5,009 | 2020-11-03 -> 2023-12-16 | 422 |
| **ALL** | ALLSTATE CORP | Financials | 7,699 | 2021-05-27 -> 2023-12-15 | 458 |
| **APO** | Apollo Global Management, Inc. | Financials | 3,209 | 2022-02-04 -> 2023-12-16 | 532 |
| **ARES** | Ares Management Corp | Financials | 2,432 | 2017-03-15 -> 2023-12-16 | 421 |
| **BNY** | Bank of New York Mellon Corp | Financials | 5,641 | 2012-04-06 -> 2023-06-05 | 59 |
| **BX** | Blackstone Inc. | Financials | 4,159 | 2023-02-28 -> 2023-12-16 | 529 |
| **C** | CITIGROUP INC | Financials | 11,849 | 2022-09-28 -> 2023-12-16 | 483 |
| **CBOE** | Cboe Global Markets, Inc. | Financials | 3,409 | 2022-06-02 -> 2023-12-16 | 352 |
| **CFG** | CITIZENS FINANCIAL GROUP INC/RI | Financials | 2,332 | 2022-02-25 -> 2023-12-16 | 464 |
| **CME** | CME GROUP INC. | Financials | 5,301 | 2022-04-26 -> 2023-12-16 | 445 |
| **COF** | CAPITAL ONE FINANCIAL CORP | Financials | 7,330 | 2022-05-12 -> 2023-12-15 | 416 |
| **ERIE** | ERIE INDEMNITY CO | Financials | 7,110 | 2012-05-31 -> 2023-12-12 | 280 |
| **FDS** | FACTSET RESEARCH SYSTEMS INC | Financials | 6,922 | 2018-12-18 -> 2023-12-16 | 419 |
| **FIS** | Fidelity National Information Servi | Financials | 5,667 | 2020-10-30 -> 2023-12-14 | 431 |
| **GPN** | GLOBAL PAYMENTS INC | Financials | 5,775 | 2020-05-29 -> 2023-12-12 | 468 |
| **GS** | GOLDMAN SACHS GROUP INC | Financials | 6,205 | 2023-08-25 -> 2023-12-16 | 538 |
| **HIG** | HARTFORD INSURANCE GROUP, INC. | Financials | 7,057 | 2020-11-12 -> 2023-12-15 | 434 |
| **IBKR** | Interactive Brokers Group, Inc. | Financials | 4,193 | 2023-12-11 -> 2023-12-16 | 7 |
| **ICE** | Intercontinental Exchange, Inc. | Financials | 4,559 | 2021-12-28 -> 2023-12-16 | 454 |
| **KEY** | KEYCORP /NEW/ | Financials | 9,108 | 2022-04-21 -> 2023-12-16 | 481 |
| **KKR** | KKR & Co. Inc. | Financials | 3,388 | 2022-07-21 -> 2023-12-16 | 607 |
| **MSCI** | MSCI Inc. | Financials | 4,057 | 2021-01-07 -> 2023-12-16 | 398 |
| **NDAQ** | NASDAQ, INC. | Financials | 5,412 | 2022-01-25 -> 2023-12-14 | 450 |
| **PFG** | PRINCIPAL FINANCIAL GROUP INC | Financials | 5,584 | 2019-01-29 -> 2023-12-05 | 400 |
| **PRU** | PRUDENTIAL FINANCIAL INC | Financials | 5,548 | 2022-04-01 -> 2023-12-12 | 430 |
| **PYPL** | PayPal Holdings, Inc. | Financials | 2,137 | 2023-08-21 -> 2023-12-16 | 425 |
| **USB** | US BANCORP \DE\ | Financials | 12,776 | 2023-02-27 -> 2023-12-16 | 483 |
| **V** | VISA INC. | Financials | 3,973 | 2010-04-15 -> 2023-12-16 | 6945 |
| **ALGN** | ALIGN TECHNOLOGY INC | Health Care | 5,765 | 2022-07-01 -> 2023-12-16 | 450 |
| **BIIB** | BIOGEN INC. | Health Care | 8,132 | 2023-01-15 -> 2023-12-16 | 483 |
| **BSX** | BOSTON SCIENTIFIC CORP | Health Care | 7,962 | 2023-01-04 -> 2023-12-16 | 440 |
| **CI** | Cigna Group | Health Care | 10,525 | 2022-11-09 -> 2023-12-16 | 451 |
| **COR** | Cencora, Inc. | Health Care | 7,235 | 2016-06-13 -> 2023-12-16 | 449 |
| **CRL** | CHARLES RIVER LABORATORIES INTERNAT | Health Care | 5,916 | 2018-06-13 -> 2023-12-16 | 362 |
| **DGX** | QUEST DIAGNOSTICS INC | Health Care | 6,803 | 2021-04-05 -> 2023-12-16 | 419 |
| **DVA** | DAVITA INC. | Health Care | 7,089 | 2022-10-05 -> 2023-12-16 | 400 |
| **DXCM** | DEXCOM INC | Health Care | 4,710 | 2023-06-11 -> 2023-12-16 | 411 |
| **EW** | Edwards Lifesciences Corp | Health Care | 5,978 | 2022-01-27 -> 2023-12-16 | 399 |
| **GILD** | GILEAD SCIENCES, INC. | Health Care | 8,044 | 2023-02-09 -> 2023-12-16 | 440 |
| **HCA** | HCA Healthcare, Inc. | Health Care | 3,223 | 2022-06-21 -> 2023-12-16 | 398 |
| **HSIC** | HENRY SCHEIN INC | Health Care | 7,086 | 2022-03-09 -> 2023-12-16 | 431 |
| **HUM** | HUMANA INC | Health Care | 10,587 | 2022-11-11 -> 2023-12-16 | 491 |
| **INCY** | INCYTE CORP | Health Care | 7,591 | 2020-08-04 -> 2023-12-13 | 420 |
| **LH** | LABCORP HOLDINGS INC. | Health Care | 8,503 | 2023-11-23 -> 2023-12-16 | 7 |
| **MRK** | Merck & Co., Inc. | Health Care | 13,618 | 2023-07-06 -> 2023-12-16 | 438 |
| **MTD** | METTLER TOLEDO INTERNATIONAL INC/ | Health Care | 6,572 | 2011-11-28 -> 2023-12-16 | 344 |
| **PODD** | INSULET CORP | Health Care | 4,186 | 2022-01-28 -> 2023-12-16 | 418 |
| **REGN** | REGENERON PHARMACEUTICALS, INC. | Health Care | 8,249 | 2023-08-28 -> 2023-12-16 | 118 |
| **RMD** | RESMED INC | Health Care | 7,194 | 2020-01-30 -> 2023-12-11 | 347 |
| **VEEV** | VEEVA SYSTEMS INC | Health Care | 2,568 | 2022-05-27 -> 2023-12-16 | 397 |
| **VRTX** | VERTEX PHARMACEUTICALS INC / MA | Health Care | 8,170 | 2023-05-03 -> 2023-12-16 | 411 |
| **WAT** | WATERS CORP /DE/ | Health Care | 7,076 | 2016-10-19 -> 2023-12-13 | 393 |
| **ALLE** | Allegion plc | Industrials | 2,545 | 2019-12-01 -> 2023-12-16 | 420 |
| **BA** | BOEING CO | Industrials | 15,605 | 2018-05-24 -> 2023-12-16 | 6065 |
| **BLDR** | Builders FirstSource, Inc. | Industrials | 4,658 | 2022-09-05 -> 2023-12-16 | 427 |
| **BR** | BROADRIDGE FINANCIAL SOLUTIONS, INC | Industrials | 4,223 | 2018-12-21 -> 2023-12-16 | 430 |
| **CARR** | CARRIER GLOBAL Corp | Industrials | 1,002 | 2021-05-01 -> 2023-12-16 | 505 |
| **CAT** | CATERPILLAR INC | Industrials | 13,618 | 2009-11-04 -> 2023-12-16 | 5185 |
| **CHRW** | C. H. ROBINSON WORLDWIDE, INC. | Industrials | 6,593 | 2020-07-29 -> 2023-12-11 | 448 |
| **CPRT** | COPART INC | Industrials | 7,499 | 2019-03-26 -> 2023-12-15 | 348 |
| **CSX** | CSX CORP | Industrials | 10,879 | 2022-05-20 -> 2023-12-16 | 523 |
| **DAL** | DELTA AIR LINES, INC. | Industrials | 4,194 | 2023-07-24 -> 2023-12-16 | 436 |
| **FDX** | FEDEX CORP | Industrials | 11,528 | 2023-05-02 -> 2023-12-16 | 418 |
| **FIX** | COMFORT SYSTEMS USA INC | Industrials | 6,670 | 2015-12-10 -> 2023-12-13 | 390 |
| **FTV** | Fortive Corp | Industrials | 1,885 | 2018-02-12 -> 2023-12-12 | 403 |
| **GE** | GENERAL ELECTRIC CO | Industrials | 15,605 | 2023-05-01 -> 2023-12-16 | 463 |
| **GNRC** | GENERAC HOLDINGS INC. | Industrials | 3,494 | 2020-12-15 -> 2023-12-12 | 486 |
| **LDOS** | Leidos Holdings, Inc. | Industrials | 4,329 | 2019-07-30 -> 2023-12-16 | 433 |
| **LHX** | L3HARRIS TECHNOLOGIES, INC. /DE/ | Industrials | 10,587 | 2021-08-03 -> 2023-12-16 | 451 |
| **LII** | LENNOX INTERNATIONAL INC | Industrials | 6,145 | 2023-12-05 -> 2023-12-16 | 7 |
| **NOC** | NORTHROP GRUMMAN CORP /DE/ | Industrials | 10,587 | 2023-03-24 -> 2023-12-16 | 422 |
| **NSC** | NORFOLK SOUTHERN CORP | Industrials | 10,482 | 2022-06-29 -> 2023-12-16 | 446 |
| **OTIS** | Otis Worldwide Corp | Industrials | 952 | 2022-05-26 -> 2023-12-15 | 182 |
| **PNR** | PENTAIR plc | Industrials | 12,776 | 2018-12-11 -> 2023-12-12 | 358 |
| **PWR** | QUANTA SERVICES, INC. | Industrials | 6,512 | 2020-08-06 -> 2023-12-16 | 415 |
| **ROK** | ROCKWELL AUTOMATION, INC | Industrials | 10,587 | 2019-11-14 -> 2023-12-16 | 419 |
| **RSG** | REPUBLIC SERVICES, INC. | Industrials | 6,416 | 2019-10-30 -> 2023-12-14 | 501 |
| **UBER** | Uber Technologies, Inc | Industrials | 1,168 | 2023-07-31 -> 2023-12-16 | 470 |
| **UNP** | UNION PACIFIC CORP | Industrials | 11,092 | 2022-12-13 -> 2023-12-16 | 456 |
| **UPS** | UNITED PARCEL SERVICE INC | Industrials | 6,072 | 2023-05-08 -> 2023-12-16 | 445 |
| **URI** | UNITED RENTALS, INC. | Industrials | 6,549 | 2022-08-24 -> 2023-12-16 | 424 |
| **VRSK** | Verisk Analytics, Inc. | Industrials | 3,581 | 2019-02-19 -> 2023-12-16 | 401 |
| **VRT** | Vertiv Holdings Co | Industrials | 1,943 | 2020-05-12 -> 2023-12-15 | 331 |
| **WAB** | WESTINGHOUSE AIR BRAKE TECHNOLOGIES | Industrials | 7,184 | 2019-02-16 -> 2023-12-16 | 445 |
| **XYL** | Xylem Inc. | Industrials | 3,072 | 2019-07-11 -> 2023-12-13 | 376 |
| **AAPL** | Apple Inc. | Information Technology | 10,852 | 2022-06-03 -> 2023-12-16 | 8865 |
| **ACN** | Accenture plc | Information Technology | 5,647 | 2022-11-15 -> 2023-12-16 | 527 |
| **AKAM** | AKAMAI TECHNOLOGIES INC | Information Technology | 6,080 | 2021-12-14 -> 2023-12-15 | 417 |
| **ANET** | Arista Networks, Inc. | Information Technology | 2,408 | 2023-08-10 -> 2023-12-16 | 392 |
| **APH** | AMPHENOL CORP /DE/ | Information Technology | 8,094 | 2018-10-08 -> 2023-12-16 | 424 |
| **AVGO** | Broadcom Inc. | Information Technology | 3,624 | 2023-12-16 -> 2023-12-16 | 7 |
| **CIEN** | CIENA CORP | Information Technology | 6,767 | 2020-03-13 -> 2023-12-16 | 404 |
| **CRM** | Salesforce, Inc. | Information Technology | 4,914 | 2009-12-14 -> 2023-12-16 | 6105 |
| **CRWD** | CrowdStrike Holdings, Inc. | Information Technology | 1,146 | 2023-08-08 -> 2023-12-16 | 426 |
| **CTSH** | COGNIZANT TECHNOLOGY SOLUTIONS CORP | Information Technology | 6,424 | 2020-07-24 -> 2023-12-14 | 381 |
| **DDOG** | Datadog, Inc. | Information Technology | 1,077 | 2023-01-26 -> 2023-12-16 | 455 |
| **DELL** | Dell Technologies Inc. | Information Technology | 1,854 | 2022-10-05 -> 2023-12-16 | 477 |
| **FFIV** | F5, INC. | Information Technology | 6,183 | 2019-10-23 -> 2023-12-07 | 392 |
| **FLEX** | FLEX LTD. | Information Technology | 7,498 | 2019-02-01 -> 2023-12-16 | 412 |
| **FSLR** | FIRST SOLAR, INC. | Information Technology | 4,306 | 2023-03-03 -> 2023-12-16 | 483 |
| **FTNT** | Fortinet, Inc. | Information Technology | 3,551 | 2023-02-06 -> 2023-12-16 | 429 |
| **GDDY** | GoDaddy Inc. | Information Technology | 2,203 | 2018-08-15 -> 2023-12-16 | 391 |
| **HPE** | Hewlett Packard Enterprise Co | Information Technology | 2,063 | 2022-03-31 -> 2023-12-16 | 446 |
| **HPQ** | HP INC | Information Technology | 15,605 | 2022-09-02 -> 2023-12-16 | 464 |
| **IBM** | INTERNATIONAL BUSINESS MACHINES COR | Information Technology | 15,605 | 2023-12-16 -> 2023-12-16 | 7 |
| **INTC** | INTEL CORP | Information Technology | 11,040 | 2017-12-26 -> 2023-12-16 | 8682 |
| **LITE** | Lumentum Holdings Inc. | Information Technology | 2,124 | 2023-12-06 -> 2023-12-16 | 7 |
| **MPWR** | MONOLITHIC POWER SYSTEMS, INC. | Information Technology | 4,809 | 2020-04-29 -> 2023-12-16 | 420 |
| **MRVL** | Marvell Technology, Inc. | Information Technology | 5,911 | 2022-12-29 -> 2023-12-12 | 428 |
| **MSFT** | MICROSOFT CORP | Information Technology | 9,526 | 2022-04-26 -> 2023-12-16 | 8737 |
| **NOW** | ServiceNow, Inc. | Information Technology | 2,893 | 2023-04-11 -> 2023-12-16 | 469 |
| **NTAP** | NetApp, Inc. | Information Technology | 7,074 | 2020-08-27 -> 2023-12-15 | 465 |
| **NVDA** | NVIDIA CORP | Information Technology | 6,275 | 2021-08-17 -> 2023-12-16 | 8716 |
| **ON** | ON SEMICONDUCTOR CORP | Information Technology | 5,953 | 2023-02-06 -> 2023-12-15 | 448 |
| **ORCL** | ORACLE CORP | Information Technology | 9,527 | 2009-11-22 -> 2023-12-16 | 5291 |
| **PANW** | Palo Alto Networks Inc | Information Technology | 2,879 | 2023-08-18 -> 2023-12-16 | 382 |
| **QCOM** | QUALCOMM INC/DE | Information Technology | 8,070 | 2023-08-02 -> 2023-12-16 | 467 |
| **ROP** | ROPER TECHNOLOGIES INC | Information Technology | 8,028 | 2020-02-11 -> 2023-12-16 | 420 |
| **SWKS** | SKYWORKS SOLUTIONS, INC. | Information Technology | 9,907 | 2021-09-20 -> 2023-12-12 | 420 |
| **VRSN** | VERISIGN INC/CA | Information Technology | 6,521 | 2014-08-09 -> 2023-12-16 | 444 |
| **WDAY** | Workday, Inc. | Information Technology | 2,820 | 2022-12-29 -> 2023-12-16 | 426 |
| **CF** | CF Industries Holdings, Inc. | Materials | 4,627 | 2023-01-17 -> 2023-12-16 | 252 |
| **CTVA** | Corteva, Inc. | Materials | 1,158 | 2021-05-05 -> 2023-12-16 | 501 |
| **DOW** | DOW INC. | Materials | 1,204 | 2022-07-01 -> 2023-12-16 | 457 |
| **LIN** | LINDE PLC | Materials | 7,942 | 2023-12-14 -> 2023-12-16 | 7 |
| **LYB** | LyondellBasell Industries N.V. | Materials | 3,442 | 2023-12-11 -> 2023-12-16 | 7 |
| **PKG** | PACKAGING CORP OF AMERICA | Materials | 6,018 | 2019-12-17 -> 2023-12-16 | 426 |
| **AMT** | AMERICAN TOWER CORP /MA/ | Real Estate | 6,502 | 2022-10-17 -> 2023-12-16 | 455 |
| **ARE** | ALEXANDRIA REAL ESTATE EQUITIES, IN | Real Estate | 6,692 | 2022-01-05 -> 2023-12-16 | 403 |
| **BXP** | BXP, Inc. | Real Estate | 6,677 | 2019-10-21 -> 2023-12-16 | 403 |
| **CCI** | CROWN CASTLE INC. | Real Estate | 6,383 | 2022-04-12 -> 2023-12-16 | 445 |
| **CPT** | CAMDEN PROPERTY TRUST | Real Estate | 7,665 | 2018-10-25 -> 2023-12-12 | 316 |
| **CSGP** | COSTAR GROUP, INC. | Real Estate | 6,416 | 2017-12-15 -> 2023-12-13 | 375 |
| **DOC** | HEALTHPEAK PROPERTIES, INC. | Real Estate | 2,630 | 2013-07-05 -> 2023-12-14 | 366 |
| **ESS** | ESSEX PROPERTY TRUST, INC. | Real Estate | 7,444 | 2018-07-24 -> 2023-12-16 | 360 |
| **EXR** | Extra Space Storage Inc. | Real Estate | 4,877 | 2020-04-21 -> 2023-12-14 | 470 |
| **FRT** | FEDERAL REALTY INVESTMENT TRUST | Real Estate | 12,776 | 2020-11-06 -> 2023-12-12 | 409 |
| **KIM** | KIMCO REALTY CORP | Real Estate | 8,084 | 2019-08-29 -> 2023-12-14 | 387 |
| **PLD** | Prologis, Inc. | Real Estate | 6,567 | 2022-09-26 -> 2023-12-16 | 464 |
| **PSA** | Public Storage | Real Estate | 10,869 | 2021-11-01 -> 2023-12-14 | 498 |
| **REG** | REGENCY CENTERS CORP | Real Estate | 7,595 | 2022-11-28 -> 2023-12-15 | 110 |
| **VICI** | VICI PROPERTIES INC. | Real Estate | 1,556 | 2022-05-24 -> 2023-12-12 | 387 |
| **VTR** | Ventas, Inc. | Real Estate | 6,708 | 2019-02-06 -> 2023-12-14 | 410 |
| **WY** | WEYERHAEUSER CO | Real Estate | 12,776 | 2019-10-25 -> 2023-12-01 | 397 |
| **AEE** | AMEREN CORP | Utilities | 6,540 | 2019-01-28 -> 2023-12-16 | 495 |
| **AEP** | AMERICAN ELECTRIC POWER CO INC | Utilities | 13,618 | 2022-02-15 -> 2023-12-16 | 481 |
| **AES** | AES CORP | Utilities | 8,189 | 2019-07-29 -> 2023-12-16 | 478 |
| **ATO** | ATMOS ENERGY CORP | Utilities | 10,083 | 2021-11-11 -> 2023-12-16 | 439 |
| **AWK** | American Water Works Company, Inc. | Utilities | 3,949 | 2023-12-12 -> 2023-12-15 | 7 |
| **CNP** | CENTERPOINT ENERGY INC | Utilities | 13,618 | 2019-08-30 -> 2023-12-16 | 446 |
| **NRG** | NRG ENERGY, INC. | Utilities | 5,053 | 2020-11-06 -> 2023-12-16 | 528 |
| **PEG** | PUBLIC SERVICE ENTERPRISE GROUP INC | Utilities | 11,092 | 2019-02-27 -> 2023-12-14 | 450 |
| **VST** | Vistra Corp. | Utilities | 2,242 | 2018-05-23 -> 2023-12-14 | 429 |

## 5. Conclusiones y Decisión para la Fase 2

1. **Depuración cuantitativa completada:** Se ha descartado con rigor el 73% del dataset FNSPID que no cumple estándares de investigación (costura 2020, OHLC erróneo, ETFs y warrants).
2. **Universo viable identificado:** Disponemos de una base sólida y depurada de empresas de primera línea para el TFM.
3. **Paso a la Fase 2:** Con este censo, la Fase 2 (entity linking, descarte de casi-duplicados/boilerplate y alineación temporal anti-lookahead) se aplicará sobre un universo libre de ruido.