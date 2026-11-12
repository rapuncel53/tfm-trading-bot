import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_english_deck(output_paths=[
    "analisis_noticias_tfm/presentation_news_and_stock_selection.pptx",
    "analisis_noticias_tfm/presentacion_noticias_resumida.pptx"
]):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    C_NAVY = RGBColor(10, 37, 64)       # #0A2540
    C_BLUE = RGBColor(0, 102, 204)     # #0066CC
    C_DARK = RGBColor(30, 41, 59)      # #1E293B
    C_MUTED = RGBColor(100, 116, 139)  # #64748B
    C_BG_CARD = RGBColor(248, 250, 252)
    C_WHITE = RGBColor(255, 255, 255)
    C_GREEN = RGBColor(46, 125, 50)
    C_ORANGE = RGBColor(230, 81, 0)
    C_BORDER = RGBColor(226, 232, 240)

    blank_layout = prs.slide_layouts[6]

    def add_slide_header(slide, title_text, category="FINANCIAL NLP & NEWSFLOW | MASTER'S THESIS"):
        # Category label
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Calibri"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE
        
        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY
        
        # Underline rule
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.025))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BLUE
        line.line.color.rgb = C_BLUE

    # =============================================================
    # SLIDE 1: COVER
    # =============================================================
    s1 = prs.slides.add_slide(blank_layout)
    
    # Left accent banner
    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.3), Inches(7.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_BLUE
    banner.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "Financial News Datasets & Optimal Stock Selection"
    p0.font.name = "Calibri"
    p0.font.size = Pt(34)
    p0.font.bold = True
    p0.font.color.rgb = C_NAVY
    
    p1 = tf.add_paragraph()
    p1.text = "Dual-Source Audit (Benzinga vs. FNSPID) & Balanced Train / Val / Test Partitioning"
    p1.font.name = "Calibri"
    p1.font.size = Pt(18)
    p1.font.color.rgb = C_BLUE
    p1.font.bold = True
    p1.space_before = Pt(12)
    
    p2 = tf.add_paragraph()
    p2.text = "Master's Thesis (TFM)  •  UPC Barcelona  •  November 2026"
    p2.font.name = "Calibri"
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_MUTED
    p2.space_before = Pt(30)

    # =============================================================
    # SLIDE 2: THE TWO NEWS DATASETS (OVERVIEW)
    # =============================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "Two Complementary Financial News Datasets", "DATA ARCHITECTURE & SOURCES")

    # Card 1: Benzinga
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_BG_CARD
    c1.line.color.rgb = C_BLUE
    c1.line.width = Pt(1.5)
    
    tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "Benzinga News Feed"
    p.font.name = "Calibri"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(14)
    
    bullets_bz = [
        ("Time Horizon:", " 2009 – June 2020 (11 years of historical coverage)."),
        ("Data Volume:", " ~1.4 million news records across 6,204 unique tickers."),
        ("Feed Nature:", " High-frequency trading alerts and immediate market catalysts."),
        ("Publication Window:", " 97.2% published in pre-market (prior to 09:00 EDT)."),
        ("Role in Thesis:", " Core Training backbone (Train) & COVID crash stress-test (Val).")
    ]
    for bold_txt, norm_txt in bullets_bz:
        pb = tf1.add_paragraph()
        pb.space_after = Pt(10)
        r1 = pb.add_run()
        r1.text = "• " + bold_txt
        r1.font.bold = True
        r1.font.color.rgb = C_BLUE
        r1.font.size = Pt(13)
        r2 = pb.add_run()
        r2.text = norm_txt
        r2.font.color.rgb = C_DARK
        r2.font.size = Pt(13)

    # Card 2: FNSPID
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_BG_CARD
    c2.line.color.rgb = C_ORANGE
    c2.line.width = Pt(1.5)
    
    tb2 = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    p.text = "FNSPID Dataset (NASDAQ)"
    p.font.name = "Calibri"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(14)
    
    bullets_fn = [
        ("Time Horizon:", " 2009 – December 2023 (14 years of corpus history)."),
        ("Data Volume:", " ~15.7 million global NASDAQ financial news articles."),
        ("Feed Nature:", " Comprehensive academic corpus with full-text reporting."),
        ("Rich Structure:", " Headline, full body & 4 extractive summaries (LSA, TextRank)."),
        ("Role in Thesis:", " Blind out-of-sample evaluation under modern rates (Test 2021–2023).")
    ]
    for bold_txt, norm_txt in bullets_fn:
        pb = tf2.add_paragraph()
        pb.space_after = Pt(10)
        r1 = pb.add_run()
        r1.text = "• " + bold_txt
        r1.font.bold = True
        r1.font.color.rgb = C_ORANGE
        r1.font.size = Pt(13)
        r2 = pb.add_run()
        r2.text = norm_txt
        r2.font.color.rgb = C_DARK
        r2.font.size = Pt(13)

    # =============================================================
    # SLIDE 3: NEWS CHARACTERISTICS & REAL-WORLD EXAMPLES
    # =============================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "News Characteristics and Real-World Examples", "DATA CHARACTERISTICS & EXAMPLES")

    # Card 1: Benzinga Style & Examples
    c1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_BG_CARD
    c1.line.color.rgb = C_BLUE
    c1.line.width = Pt(1.5)
    
    tb1 = s3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.2), Inches(4.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "Benzinga: Actionable Trading Alerts"
    p.font.name = "Calibri"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(8)
    
    p_trait = tf1.add_paragraph()
    p_trait.text = "• Style: Ultra-short headlines reporting immediate price drivers: analyst upgrades/downgrades, price targets, and earnings surprises."
    p_trait.font.size = Pt(11.5)
    p_trait.font.color.rgb = C_DARK
    p_trait.space_after = Pt(12)
    
    p_ex_hdr = tf1.add_paragraph()
    p_ex_hdr.text = "Real Headline Samples:"
    p_ex_hdr.font.bold = True
    p_ex_hdr.font.size = Pt(12)
    p_ex_hdr.font.color.rgb = C_BLUE
    p_ex_hdr.space_after = Pt(6)
    
    # Ex 1 Box
    ex1_shape = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.3), Inches(5.2), Inches(1.4))
    ex1_shape.fill.solid()
    ex1_shape.fill.fore_color.rgb = C_WHITE
    ex1_shape.line.color.rgb = C_BORDER
    tb_e1 = s3.shapes.add_textbox(Inches(1.1), Inches(3.35), Inches(5.0), Inches(1.3))
    tf_e1 = tb_e1.text_frame
    tf_e1.word_wrap = True
    p_t1 = tf_e1.paragraphs[0]
    p_t1.text = "CAT (Caterpillar)  •  Analyst Price Target Revision"
    p_t1.font.bold = True
    p_t1.font.size = Pt(10.5)
    p_t1.font.color.rgb = C_BLUE
    p_m1 = tf_e1.add_paragraph()
    p_m1.text = '“UBS Maintains Neutral on Caterpillar, Raises Price Target to $112”'
    p_m1.font.italic = True
    p_m1.font.size = Pt(11)
    p_m1.font.color.rgb = C_DARK
    
    # Ex 2 Box
    ex2_shape = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.9), Inches(5.2), Inches(1.6))
    ex2_shape.fill.solid()
    ex2_shape.fill.fore_color.rgb = C_WHITE
    ex2_shape.line.color.rgb = C_BORDER
    tb_e2 = s3.shapes.add_textbox(Inches(1.1), Inches(4.95), Inches(5.0), Inches(1.5))
    tf_e2 = tb_e2.text_frame
    tf_e2.word_wrap = True
    p_t2 = tf_e2.paragraphs[0]
    p_t2.text = "CAT (Caterpillar)  •  Earnings Release & Guidance"
    p_t2.font.bold = True
    p_t2.font.size = Pt(10.5)
    p_t2.font.color.rgb = C_BLUE
    p_m2 = tf_e2.add_paragraph()
    p_m2.text = '“Caterpillar Q1 Adj. EPS $1.60 Misses $1.69 Estimate, Sales $10.60B Miss $10.92B Estimate”'
    p_m2.font.italic = True
    p_m2.font.size = Pt(11)
    p_m2.font.color.rgb = C_DARK

    # Card 2: FNSPID Style & Examples
    c2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_BG_CARD
    c2.line.color.rgb = C_ORANGE
    c2.line.width = Pt(1.5)
    
    tb2 = s3.shapes.add_textbox(Inches(7.0), Inches(1.75), Inches(5.3), Inches(4.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    p.text = "FNSPID: Corporate & Analytical Context"
    p.font.name = "Calibri"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(8)
    
    p_trait2 = tf2.add_paragraph()
    p_trait2.text = "• Style: In-depth company reports, official press statements, and fundamental corporate developments accompanied by NLP summaries."
    p_trait2.font.size = Pt(11.5)
    p_trait2.font.color.rgb = C_DARK
    p_trait2.space_after = Pt(12)
    
    p_ex_hdr2 = tf2.add_paragraph()
    p_ex_hdr2.text = "Real Headline Samples:"
    p_ex_hdr2.font.bold = True
    p_ex_hdr2.font.size = Pt(12)
    p_ex_hdr2.font.color.rgb = C_ORANGE
    p_ex_hdr2.space_after = Pt(6)
    
    # Ex 1 FNSPID Box
    ex3_shape = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(3.3), Inches(5.3), Inches(1.4))
    ex3_shape.fill.solid()
    ex3_shape.fill.fore_color.rgb = C_WHITE
    ex3_shape.line.color.rgb = C_BORDER
    tb_e3 = s3.shapes.add_textbox(Inches(7.1), Inches(3.35), Inches(5.1), Inches(1.3))
    tf_e3 = tb_e3.text_frame
    tf_e3.word_wrap = True
    p_t3 = tf_e3.paragraphs[0]
    p_t3.text = "A (Agilent Technologies)  •  Institutional Coverage Initiation"
    p_t3.font.bold = True
    p_t3.font.size = Pt(10.5)
    p_t3.font.color.rgb = C_ORANGE
    p_m3 = tf_e3.add_paragraph()
    p_m3.text = '“Wolfe Research Initiates Coverage of Agilent Technologies with Outperform Recommendation”'
    p_m3.font.italic = True
    p_m3.font.size = Pt(11)
    p_m3.font.color.rgb = C_DARK
    
    # Ex 2 FNSPID Box
    ex4_shape = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(4.9), Inches(5.3), Inches(1.6))
    ex4_shape.fill.solid()
    ex4_shape.fill.fore_color.rgb = C_WHITE
    ex4_shape.line.color.rgb = C_BORDER
    tb_e4 = s3.shapes.add_textbox(Inches(7.1), Inches(4.95), Inches(5.1), Inches(1.5))
    tf_e4 = tb_e4.text_frame
    tf_e4.word_wrap = True
    p_t4 = tf_e4.paragraphs[0]
    p_t4.text = "A (Agilent Technologies)  •  Product Innovation & Technology"
    p_t4.font.bold = True
    p_t4.font.size = Pt(10.5)
    p_t4.font.color.rgb = C_ORANGE
    p_m4 = tf_e4.add_paragraph()
    p_m4.text = '“Agilent Enhances BioTek Cytation C10 With New Technology”'
    p_m4.font.italic = True
    p_m4.font.size = Pt(11)
    p_m4.font.color.rgb = C_DARK

    # =============================================================
    # SLIDE 4: TIMELINE GANTT CHART (WHERE NEWS ARE LOCATED)
    # =============================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "Company News Timeline Coverage: Where and When News Occur", "TEMPORAL DISTRIBUTION & AUDIT")

    # Image on left (English chart)
    img_mapa = "analisis_noticias_tfm/mapa_temporal_noticias_por_compania_en.png"
    if not os.path.exists(img_mapa):
        img_mapa = "analisis_noticias_tfm/mapa_temporal_noticias_por_compania.png"
    if os.path.exists(img_mapa):
        s4.shapes.add_picture(img_mapa, Inches(0.8), Inches(1.55), Inches(8.3), Inches(5.3))

    # Right side: Key takeaway card
    c_side = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.3), Inches(1.55), Inches(3.2), Inches(5.3))
    c_side.fill.solid()
    c_side.fill.fore_color.rgb = C_BG_CARD
    c_side.line.color.rgb = C_BLUE
    c_side.line.width = Pt(1.5)
    
    tb_s = s4.shapes.add_textbox(Inches(9.45), Inches(1.7), Inches(2.9), Inches(5.0))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    
    p = tf_s.paragraphs[0]
    p.text = "Key Timeline Findings:"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(12)
    
    notes_s4 = [
        ("Tier 1 (Continuous):", " 36 companies exhibit uninterrupted newsflow across Train, Val, and Test (e.g., ORCL, CAT, KO, NVDA)."),
        ("Big Tech Asymmetry:", " AAPL, AMZN, and MSFT have 85%–100% of their news in 2022–2023 (empty in Train)."),
        ("14-Month Embargo:", " Methodological quarantine (Jun 2020 – Aug 2021) isolates post-COVID distortions and prevents source overlap.")
    ]
    for b_title, b_desc in notes_s4:
        p_item = tf_s.add_paragraph()
        p_item.space_after = Pt(12)
        r1 = p_item.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.color.rgb = C_BLUE
        r1.font.size = Pt(11.5)
        r2 = p_item.add_run()
        r2.text = b_desc
        r2.font.color.rgb = C_DARK
        r2.font.size = Pt(11.5)

    # =============================================================
    # SLIDE 5: OPTIMAL STOCK SELECTION (BALANCED 70 / 10 / 20 SPLIT)
    # =============================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "Optimal Stock Selection: Balanced Train / Val / Test Split", "PORTFOLIO SELECTION & METHODOLOGY")

    # Image on left (English chart)
    img_dist = "analisis_noticias_tfm/distribucion_optimizada_70_10_20_en.png"
    if not os.path.exists(img_dist):
        img_dist = "analisis_noticias_tfm/distribucion_optimizada_70_10_20.png"
    if os.path.exists(img_dist):
        s5.shapes.add_picture(img_dist, Inches(0.8), Inches(1.55), Inches(8.3), Inches(5.3))

    # Right side: Key takeaway card
    c_side2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.3), Inches(1.55), Inches(3.2), Inches(5.3))
    c_side2.fill.solid()
    c_side2.fill.fore_color.rgb = C_BG_CARD
    c_side2.line.color.rgb = C_GREEN
    c_side2.line.width = Pt(1.5)
    
    tb_s2 = s5.shapes.add_textbox(Inches(9.45), Inches(1.7), Inches(2.9), Inches(5.0))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    
    p = tf_s2.paragraphs[0]
    p.text = "Why This Selection:"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(12)
    
    notes_s5 = [
        ("Elite Stock Basket:", " 12 liquid leaders across key GICS sectors (ORCL, CAT, KO, EBAY, V, COST, CRM, GILD, QCOM, ADBE, NVDA)."),
        ("ML Golden Ratio:", " Faithfully matches the ~70% Train (2011–2019), ~10% Val (COVID 2020), and ~20% Blind Test (2021–2023) split."),
        ("Zero Look-Ahead Bias:", " The LLM learns causal market dynamics in historical data and generalizes out-of-sample in modern market regimes.")
    ]
    for b_title, b_desc in notes_s5:
        p_item = tf_s2.add_paragraph()
        p_item.space_after = Pt(12)
        r1 = p_item.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.color.rgb = C_GREEN
        r1.font.size = Pt(11.5)
        r2 = p_item.add_run()
        r2.text = b_desc
        r2.font.color.rgb = C_DARK
        r2.font.size = Pt(11.5)

    # Save files
    for pth in output_paths:
        try:
            prs.save(pth)
            print(f"SUCCESS: Saved English presentation at {pth}")
        except PermissionError:
            print(f"NOTE: {pth} is currently open in another application. Saved alternative at {output_paths[0]}.")

if __name__ == "__main__":
    create_english_deck()
