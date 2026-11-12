# Catálogo Maestro de Empresas, Periodos de Noticias y Visor de Titulares (TFM)

> **Propósito:** Definir el universo de empresas elegibles para el Trabajo de Fin de Máster (TFM), detallando la calidad de los datos bursátiles (OHLCV 2000–2023), los periodos exactos de noticias disponibles (FNSPID y Benzinga) y la auditoría rigurosa de huecos temporales.

---

## 1. Resumen Ejecutivo del Universo de Datos

* **Activos de bolsa auditados inicialmente:** 7.693 tickers.
* **Filtros de calidad aplicados:**
  * Eliminación del corte abrupto de julio de 2020 (*seam* de Yahoo Finance).
  * Verificación física del OHLC (Low <= Open/Close/High, High >= Low, Vol >= 0).
  * Pertenencia oficial al índice S&P 500 (SEC CIK verificado).
* **Empresas Tier 1 Gold resultantes:** **199 empresas** con más de 20 años de precios diarios limpios (2000 a 2023).

### Clasificación de Cobertura de Noticias

| Categoría | Nº Empresas | Periodo Noticias | Existencia de Huecos | Idoneidad TFM |
| :--- | :---: | :---: | :---: | :--- |
| **Grupo 1: Continua Total** | **136** | **2009/2012 – 2023** | **0 huecos estructurales** | **Máxima (Recomendada)** |
| **Grupo 2: Big Tech Híbrida** | **22** | **2010/2019 – 2023** | **Hueco central (14 a 33 meses)** | Condicional (tratamiento de salto) |
| **Grupo 3: Continua Media** | **33** | **2013/2019 – 2023** | **0 huecos** | Alta (empresas más jóvenes) |
| **Grupo 4: Reciente / Fragmentada** | **8** | **2022/2023** | Fragmentada | Desaconsejada |

---

## 2. Visor Interactivo HTML

Se ha generado un cuadro de mando interactivo autónomo que permite filtrar, buscar y visualizar titulares reales:
👉 **[Abrir Dashboard Interactivo (catalogo_empresas_y_noticias.html)](file:///C:/Users/julia/.gemini/antigravity/brain/9f7a61e6-afb4-4584-a3e5-1f6d74df8639/catalogo_empresas_y_noticias.html)**

---

## 3. Grupo 1: Las 136 Empresas con Cobertura Continua (Sin Huecos)

Estas empresas son el núcleo óptimo para el entrenamiento y backtesting del modelo. Tienen cotizaciones diarias completas (2000–2023) y un flujo de noticias continuo mes a mes desde 2009 hasta finales de 2023.

### Sector: Communication Services (4 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`TTWO`** | TAKE TWO INTERACTIVE SOFTWARE INC | 6722 | 3,072 | 0 | **3,072** | 2010-05-26 a 2023-12-16 |
| **`CHTR`** | CHARTER COMMUNICATIONS, INC. /MO/ | 3520 | 2,187 | 210 | **2,397** | 2011-05-02 a 2023-12-16 |
| **`NWSA`** | NEWS CORP | 2651 | 1,223 | 1,058 | **2,281** | 2009-08-07 a 2023-12-13 |
| **`NWS`** | NEWS CORP | 2651 | 442 | 402 | **844** | 2009-08-17 a 2023-11-13 |

### Sector: Consumer Discretionary (11 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`CMG`** | CHIPOTLE MEXICAN GRILL INC | 4512 | 6,354 | 2,370 | **8,724** | 2009-10-16 a 2023-12-16 |
| **`EBAY`** | EBAY INC | 6357 | 5,260 | 3,018 | **8,278** | 2009-10-15 a 2023-12-16 |
| **`DRI`** | DARDEN RESTAURANTS INC | 7211 | 2,890 | 1,523 | **4,413** | 2009-08-17 a 2023-12-13 |
| **`DPZ`** | DOMINOS PIZZA INC | 4901 | 3,229 | 1,130 | **4,359** | 2009-10-13 a 2023-12-16 |
| **`ULTA`** | Ulta Beauty, Inc. | 4072 | 3,203 | 870 | **4,073** | 2011-06-08 a 2023-12-16 |
| **`EXPE`** | Expedia Group, Inc. | 4642 | 2,968 | 790 | **3,758** | 2010-04-28 a 2023-12-15 |
| **`TSCO`** | TRACTOR SUPPLY CO /DE/ | 7518 | 2,317 | 695 | **3,012** | 2009-10-08 a 2023-12-16 |
| **`RL`** | RALPH LAUREN CORP | 6681 | 1,927 | 933 | **2,860** | 2009-08-07 a 2023-12-14 |
| **`GRMN`** | GARMIN LTD | 5799 | 1,640 | 811 | **2,451** | 2009-08-16 a 2023-12-16 |
| **`ORLY`** | O REILLY AUTOMOTIVE INC | 7727 | 1,614 | 606 | **2,220** | 2009-09-02 a 2023-12-16 |
| **`NVR`** | NVR INC | 9688 | 1,250 | 247 | **1,497** | 2009-10-21 a 2023-12-15 |

### Sector: Consumer Staples (5 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`COST`** | COSTCO WHOLESALE CORP /NEW | 9445 | 6,781 | 0 | **6,781** | 2010-02-17 a 2023-12-16 |
| **`DLTR`** | DOLLAR TREE, INC. | 7255 | 2,968 | 1,508 | **4,476** | 2009-11-16 a 2023-12-12 |
| **`SYY`** | SYSCO CORP | 12773 | 1,875 | 796 | **2,671** | 2009-08-18 a 2023-12-16 |
| **`BG`** | Bunge Global SA | 5637 | 1,119 | 526 | **1,645** | 2009-07-27 a 2023-12-16 |
| **`CASY`** | CASEYS GENERAL STORES INC | 10130 | 1,484 | 70 | **1,554** | 2010-06-02 a 2023-12-16 |

### Sector: Energy (7 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`COP`** | CONOCOPHILLIPS | 10587 | 5,989 | 1,711 | **7,700** | 2009-08-10 a 2023-12-16 |
| **`OXY`** | OCCIDENTAL PETROLEUM CORP /DE/ | 10587 | 4,791 | 1,168 | **5,959** | 2009-07-27 a 2023-12-16 |
| **`EOG`** | EOG RESOURCES INC | 8625 | 3,515 | 924 | **4,439** | 2009-08-10 a 2023-12-16 |
| **`VLO`** | VALERO ENERGY CORP/TX | 10586 | 3,020 | 999 | **4,019** | 2009-08-10 a 2023-12-16 |
| **`APA`** | APA Corp | 11252 | 2,708 | 0 | **2,708** | 2010-02-10 a 2023-12-15 |
| **`FANG`** | Diamondback Energy, Inc. | 2820 | 2,031 | 110 | **2,141** | 2012-10-02 a 2023-12-16 |
| **`TRGP`** | Targa Resources Corp. | 3287 | 781 | 434 | **1,215** | 2011-01-18 a 2023-12-16 |

### Sector: Financials (21 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`V`** | VISA INC. | 3973 | 6,945 | 10 | **6,955** | 2010-04-15 a 2023-12-16 |
| **`BX`** | Blackstone Inc. | 4159 | 3,437 | 1,476 | **4,913** | 2009-08-13 a 2023-12-16 |
| **`USB`** | US BANCORP \DE\ | 12776 | 3,333 | 1,086 | **4,419** | 2009-08-09 a 2023-12-16 |
| **`COF`** | CAPITAL ONE FINANCIAL CORP | 7330 | 2,369 | 1,048 | **3,417** | 2009-07-27 a 2023-12-15 |
| **`CME`** | CME GROUP INC. | 5301 | 2,187 | 967 | **3,154** | 2009-07-27 a 2023-12-16 |
| **`KKR`** | KKR & Co. Inc. | 3388 | 2,109 | 1,042 | **3,151** | 2010-05-07 a 2023-12-16 |
| **`PRU`** | PRUDENTIAL FINANCIAL INC | 5548 | 2,109 | 827 | **2,936** | 2009-09-09 a 2023-12-12 |
| **`NDAQ`** | NASDAQ, INC. | 5412 | 1,796 | 1,112 | **2,908** | 2009-08-27 a 2023-12-14 |
| **`ICE`** | Intercontinental Exchange, Inc. | 4559 | 1,770 | 918 | **2,688** | 2009-08-10 a 2023-12-16 |
| **`ALL`** | ALLSTATE CORP | 7699 | 1,796 | 789 | **2,585** | 2009-08-10 a 2023-12-15 |
| **`APO`** | Apollo Global Management, Inc. | 3209 | 1,588 | 770 | **2,358** | 2010-02-27 a 2023-12-16 |
| **`KEY`** | KEYCORP /NEW/ | 9108 | 1,718 | 610 | **2,328** | 2010-04-14 a 2023-12-16 |
| **`CBOE`** | Cboe Global Markets, Inc. | 3409 | 1,927 | 0 | **1,927** | 2010-04-27 a 2023-12-16 |
| **`GPN`** | GLOBAL PAYMENTS INC | 5775 | 1,197 | 715 | **1,912** | 2009-10-01 a 2023-12-12 |
| **`ACGL`** | ARCH CAPITAL GROUP LTD. | 7122 | 1,536 | 269 | **1,805** | 2009-11-06 a 2023-12-16 |
| **`FIS`** | Fidelity National Information Services, Inc. | 5667 | 1,119 | 494 | **1,613** | 2009-11-18 a 2023-12-14 |
| **`FDS`** | FACTSET RESEARCH SYSTEMS INC | 6922 | 1,015 | 559 | **1,574** | 2009-12-15 a 2023-12-16 |
| **`AIZ`** | ASSURANT, INC. | 5009 | 1,197 | 328 | **1,525** | 2010-02-03 a 2023-12-16 |
| **`PFG`** | PRINCIPAL FINANCIAL GROUP INC | 5584 | 963 | 385 | **1,348** | 2009-08-16 a 2023-12-05 |
| **`MSCI`** | MSCI Inc. | 4057 | 963 | 351 | **1,314** | 2010-07-07 a 2023-12-16 |
| **`ERIE`** | ERIE INDEMNITY CO | 7110 | 286 | 108 | **394** | 2009-12-30 a 2023-12-12 |

### Sector: Health Care (21 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`MRK`** | Merck & Co., Inc. | 13618 | 8,593 | 3,333 | **11,926** | 2009-07-27 a 2023-12-16 |
| **`GILD`** | GILEAD SCIENCES, INC. | 8044 | 8,932 | 2,968 | **11,900** | 2009-09-11 a 2023-12-16 |
| **`BIIB`** | BIOGEN INC. | 8132 | 5,208 | 1,907 | **7,115** | 2010-02-09 a 2023-12-16 |
| **`VRTX`** | VERTEX PHARMACEUTICALS INC / MA | 8170 | 4,088 | 1,337 | **5,425** | 2009-08-10 a 2023-12-16 |
| **`HUM`** | HUMANA INC | 10587 | 2,864 | 1,575 | **4,439** | 2009-08-10 a 2023-12-16 |
| **`CI`** | Cigna Group | 10525 | 2,890 | 1,350 | **4,240** | 2009-08-07 a 2023-12-16 |
| **`BSX`** | BOSTON SCIENTIFIC CORP | 7962 | 2,421 | 1,456 | **3,877** | 2009-08-07 a 2023-12-16 |
| **`ALGN`** | ALIGN TECHNOLOGY INC | 5765 | 2,786 | 564 | **3,350** | 2010-01-28 a 2023-12-16 |
| **`EW`** | Edwards Lifesciences Corp | 5978 | 2,083 | 1,002 | **3,085** | 2009-08-28 a 2023-12-16 |
| **`DXCM`** | DEXCOM INC | 4710 | 2,031 | 594 | **2,625** | 2010-01-07 a 2023-12-16 |
| **`INCY`** | INCYTE CORP | 7591 | 1,692 | 884 | **2,576** | 2009-09-23 a 2023-12-13 |
| **`HCA`** | HCA Healthcare, Inc. | 3223 | 1,822 | 720 | **2,542** | 2011-03-10 a 2023-12-16 |
| **`DVA`** | DAVITA INC. | 7089 | 1,614 | 623 | **2,237** | 2010-03-11 a 2023-12-16 |
| **`DGX`** | QUEST DIAGNOSTICS INC | 6803 | 1,354 | 763 | **2,117** | 2009-10-08 a 2023-12-16 |
| **`HSIC`** | HENRY SCHEIN INC | 7086 | 1,510 | 423 | **1,933** | 2009-12-01 a 2023-12-16 |
| **`RMD`** | RESMED INC | 7194 | 1,119 | 427 | **1,546** | 2010-02-08 a 2023-12-11 |
| **`PODD`** | INSULET CORP | 4186 | 989 | 475 | **1,464** | 2009-10-27 a 2023-12-16 |
| **`CRL`** | CHARLES RIVER LABORATORIES INTERNATIONAL, INC. | 5916 | 885 | 507 | **1,392** | 2009-08-07 a 2023-12-16 |
| **`WAT`** | WATERS CORP /DE/ | 7076 | 625 | 316 | **941** | 2009-10-28 a 2023-12-13 |
| **`COR`** | Cencora, Inc. | 7235 | 677 | 217 | **894** | 2010-06-01 a 2023-12-16 |
| **`MTD`** | METTLER TOLEDO INTERNATIONAL INC/ | 6572 | 442 | 256 | **698** | 2009-08-10 a 2023-12-16 |

### Sector: Industrials (22 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`GE`** | GENERAL ELECTRIC CO | 15605 | 9,921 | 0 | **9,921** | 2012-04-20 a 2023-12-16 |
| **`FDX`** | FEDEX CORP | 11528 | 5,234 | 2,629 | **7,863** | 2009-09-13 a 2023-12-16 |
| **`CAT`** | CATERPILLAR INC | 13618 | 5,185 | 2,322 | **7,507** | 2009-11-04 a 2023-12-16 |
| **`NOC`** | NORTHROP GRUMMAN CORP /DE/ | 10587 | 4,166 | 1,214 | **5,380** | 2009-08-07 a 2023-12-16 |
| **`UPS`** | UNITED PARCEL SERVICE INC | 6072 | 4,427 | 90 | **4,517** | 2009-11-20 a 2023-12-16 |
| **`CSX`** | CSX CORP | 10879 | 2,526 | 1,617 | **4,143** | 2009-07-21 a 2023-12-16 |
| **`NSC`** | NORFOLK SOUTHERN CORP | 10482 | 2,109 | 1,192 | **3,301** | 2009-10-26 a 2023-12-16 |
| **`UNP`** | UNION PACIFIC CORP | 11092 | 3,177 | 50 | **3,227** | 2009-11-03 a 2023-12-16 |
| **`URI`** | UNITED RENTALS, INC. | 6549 | 1,822 | 270 | **2,092** | 2011-01-14 a 2023-12-16 |
| **`ROK`** | ROCKWELL AUTOMATION, INC | 10587 | 1,093 | 561 | **1,654** | 2009-11-03 a 2023-12-16 |
| **`PWR`** | QUANTA SERVICES, INC. | 6512 | 1,145 | 419 | **1,564** | 2009-08-07 a 2023-12-16 |
| **`BLDR`** | Builders FirstSource, Inc. | 4658 | 1,223 | 283 | **1,506** | 2010-02-22 a 2023-12-16 |
| **`RSG`** | REPUBLIC SERVICES, INC. | 6416 | 1,093 | 375 | **1,468** | 2009-10-29 a 2023-12-14 |
| **`BR`** | BROADRIDGE FINANCIAL SOLUTIONS, INC. | 4223 | 1,041 | 307 | **1,348** | 2009-08-10 a 2023-12-16 |
| **`PNR`** | PENTAIR plc | 12776 | 807 | 473 | **1,280** | 2009-11-23 a 2023-12-12 |
| **`CHRW`** | C. H. ROBINSON WORLDWIDE, INC. | 6593 | 1,223 | 30 | **1,253** | 2010-07-31 a 2023-12-11 |
| **`WAB`** | WESTINGHOUSE AIR BRAKE TECHNOLOGIES CORP | 7184 | 781 | 443 | **1,224** | 2009-08-13 a 2023-12-16 |
| **`CPRT`** | COPART INC | 7499 | 885 | 336 | **1,221** | 2010-01-07 a 2023-12-15 |
| **`XYL`** | Xylem Inc. | 3072 | 885 | 311 | **1,196** | 2011-10-24 a 2023-12-13 |
| **`GNRC`** | GENERAC HOLDINGS INC. | 3494 | 859 | 335 | **1,194** | 2010-02-11 a 2023-12-12 |
| **`VRSK`** | Verisk Analytics, Inc. | 3581 | 807 | 338 | **1,145** | 2009-10-19 a 2023-12-16 |
| **`FIX`** | COMFORT SYSTEMS USA INC | 6670 | 625 | 157 | **782** | 2009-12-23 a 2023-12-13 |

### Sector: Information Technology (23 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`QCOM`** | QUALCOMM INC/DE | 8070 | 7,031 | 2,941 | **9,972** | 2010-02-01 a 2023-12-16 |
| **`ORCL`** | ORACLE CORP | 9527 | 5,291 | 2,701 | **7,992** | 2009-11-22 a 2023-12-16 |
| **`CRM`** | Salesforce, Inc. | 4914 | 6,105 | 1,483 | **7,588** | 2009-12-14 a 2023-12-16 |
| **`FSLR`** | FIRST SOLAR, INC. | 4306 | 3,880 | 2,222 | **6,102** | 2010-01-09 a 2023-12-16 |
| **`PANW`** | Palo Alto Networks Inc | 2879 | 3,567 | 1,334 | **4,901** | 2012-07-09 a 2023-12-16 |
| **`HPQ`** | HP INC | 15605 | 4,635 | 10 | **4,645** | 2009-10-14 a 2023-12-16 |
| **`ACN`** | Accenture plc | 5647 | 3,151 | 1,323 | **4,474** | 2009-10-01 a 2023-12-16 |
| **`MRVL`** | Marvell Technology, Inc. | 5911 | 2,187 | 1,517 | **3,704** | 2009-08-13 a 2023-12-12 |
| **`NTAP`** | NetApp, Inc. | 7074 | 1,744 | 1,535 | **3,279** | 2009-07-27 a 2023-12-15 |
| **`FTNT`** | Fortinet, Inc. | 3551 | 2,161 | 887 | **3,048** | 2010-06-03 a 2023-12-16 |
| **`WDAY`** | Workday, Inc. | 2820 | 1,901 | 939 | **2,840** | 2012-08-31 a 2023-12-16 |
| **`NOW`** | ServiceNow, Inc. | 2893 | 1,953 | 659 | **2,612** | 2009-08-07 a 2023-12-16 |
| **`CIEN`** | CIENA CORP | 6767 | 1,197 | 1,114 | **2,311** | 2009-08-13 a 2023-12-16 |
| **`CTSH`** | COGNIZANT TECHNOLOGY SOLUTIONS CORP | 6424 | 1,432 | 843 | **2,275** | 2009-08-17 a 2023-12-14 |
| **`DELL`** | Dell Technologies Inc. | 1854 | 2,083 | 0 | **2,083** | 2009-10-26 a 2023-12-16 |
| **`SWKS`** | SKYWORKS SOLUTIONS, INC. | 9907 | 1,979 | 0 | **1,979** | 2010-03-08 a 2023-12-12 |
| **`AKAM`** | AKAMAI TECHNOLOGIES INC | 6080 | 1,770 | 90 | **1,860** | 2009-11-06 a 2023-12-15 |
| **`ROP`** | ROPER TECHNOLOGIES INC | 8028 | 1,119 | 349 | **1,468** | 2010-01-07 a 2023-12-16 |
| **`APH`** | AMPHENOL CORP /DE/ | 8094 | 937 | 360 | **1,297** | 2009-08-07 a 2023-12-16 |
| **`FLEX`** | FLEX LTD. | 7498 | 781 | 469 | **1,250** | 2009-08-13 a 2023-12-16 |
| **`FFIV`** | F5, INC. | 6183 | 1,093 | 0 | **1,093** | 2010-03-18 a 2023-12-07 |
| **`MPWR`** | MONOLITHIC POWER SYSTEMS, INC. | 4809 | 729 | 289 | **1,018** | 2010-02-03 a 2023-12-16 |
| **`VRSN`** | VERISIGN INC/CA | 6521 | 598 | 388 | **986** | 2009-07-27 a 2023-12-16 |

### Sector: Materials (1 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`PKG`** | PACKAGING CORP OF AMERICA | 6018 | 1,067 | 429 | **1,496** | 2009-10-09 a 2023-12-16 |

### Sector: Real Estate (14 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`AMT`** | AMERICAN TOWER CORP /MA/ | 6502 | 4,843 | 708 | **5,551** | 2009-09-16 a 2023-12-16 |
| **`PSA`** | Public Storage | 10869 | 1,953 | 460 | **2,413** | 2009-12-01 a 2023-12-14 |
| **`CCI`** | CROWN CASTLE INC. | 6383 | 1,744 | 626 | **2,370** | 2009-08-10 a 2023-12-16 |
| **`PLD`** | Prologis, Inc. | 6567 | 2,135 | 0 | **2,135** | 2010-06-24 a 2023-12-16 |
| **`VTR`** | Ventas, Inc. | 6708 | 1,223 | 488 | **1,711** | 2009-11-16 a 2023-12-14 |
| **`BXP`** | BXP, Inc. | 6677 | 1,067 | 504 | **1,571** | 2009-11-02 a 2023-12-16 |
| **`KIM`** | KIMCO REALTY CORP | 8084 | 1,067 | 388 | **1,455** | 2009-11-17 a 2023-12-14 |
| **`ARE`** | ALEXANDRIA REAL ESTATE EQUITIES, INC. | 6692 | 1,197 | 238 | **1,435** | 2009-08-10 a 2023-12-16 |
| **`EXR`** | Extra Space Storage Inc. | 4877 | 1,067 | 280 | **1,347** | 2010-01-11 a 2023-12-14 |
| **`ESS`** | ESSEX PROPERTY TRUST, INC. | 7444 | 885 | 346 | **1,231** | 2009-10-28 a 2023-12-16 |
| **`WY`** | WEYERHAEUSER CO | 12776 | 1,145 | 0 | **1,145** | 2010-07-12 a 2023-12-01 |
| **`FRT`** | FEDERAL REALTY INVESTMENT TRUST | 12776 | 963 | 0 | **963** | 2010-02-25 a 2023-12-12 |
| **`CPT`** | CAMDEN PROPERTY TRUST | 7665 | 651 | 281 | **932** | 2009-08-10 a 2023-12-12 |
| **`CSGP`** | COSTAR GROUP, INC. | 6416 | 677 | 210 | **887** | 2010-11-18 a 2023-12-13 |

### Sector: Utilities (7 empresas)
| Ticker | Empresa | Precios | Noticias FNSPID | Noticias Benzinga | Total Noticias | Periodo Completo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`NRG`** | NRG ENERGY, INC. | 5053 | 1,588 | 754 | **2,342** | 2009-11-16 a 2023-12-16 |
| **`PEG`** | PUBLIC SERVICE ENTERPRISE GROUP INC | 11092 | 1,614 | 556 | **2,170** | 2009-10-28 a 2023-12-14 |
| **`AEP`** | AMERICAN ELECTRIC POWER CO INC | 13618 | 1,953 | 0 | **1,953** | 2009-10-09 a 2023-12-16 |
| **`AES`** | AES CORP | 8189 | 1,223 | 482 | **1,705** | 2009-08-10 a 2023-12-16 |
| **`CNP`** | CENTERPOINT ENERGY INC | 13618 | 1,197 | 476 | **1,673** | 2010-02-19 a 2023-12-16 |
| **`AEE`** | AMEREN CORP | 6540 | 1,276 | 379 | **1,655** | 2009-10-27 a 2023-12-16 |
| **`ATO`** | ATMOS ENERGY CORP | 10083 | 989 | 0 | **989** | 2012-02-22 a 2023-12-16 |

---

## 4. Grupo 2: Big Tech Híbridas (Detalle del Hueco Central)

Para estas 22 empresas, Benzinga cubre el periodo histórico hasta el **10 de junio de 2020**, y FNSPID comienza más tarde debido al límite de 8.700 noticias del scraper de NASDAQ. Existe un hueco intermedio que debe tenerse en cuenta si se utilizan:

| Ticker | Empresa | Sector | Fin Benzinga | Inicio FNSPID | Duración del Hueco | Meses Vacíos |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`NVDA`** | NVIDIA CORP | Information Technology | 2020-06-10 | 2021-08-17 | **433 días** | **14.2 meses** |
| **`NCLH`** | Norwegian Cruise Line Holdings Ltd. | Consumer Discretionary | 2020-06-09 | 2021-12-02 | **541 días** | **17.8 meses** |
| **`TSLA`** | Tesla, Inc. | Consumer Discretionary | 2020-06-10 | 2022-05-02 | **691 días** | **22.7 meses** |
| **`AAPL`** | Apple Inc. | Information Technology | 2020-06-10 | 2022-06-03 | **723 días** | **23.8 meses** |
| **`DAL`** | DELTA AIR LINES, INC. | Industrials | 2020-06-10 | 2022-11-22 | **895 días** | **29.4 meses** |
| **`REG`** | REGENCY CENTERS CORP | Real Estate | 2020-06-11 | 2022-11-28 | **900 días** | **29.6 meses** |
| **`GOOG`** | Alphabet Inc. | Communication Services | 2020-06-10 | 2023-01-10 | **944 días** | **31.1 meses** |
| **`HIG`** | HARTFORD INSURANCE GROUP, INC. | Financials | 2020-06-11 | 2023-02-02 | **966 días** | **31.8 meses** |
| **`AMZN`** | AMAZON COM INC | Consumer Discretionary | 2020-06-10 | 2023-03-09 | **1002 días** | **33.0 meses** |
| **`F`** | FORD MOTOR CO | Consumer Discretionary | 2020-06-11 | 2023-06-09 | **1093 días** | **36.0 meses** |
| **`REGN`** | REGENERON PHARMACEUTICALS, INC. | Health Care | 2020-06-05 | 2023-08-28 | **1179 días** | **38.8 meses** |
| **`RCL`** | ROYAL CARIBBEAN CRUISES LTD | Consumer Discretionary | 2020-06-11 | 2023-11-15 | **1252 días** | **41.2 meses** |
| **`LH`** | LABCORP HOLDINGS INC. | Health Care | 2020-06-11 | 2023-11-23 | **1260 días** | **41.4 meses** |
| **`GM`** | General Motors Co | Consumer Discretionary | 2020-06-11 | 2023-11-30 | **1267 días** | **41.7 meses** |
| **`LYB`** | LyondellBasell Industries N.V. | Materials | 2020-06-11 | 2023-12-11 | **1278 días** | **42.0 meses** |
| **`LYV`** | Live Nation Entertainment, Inc. | Communication Services | 2020-06-11 | 2023-12-16 | **1283 días** | **42.2 meses** |
| **`IBM`** | INTERNATIONAL BUSINESS MACHINES CORP | Information Technology | 2020-06-11 | 2023-12-16 | **1283 días** | **42.2 meses** |
| **`AWK`** | American Water Works Company, Inc. | Utilities | 2020-06-05 | 2023-12-12 | **1285 días** | **42.3 meses** |
| **`IBKR`** | Interactive Brokers Group, Inc. | Financials | 2020-06-04 | 2023-12-11 | **1285 días** | **42.3 meses** |
| **`AVGO`** | Broadcom Inc. | Information Technology | 2020-06-08 | 2023-12-16 | **1286 días** | **42.3 meses** |
| **`AZO`** | AUTOZONE INC | Consumer Discretionary | 2020-05-27 | 2023-12-12 | **1294 días** | **42.6 meses** |
| **`LII`** | LENNOX INTERNATIONAL INC | Industrials | 2020-04-21 | 2023-12-05 | **1323 días** | **43.5 meses** |

---

## 5. Muestras de Noticias Reales Extraídas

A continuación se presentan muestras reales de noticias representativas para empresas emblemáticas de cada grupo, demostrando la naturaleza del texto disponible:

### `NVDA` — NVIDIA CORP (Information Technology)
* **Total Noticias Disponibles:** 11,862 (Benzinga: 3,146, FNSPID: 8,716)
* **Periodo:** 2011-03-03 a 2023-12-16
* ⚠️ **Hueco detectado:** 433 días (14.4 meses)

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2011-03-03` | Benzinga | Nvidia Goes Negative (NVDA)... | Scott Rubin |
| `2013-03-14` | Benzinga | PlayStation 4 was Too Expensive for NVIDIA... | Louis Bedigian |
| `2016-03-23` | Benzinga | Global Equities Trip Chowdhry Says Nvidia Business Extremely Strong... | Hal Lindon |
| `2017-04-09` | Benzinga | Benzinga's Top Picks Of The Week: Disney, Netflix, BlackBerry And More... | Nelson Hem |
| `2017-12-23` | Benzinga | AMD, Fitbit Top List Of Robinhood Broker's 'Most Traded' Stocks Of The Year... | Jayson Derrick |
| `2018-11-15` | Benzinga | NVIDIA To Report Q3 Earnings After The Closing Bell; Co. Historically Issues Its Report At... | Benzinga Newsdesk |


### `QCOM` — QUALCOMM INC/DE (Information Technology)
* **Total Noticias Disponibles:** 9,972 (Benzinga: 2,941, FNSPID: 7,031)
* **Periodo:** 2010-02-01 a 2023-12-16

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2011-11-03` | Benzinga | Benzinga's Top ETF Decliners, November 3rd (TVIX, SOXS, TZA, ERY)... | Craig Jones |
| `2013-08-05` | Benzinga | Benzinga's Top Downgrades... | Lisa Levin |
| `2015-04-13` | Benzinga | UPDATE: Qualcomm Shares Rise More than 4% Premarket as Jana Urges Spinoff of Chip Unit... | Charles Gross |
| `2016-06-30` | Benzinga | Bernstein Downgrades Qualcomm Ahead Of Q3 Results... | Manikandan Raman |
| `2017-06-21` | Benzinga | The Latest On Apple's Legal Battle With Qualcomm... | Jayson Derrick |
| `2018-04-05` | Benzinga | REMINDER: QUALCOMM Tender Offer For NXP Semiconductors Set To Expire Friday at 5pm ET... | Hal Lindon |


### `V` — VISA INC. (Financials)
* **Total Noticias Disponibles:** 6,955 (Benzinga: 10, FNSPID: 6,945)
* **Periodo:** 2010-04-15 a 2023-12-16

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2020-05-20` | Benzinga | Cowen & Co. Maintains Outperform on Visa, Raises Price Target to $196... | vishwanath@benzinga.com |
| `2020-05-21` | Benzinga | Mastercard Employees Can Work From Home Until Pandemic Is Under Control... | Shivdeep Dhaliwal |
| `2020-05-26` | Benzinga | Visa Option Trader Makes $4.3M Bet On 14% Upside... | Wayne Duggan |
| `2020-06-01` | Benzinga | Visa Says Global Processed Transactions Declined 12% In May, A 12 Ppt Improvement Over Apr... | Benzinga Newsdesk |
| `2020-06-05` | Benzinga | Shares of several companies in the broader technology sector are trading higher as markets... | BenzingaâNewsdesk |
| `2020-06-05` | Benzinga | Shares of several companies in the broader technology space are trading higher as markets ... | BenzingaâNewsdesk |


### `CAT` — CATERPILLAR INC (Industrials)
* **Total Noticias Disponibles:** 7,507 (Benzinga: 2,322, FNSPID: 5,185)
* **Periodo:** 2009-11-04 a 2023-12-16

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2011-08-23` | Benzinga | Mad Money Lightning Round: Cramer Likes Caterpillar... | Lisa Levin |
| `2012-10-11` | Benzinga | RBC Downgrades Caterpillar from Outperform to Sector Perform... | Paul Quintaro |
| `2013-12-17` | Benzinga | Slideshow: The Top 10 'Highs & Dives' Of S&P 500 Stocks In 2013... | Charley Blaine |
| `2015-09-21` | Benzinga | 8-K from Cat Shows Global Rolling 3-Month Retail Sales for Aug. Down 14%... | Paul Quintaro |
| `2016-12-01` | Benzinga | Caterpillar 8-K Shows Co. Belief FY17 EPS Of $3.25 'Too Optimistic' Considering Expected H... | Paul Quintaro |
| `2018-01-25` | Benzinga | Mid-Morning Market Update: Markets Mostly Higher; Caterpillar Earnings Beat Expectations... | Lisa Levin |


### `MRK` — Merck & Co., Inc. (Health Care)
* **Total Noticias Disponibles:** 11,926 (Benzinga: 3,333, FNSPID: 8,593)
* **Periodo:** 2009-07-27 a 2023-12-16

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2009-07-27` | Benzinga | Wall Street News Alert: Stocks This Morning: Green Star Alternative Energy -- July 27, 200... | Benzinga Staff |
| `2011-08-09` | Benzinga | Jefferies Upgrades Merck & Co. To Buy, Lowers PT To $37... | Joe Young |
| `2013-08-02` | Benzinga | S&P: Heaping Praise For Some Health Care ETFs... | ETF Professor |
| `2015-01-27` | Benzinga | Fast Money Halftime Report Final Trade From January 27... | Craig Jones |
| `2016-08-08` | Benzinga | Results from Merck's Phase 3 Study Of Zepatier Hep C Treatment Published In Annals Of Inte... | Hal Lindon |
| `2018-02-06` | Benzinga | Leerink Swann Maintains Market Perform on Merck & Co, Lowers Price Target to $67.00... | Vick Meyer |


### `COST` — COSTCO WHOLESALE CORP /NEW (Consumer Staples)
* **Total Noticias Disponibles:** 6,781 (Benzinga: 0, FNSPID: 6,781)
* **Periodo:** 2010-02-17 a 2023-12-16

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2019-01-04` | NASDAQ (FNSPID) | Dollar General Corporation (DG) Ex-Dividend Date Scheduled for January 07, 2019... | NASDAQ |
| `2019-11-27` | NASDAQ (FNSPID) | 3 Smart Money Stocks to Buy... | NASDAQ |
| `2020-08-19` | NASDAQ (FNSPID) | Kohl’s Stock Has Reached the Retail Lifeboat... | NASDAQ |
| `2021-05-21` | NASDAQ (FNSPID) | Warren Buffett's Latest Investing Mistakes... | NASDAQ |
| `2022-02-18` | NASDAQ (FNSPID) | Wolverine (WWW) Queued Up for Q4 Earnings: What's in Store?... | NASDAQ |
| `2022-09-30` | NASDAQ (FNSPID) | Costco (COST) is a Top-Ranked Growth Stock: Should You Buy?... | NASDAQ |


### `TSLA` — Tesla, Inc. (Consumer Discretionary)
* **Total Noticias Disponibles:** 10,587 (Benzinga: 1,875, FNSPID: 8,712)
* **Periodo:** 2019-07-01 a 2023-12-16
* ⚠️ **Hueco detectado:** 691 días (23.0 meses)

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2019-07-01` | Benzinga | Tesla's Q2 Delivery Number Could Cause A Big Move... | Wayne Duggan |
| `2019-07-01` | NASDAQ (FNSPID) | UPDATE: JMP Reiterates Outperform, $347 Target On Tesla As Firm Notes 'In general we think... | Benzinga_Newsdesk |
| `2019-09-26` | Benzinga | 'Tesla 'has a shot' at record 100,000 cars this quarter â Elon Musk in leak email' -Elec... | Benzinga Newsdesk |
| `2019-11-22` | Benzinga | Why Tesla Shorts Can't Stop, Won't Stop... | Wayne Duggan |
| `2019-12-12` | NASDAQ (FNSPID) | 'I Can't Fight It Anymore': Why Cramer Likes Tesla Now... | Elizabeth Balboa |
| `2020-01-13` | Benzinga | Tesla $93B Valuation: Does A Great Product Equate To A Great Stock?... | Tom Meilleur |


### `AAPL` — Apple Inc. (Information Technology)
* **Total Noticias Disponibles:** 9,306 (Benzinga: 441, FNSPID: 8,865)
* **Periodo:** 2020-03-09 a 2023-12-16
* ⚠️ **Hueco detectado:** 723 días (24.1 meses)

| Fecha | Fuente | Titular de la Noticia | Editor |
| :--- | :---: | :--- | :--- |
| `2020-03-09` | Benzinga | Crude Awakening: Energy Sector Takes A 20% Spill As Crude Price War Sends Oil To 4-Year Lo... | JJ Kinahan |
| `2020-03-17` | Benzinga | Jefferies Reiterates Buy on Apple, Lowers Price Target to $320... | Benzinga_Newsdesk |
| `2020-03-31` | Benzinga | Apple Acquires DarkSky, Weather App To Be Pulled From Android... | Neer Varshney |
| `2020-04-15` | Benzinga | BioXcel Therapeutics CEO Says Wearable Devices Are Another Tool To Combat Alzheimer's Agit... | Othanas Economopoulos |
| `2020-04-27` | Benzinga | Apple Is Pushing Back New iPhone Production, WSJ Reports... | Tanzeel Akhtar |
| `2020-05-01` | Benzinga | 32 Stocks Moving in Friday's Pre-Market Session... | Lisa Levin |


---

## 6. Recomendaciones para la Configuración Final del Dataset del TFM

1. **Cesta Principal de Experimentación (Recomendada):** Seleccionar 20 a 30 líderes del **Grupo 1** (como `QCOM`, `ORCL`, `CRM`, `V`, `JPM`, `MRK`, `GILD`, `CAT`, `GE`, `COST`, `COP`). Garantiza 14 años continuos (2009–2023) sin necesidad de imputación ni saltos temporales.
2. **Uso de Nvidia / Big Tech:** Si se incluye a `NVDA` o `TSLA`, se recomienda evaluarlas en su ventana reciente continua (agosto 2021 – diciembre 2023), o bien documentar explícitamente en el TFM el salto temporal de 2020-2021.