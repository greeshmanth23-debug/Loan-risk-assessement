"""
ML Project Report Generator
Generates a DOCX report following the template's exact formatting:
  - Chapter titles: 12pt bold, centered, black (#000000)
  - Heading 1 (section headings): 16pt (Heading 1 style)
  - Heading 2 (subsection headings): 13pt (Heading 2 style)
  - Body text: 11pt, justified, black
  - List items: 11pt, List Paragraph style
  - Each chapter/section starts on a new page via section breaks
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ─── Constants ───────────────────────────────────────────────────────────────
FONT_NAME = "Times New Roman"
BODY_SIZE = Pt(12)
CHAPTER_TITLE_SIZE = Pt(12)
HEADING1_SIZE = Pt(16)
HEADING2_SIZE = Pt(13)
LIST_SIZE = Pt(12)
BLACK = RGBColor(0, 0, 0)
GREEN_SCHOOL = RGBColor(0x2E, 0x7D, 0x32)
RED_CERT = RGBColor(0xCC, 0x00, 0x00)


def set_run_font(run, size=BODY_SIZE, bold=False, italic=False, color=BLACK, name=FONT_NAME, underline=False):
    """Apply uniform font formatting to a run."""
    run.font.name = name
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.underline = underline
    # Ensure East Asian font fallback
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), name)


def add_page_break_before(paragraph):
    """Set the paragraph to start on a new page."""
    pPr = paragraph._element.get_or_add_pPr()
    pb = OxmlElement('w:pageBreakBefore')
    pb.set(qn('w:val'), 'true')
    pPr.append(pb)


def add_section_break(doc):
    """Add a section break (new page) to the document."""
    new_section = doc.add_section()
    new_section.page_width = Inches(8.27)
    new_section.page_height = Inches(11.69)
    new_section.top_margin = Inches(1)
    new_section.bottom_margin = Inches(1)
    new_section.left_margin = Inches(1)
    new_section.right_margin = Inches(1)
    return new_section


def add_chapter_title(doc, chapter_num, chapter_name, new_page=True):
    """Add centered CHAPTER N + TITLE like the template."""
    if new_page:
        add_section_break(doc)

    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p1.add_run(f"CHAPTER {chapter_num}")
    set_run_font(run1, size=CHAPTER_TITLE_SIZE, bold=True, color=BLACK)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run(chapter_name.upper())
    set_run_font(run2, size=CHAPTER_TITLE_SIZE, bold=True, color=BLACK)

    doc.add_paragraph()  # spacing


def add_heading1(doc, text):
    """Add a Heading 1 style paragraph."""
    h = doc.add_heading(text, level=1)
    for run in h.runs:
        set_run_font(run, size=HEADING1_SIZE, bold=True, color=BLACK)
    return h


def add_heading2(doc, text):
    """Add a Heading 2 style paragraph."""
    h = doc.add_heading(text, level=2)
    for run in h.runs:
        set_run_font(run, size=HEADING2_SIZE, bold=True, color=BLACK)
    return h


def add_body(doc, text, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add a justified body paragraph."""
    p = doc.add_paragraph()
    p.alignment = alignment
    run = p.add_run(text)
    set_run_font(run, size=BODY_SIZE)
    return p


def add_body_bold_prefix(doc, prefix, text, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add paragraph with bold prefix followed by normal text."""
    p = doc.add_paragraph()
    p.alignment = alignment
    r1 = p.add_run(prefix)
    set_run_font(r1, size=BODY_SIZE, bold=True)
    r2 = p.add_run(text)
    set_run_font(r2, size=BODY_SIZE)
    return p


def add_list_item(doc, text, bold=False):
    """Add a bullet list item using List Paragraph style."""
    p = doc.add_paragraph(style='List Paragraph')
    run = p.add_run(text)
    set_run_font(run, size=LIST_SIZE, bold=bold)
    return p


def add_centered(doc, text, size=BODY_SIZE, bold=False, color=BLACK):
    """Add a centered paragraph."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    return p


def add_table(doc, headers, rows):
    """Add a formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'

    # Header row
    for j, header in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(header)
        set_run_font(run, size=BODY_SIZE, bold=True)

    # Data rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            set_run_font(run, size=BODY_SIZE)

    doc.add_paragraph()
    return table


# ═══════════════════════════════════════════════════════════════════════════
#  REPORT CONTENT
# ═══════════════════════════════════════════════════════════════════════════

def generate_report():
    doc = Document()

    # Set default style
    style = doc.styles['Normal']
    font = style.font
    font.name = FONT_NAME
    font.size = BODY_SIZE
    font.color.rgb = BLACK

    # Set page dimensions for first section
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # ── CERTIFICATE PAGE ─────────────────────────────────────────────────
    doc.add_paragraph()
    add_centered(doc, "School of Computing", size=Pt(13), bold=True, color=GREEN_SCHOOL)
    add_centered(doc, "Department of Artificial Intelligence and Machine Learning",
                 size=CHAPTER_TITLE_SIZE, bold=True, color=GREEN_SCHOOL)
    doc.add_paragraph()
    add_centered(doc, "CERTIFICATE", size=Pt(14), bold=True, color=BLACK)
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(
        'This is to certify that the project work entitled '
        '"AI/ML Powered Loan Risk Assessment System" is submitted by'
    )
    set_run_font(run, size=BODY_SIZE)

    add_centered(doc, "[Student Name 1] ([Roll No.])")
    add_centered(doc, "[Student Name 2] ([Roll No.])")
    add_centered(doc, "[Student Name 3] ([Roll No.])")
    add_centered(doc, "[Student Name 4] ([Roll No.])")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(
        'in partial fulfilment of the requirements for the award of the B.Tech. degree '
        'in Artificial Intelligence and Machine Learning for the academic year 2025–2026.'
    )
    set_run_font(run, size=BODY_SIZE)

    # ── DECLARATION PAGE ─────────────────────────────────────────────────
    add_section_break(doc)
    add_centered(doc, "DECLARATION", size=Pt(14), bold=True, color=BLACK)
    doc.add_paragraph()

    add_body(doc,
        'We hereby declare that the project entitled "AI/ML Powered Loan Risk Assessment System" '
        'is original and is submitted to our institution in partial fulfilment of the requirements '
        'for the award of the B.Tech. degree in Artificial Intelligence and Machine Learning. '
        'This project has not been previously submitted for any other degree or diploma. '
        'The work presented in this report is entirely our own, except where due acknowledgement has been made.'
    )

    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Place: [Place]")
    set_run_font(r, size=BODY_SIZE, bold=True)

    p = doc.add_paragraph()
    r = p.add_run("Date: [DD-MM-YYYY]")
    set_run_font(r, size=BODY_SIZE, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run("By")
    set_run_font(run, size=BODY_SIZE)

    for name in ["[Student Name 1] ([Roll No.])", "[Student Name 2] ([Roll No.])",
                  "[Student Name 3] ([Roll No.])", "[Student Name 4] ([Roll No.])"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(name)
        set_run_font(run, size=BODY_SIZE)

    # ── ACKNOWLEDGEMENT PAGE ─────────────────────────────────────────────
    add_section_break(doc)
    add_centered(doc, "ACKNOWLEDGEMENT", size=Pt(14), bold=True, color=BLACK)
    doc.add_paragraph()

    add_body(doc,
        'It is with immense pleasure that we express our sincere gratitude to our Project Guide, '
        '[Guide Name, Designation], who has guided us throughout the project. Their valuable support, '
        'encouragement, and constructive feedback have been instrumental in the successful completion of this work.'
    )
    add_body(doc,
        'We would like to thank [Deputy HOD / Coordinator names] for their support and valuable suggestions.'
    )
    add_body(doc,
        'Our deepest thanks to our Head of the Department, [HOD Name, Designation], '
        'for the inspiration and for providing all the necessary facilities and resources required for this project.'
    )
    add_body(doc,
        'We also extend our sincere thanks to [Dean / Registrar / Vice-Chancellor names] '
        'for their encouragement and support during the course of our project.'
    )
    add_body(doc,
        'Finally, we would like to thank the faculty members, lab technicians, non-teaching staff, '
        'and our friends who have directly or indirectly supported us in completing this project successfully.'
    )

    # ── ABSTRACT PAGE ────────────────────────────────────────────────────
    add_section_break(doc)
    add_centered(doc, "ABSTRACT", size=Pt(14), bold=True, color=BLACK)
    doc.add_paragraph()

    add_body(doc,
        'In the modern financial landscape, accurately assessing the credit risk of loan applicants is critical '
        'for minimizing defaults and ensuring responsible lending. This project, "AI/ML Powered Loan Risk Assessment '
        'System," addresses this challenge by building a comprehensive machine learning pipeline that predicts the '
        'likelihood of loan default based on applicant financial and demographic attributes. The system utilizes a '
        'synthetically generated dataset of 1,500 loan applicant records with 8 features including Age, Monthly Income, '
        'Loan Amount, Loan Term, Credit Score, Previous Defaults, Monthly Debt Payment, and Debt-to-Income (DTI) ratio. '
        'Preprocessing steps include handling missing values using median imputation via scikit-learn\'s SimpleImputer '
        'and stratified train-test splitting (80:20). Four classification algorithms were implemented and benchmarked — '
        'Logistic Regression, Decision Tree, Random Forest, and XGBoost — and evaluated using accuracy, precision, recall, '
        'F1-score, and ROC-AUC. The Random Forest classifier (150 trees, max depth 10, balanced class weights) was selected '
        'as the deployed model due to its superior generalization performance. The system was deployed as an interactive '
        'Streamlit web application integrated with MongoDB for customer KYC onboarding, document verification (Aadhaar and PAN '
        'validation), real-time risk prediction with SHAP-based explainability, EMI and affordability analysis, and downloadable '
        'assessment reports. The project demonstrates a practical end-to-end fintech risk intelligence solution.'
    )

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(
        "Keywords: "
    )
    set_run_font(r, size=BODY_SIZE, bold=True)
    r2 = p.add_run(
        "Machine Learning, Loan Risk Assessment, Random Forest, Classification, SHAP Explainability, "
        "Streamlit, MongoDB, KYC Verification, Predictive Analytics, Feature Engineering"
    )
    set_run_font(r2, size=BODY_SIZE)

    # ── LIST OF CONTENTS ─────────────────────────────────────────────────
    add_section_break(doc)
    add_centered(doc, "LIST OF CONTENTS", size=Pt(13), bold=True, color=BLACK)
    doc.add_paragraph()

    toc_entries = [
        ("LIST OF FIGURES", "i"),
        ("Chapter 1: Introduction", "01"),
        ("  1.1 Introduction", "01"),
        ("  1.2 Problem Statement", "02"),
        ("  1.3 Objectives of the Project", "03"),
        ("  1.4 Scope of the Project", "03"),
        ("Chapter 2: System Overview", "04"),
        ("  2.1 Existing System", "04"),
        ("  2.2 Limitations of Existing System", "04"),
        ("  2.3 Proposed System", "05"),
        ("  2.4 Software Requirements", "06"),
        ("  2.5 Hardware Requirements", "06"),
        ("Chapter 3: System Implementation", "07"),
        ("Chapter 4: System Architecture", "09"),
        ("Chapter 5: Data Preprocessing", "10"),
        ("Chapter 6: Methodology and Algorithms", "13"),
        ("Chapter 7: Results and Analysis", "17"),
        ("Chapter 8: Output Screens", "21"),
        ("Chapter 9: Conclusion", "22"),
        ("Chapter 10: Future Scope", "23"),
        ("Chapter 11: References", "24"),
    ]
    for entry, page in toc_entries:
        p = doc.add_paragraph()
        run = p.add_run(f"{entry}\t{page}")
        set_run_font(run, size=BODY_SIZE)

    # ── LIST OF FIGURES ──────────────────────────────────────────────────
    add_section_break(doc)
    add_centered(doc, "LIST OF FIGURES", size=Pt(13), bold=True, color=BLACK)
    doc.add_paragraph()

    figures = [
        "Fig 3.1: Development environment — Streamlit + VS Code",
        "Fig 4.1: System architecture flowchart",
        "Fig 5.1: Missing values heatmap",
        "Fig 5.2: Feature correlation matrix",
        "Fig 6.1: Random Forest model training output",
        "Fig 6.2: XGBoost model training output",
        "Fig 7.1: Confusion matrix — Random Forest",
        "Fig 7.2: Model comparison bar chart",
        "Fig 8.1: Loan Risk Assessment Dashboard",
        "Fig 8.2: Customer Onboarding KYC Portal",
        "Fig 8.3: AI-Powered Smart Suggestions",
        "Fig 8.4: Portfolio Analytics",
        "Fig 8.5: Model Intelligence",
        "Fig 8.6: Customer Database",
        "Fig 8.7: Tenure Comparison",
    ]
    for fig in figures:
        p = doc.add_paragraph()
        run = p.add_run(fig)
        set_run_font(run, size=BODY_SIZE)

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 1: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 1, "Introduction")

    add_heading1(doc, "1.1 Introduction")
    add_body(doc,
        'The global lending industry processes trillions of dollars in loan applications annually, making credit risk '
        'assessment one of the most consequential decisions in the financial ecosystem. Traditional approaches to loan '
        'evaluation rely heavily on manual underwriting, rule-based scorecards, and subjective human judgment. While these '
        'methods have served the industry for decades, they are inherently limited in their ability to capture complex, '
        'non-linear relationships among financial variables that influence borrower default probability.'
    )
    add_body(doc,
        'Machine learning (ML) offers a paradigm shift in credit risk analysis by enabling data-driven, automated '
        'assessment systems that learn patterns from historical applicant data. ML models can simultaneously consider '
        'dozens of financial and demographic attributes — such as income levels, existing debt burden, credit history, '
        'and repayment behavior — to produce probabilistic risk scores that are more nuanced and accurate than static '
        'rule-based systems. The ability of ensemble methods like Random Forest and gradient boosting frameworks like '
        'XGBoost to handle missing data, imbalanced classes, and non-linear feature interactions makes them particularly '
        'well-suited for credit risk classification.'
    )
    add_body(doc,
        'This project, titled "AI/ML Powered Loan Risk Assessment System," develops a complete end-to-end machine '
        'learning pipeline for predicting loan default risk. The system ingests applicant data comprising 8 key financial '
        'features, preprocesses it using median imputation, trains and benchmarks four classification algorithms '
        '(Logistic Regression, Decision Tree, Random Forest, and XGBoost), and deploys the best-performing model within '
        'a production-grade Streamlit web application backed by MongoDB for persistent customer management and KYC '
        'verification. The platform also integrates SHAP-based explainability, EMI affordability calculators, and a '
        'comprehensive smart advisory engine.'
    )

    add_heading1(doc, "1.2 Problem Statement")
    add_body(doc,
        'Lending institutions face a persistent challenge: how to accurately distinguish between applicants who will '
        'repay their loans and those who are likely to default. Incorrect assessments carry significant consequences — '
        'approving a high-risk borrower leads to financial losses through non-performing assets (NPAs), while rejecting '
        'creditworthy applicants results in lost revenue and customer dissatisfaction. Current manual underwriting '
        'processes are time-consuming (often taking days), inconsistent across different loan officers, and unable to '
        'scale with growing application volumes.'
    )
    add_body(doc,
        'The problem is further compounded by the complexity of modern financial profiles. Applicants present a '
        'multi-dimensional risk picture involving credit scores, debt-to-income ratios, employment stability, '
        'previous default history, and loan-to-income ratios — variables that interact in non-obvious ways. A machine '
        'learning solution is needed to: (a) automate the risk assessment process for speed and consistency, '
        '(b) capture non-linear patterns in applicant data that rule-based systems miss, (c) provide transparent, '
        'explainable risk scores that comply with responsible AI principles, and (d) integrate seamlessly into a '
        'customer-facing application with identity verification and financial advisory capabilities.'
    )

    add_heading1(doc, "1.3 Objectives of the Project")
    objectives = [
        "Collect and preprocess a comprehensive loan applicant dataset with 8 financial features and a binary risk label",
        "Handle missing values using median imputation and perform stratified train-test splitting to prevent data leakage",
        "Implement and benchmark four classification algorithms: Logistic Regression, Decision Tree, Random Forest, and XGBoost",
        "Evaluate all models using accuracy, precision, recall, F1-score, and ROC-AUC metrics to identify the best performer",
        "Deploy the selected model (Random Forest) as an interactive Streamlit web application with real-time prediction",
        "Integrate MongoDB for customer KYC onboarding with Aadhaar and PAN validation, document upload, and persistent storage",
        "Provide SHAP-based feature-level explainability for each prediction to ensure transparency",
        "Build a smart advisory engine with EMI calculation, tenure optimization, and actionable financial suggestions",
    ]
    for obj in objectives:
        add_list_item(doc, obj)

    add_heading1(doc, "1.4 Scope of the Project")
    add_body(doc,
        'This project covers the complete machine learning lifecycle for binary loan default classification, including: '
        'data generation and preprocessing, exploratory analysis, model training and hyperparameter selection, '
        'multi-model benchmarking, model deployment via Streamlit, and integration with MongoDB for KYC and '
        'application tracking. The system uses Python 3.x with scikit-learn, XGBoost, SHAP, Plotly, and Streamlit. '
        'The dataset comprises 1,500 synthetically generated records with realistic distributions for loan applicant '
        'features.'
    )
    add_body(doc,
        'Out of scope: real-time streaming data ingestion from external banking APIs, regulatory compliance testing '
        '(e.g., GDPR, RBI guidelines), production-grade security audits, and mobile application deployment. The '
        'system is designed as a proof-of-concept demonstrating the viability of ML-driven credit risk assessment.'
    )

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 2: SYSTEM OVERVIEW
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 2, "System Overview")

    add_heading1(doc, "2.1 Existing System")
    add_body(doc,
        'The existing loan risk assessment process in most traditional financial institutions relies on manual '
        'underwriting performed by loan officers. Applicants submit physical or digital applications along with '
        'income proofs, credit reports, and identity documents. A loan officer manually reviews each application, '
        'checks the applicant\'s CIBIL or credit bureau score, compares their debt-to-income ratio against pre-set '
        'thresholds, and applies rule-based scorecards to arrive at an approval or rejection decision. This process '
        'is heavily dependent on the individual officer\'s experience and judgment, and typically takes 2–5 business '
        'days per application.'
    )

    add_heading1(doc, "2.2 Limitations of Existing System")
    limitations = [
        "Slow processing: Manual review of each application takes 2–5 days, creating bottlenecks during high-volume periods",
        "Subjective decisions: Different loan officers may evaluate the same applicant differently, leading to inconsistent outcomes",
        "Limited pattern recognition: Rule-based scorecards use simple thresholds and cannot capture complex, non-linear interactions between financial variables",
        "No real-time analysis: Applicants receive delayed feedback, reducing customer satisfaction and increasing drop-off rates",
        "Lack of explainability: Rejection reasons are often vague, making it difficult for applicants to understand or improve their profiles",
        "Scalability issues: As application volumes grow, hiring more officers becomes cost-prohibitive",
    ]
    for lim in limitations:
        add_list_item(doc, lim)

    add_heading1(doc, "2.3 Proposed System")
    add_body(doc,
        'The proposed system replaces manual underwriting with an AI/ML-powered automated risk assessment pipeline. '
        'The system follows a modular architecture:'
    )
    add_body(doc,
        '(1) Customer Onboarding Module: A KYC portal where customers register with personal, financial, and identity '
        'information. The system validates Aadhaar (12-digit format, Verhoeff check) and PAN (AAAAA9999A format) card '
        'numbers programmatically and stores documents (Aadhaar card, PAN card, salary slips) as base64-encoded data '
        'in MongoDB.'
    )
    add_body(doc,
        '(2) Data Preprocessing Pipeline: Input features are aligned to the training schema (8 features: Age, Monthly '
        'Income, Loan Amount, Loan Term Months, Credit Score, Previous Defaults, Monthly Debt Payment, DTI). A fitted '
        'SimpleImputer (median strategy) handles any missing values consistently between training and inference.'
    )
    add_body(doc,
        '(3) ML Prediction Engine: A serialized Random Forest classifier (150 trees, max depth 10, balanced class weights) '
        'produces default probability scores. These probabilities are converted to a 0–100 risk score and mapped to a '
        'letter grade system (A+ through E) with corresponding indicative interest rates.'
    )
    add_body(doc,
        '(4) Explainability Layer: SHAP TreeExplainer computes feature-level contributions for each prediction, showing '
        'which variables pushed the risk score higher or lower.'
    )
    add_body(doc,
        '(5) Advisory Engine: An intelligent suggestion generator analyzes EMI affordability, DTI thresholds, credit '
        'score impact, previous default history, and loan-to-income ratio to produce actionable, categorized recommendations.'
    )

    add_heading1(doc, "2.4 Software Requirements")
    sw_items = [
        "Operating System: macOS / Windows 10 / Linux (Ubuntu 20.04+)",
        "Programming Language: Python 3.10+",
        "Libraries: Pandas ≥2.0, NumPy ≥1.24, scikit-learn ≥1.3, XGBoost ≥1.7, SHAP ≥0.42, Matplotlib ≥3.7, Seaborn ≥0.12, Plotly ≥5.15, Joblib ≥1.3",
        "Web Framework: Streamlit ≥1.28",
        "Database: MongoDB (via PyMongo ≥4.5)",
        "IDE: Visual Studio Code / Jupyter Notebook",
        "Data Format: CSV (Comma Separated Values)",
    ]
    for item in sw_items:
        add_list_item(doc, item, bold=True)

    add_heading1(doc, "2.5 Hardware Requirements")
    hw_items = [
        "Processor: Intel Core i5 (8th generation) or Apple M1 or higher",
        "RAM: 8 GB or higher (16 GB recommended for XGBoost training)",
        "Storage: 256 GB SSD or higher",
        "System Type: 64-bit operating system",
        "Network: Internet connection for package installation and MongoDB Atlas (if cloud-hosted)",
    ]
    for item in hw_items:
        add_list_item(doc, item, bold=True)

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 3: SYSTEM IMPLEMENTATION
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 3, "System Implementation")

    add_heading1(doc, "3.1 Overview of Development Tools")

    add_heading2(doc, "3.1.1 Streamlit — Web Application Framework")
    add_body(doc,
        'Streamlit is an open-source Python framework designed for building interactive data applications with minimal '
        'frontend code. It was chosen for this project because it allows rapid prototyping of data-driven web interfaces '
        'using pure Python — no HTML, CSS, or JavaScript is required for the core functionality. Streamlit provides native '
        'support for widgets (sliders, dropdowns, file uploaders), real-time reactivity, and seamless integration with '
        'Plotly for interactive visualizations. The application uses custom CSS injection via st.markdown() with '
        'unsafe_allow_html=True to implement a premium dark-themed UI with glassmorphism effects, gradient accents, '
        'and responsive grid layouts.'
    )

    add_heading2(doc, "3.1.2 scikit-learn — Machine Learning Library")
    add_body(doc,
        'scikit-learn is the primary ML library used for model training, preprocessing, and evaluation. It provides '
        'the RandomForestClassifier, LogisticRegression, and DecisionTreeClassifier algorithms, as well as the '
        'SimpleImputer for missing value handling, train_test_split for data partitioning, and metrics modules '
        '(accuracy_score, precision_score, recall_score, f1_score, roc_auc_score) for model evaluation. All models '
        'and preprocessing artifacts are serialized using joblib for efficient loading during inference.'
    )

    add_heading2(doc, "3.1.3 MongoDB + PyMongo — Database Layer")
    add_body(doc,
        'MongoDB is a NoSQL document database used to store customer KYC records, identity documents (as base64-encoded '
        'binary data), and loan application assessment results. PyMongo provides the Python driver for MongoDB operations. '
        'The DatabaseManager class implements connection management with timeout handling, index creation for performance '
        '(unique indexes on aadhaar_number and pan_number), CRUD operations for customers and applications, and automatic '
        'application reference ID generation (format: LRA-YYYY-NNNNN).'
    )

    add_heading1(doc, "3.2 Dataset Description")
    add_body(doc,
        'The dataset used in this project is a synthetically generated loan applicant dataset created using NumPy\'s '
        'random distributions to simulate realistic financial profiles. The dataset contains 1,500 records with 8 '
        'input features and 1 binary target variable (Risk_Label). Intentional missing values (~2% per feature) are '
        'injected to test the imputation pipeline\'s robustness.'
    )

    add_table(doc,
        ["Feature", "Type", "Description", "Range"],
        [
            ["Age", "Integer", "Applicant's age in years", "20 – 67"],
            ["Monthly_Income", "Float", "Monthly income in INR", "₹12,000 – ₹250,000"],
            ["Loan_Amount", "Float", "Loan amount requested in INR", "₹20,000 – ₹50,00,000"],
            ["Loan_Term_Months", "Integer", "Repayment duration in months", "12 – 360"],
            ["Credit_Score", "Integer", "CIBIL credit score", "300 – 850"],
            ["Previous_Defaults", "Integer", "Count of past loan defaults", "0 – 4"],
            ["Monthly_Debt_Payment", "Float", "Existing monthly debt obligations", "₹600 – ₹162,000"],
            ["DTI", "Float", "Debt-to-Income ratio percentage", "5% – 65%"],
            ["Risk_Label", "Binary", "Target — 0: Low Risk, 1: High Risk", "0 or 1"],
        ]
    )

    add_body(doc,
        'Target Distribution: The dataset contains 317 Low Risk (0) and 1,183 High Risk (1) records, '
        'reflecting a class imbalance ratio of approximately 1:3.7. This imbalance is handled via '
        'the class_weight="balanced" parameter in the Random Forest classifier and stratified splitting.'
    )
    add_body(doc,
        'Missing Values: Approximately 2% of values are missing across all feature columns (23–38 missing values '
        'per column out of 1,500 records). The Risk_Label target column has no missing values.'
    )

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 4: SYSTEM ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 4, "System Architecture")

    add_body(doc,
        'The system follows a modular, layered architecture that separates concerns across data management, '
        'preprocessing, model inference, explainability, and presentation layers. The end-to-end workflow '
        'proceeds through the following stages:'
    )
    doc.add_paragraph()

    # Architecture flowchart (text-based as in template)
    flow_steps = [
        ("[ Customer Registration (KYC Portal) ]", True),
        ("↓", False),
        ("[ Data Storage (MongoDB) ]", True),
        ("↓", False),
        ("[ Customer Search & Data Retrieval ]", True),
        ("↓", False),
        ("[ Feature Engineering (DTI Calculation, Schema Alignment) ]", True),
        ("↓", False),
        ("[ Data Preprocessing (Median Imputation) ]", True),
        ("↓", False),
        ("[ ML Inference (Random Forest Classifier) ]", True),
        ("↓", False),
        ("[ Risk Scoring & Grade Assignment (A+ to E) ]", True),
        ("↓", False),
        ("[ SHAP Explainability (Feature Contributions) ]", True),
        ("↓", False),
        ("[ Advisory Engine (EMI, Tenure, Suggestions) ]", True),
        ("↓", False),
        ("[ Report Generation & Visualization Dashboard ]", True),
    ]
    for text, is_bold in flow_steps:
        add_centered(doc, text, bold=is_bold)

    doc.add_paragraph()
    add_body(doc,
        'The architecture comprises six Python modules: app.py (Streamlit frontend, 1,700+ lines), '
        'src/preprocessing.py (feature engineering and imputation utilities), src/train_model.py (training pipeline), '
        'src/evaluate_model.py (multi-model benchmarking), src/prediction.py (inference engine with SHAP), '
        'src/database.py (MongoDB operations), and src/validators.py (Aadhaar/PAN/file validation). Serialized '
        'model artifacts (Random Forest PKL, imputer PKL, feature list PKL) are stored in the model/ directory.'
    )

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 5: DATA PREPROCESSING
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 5, "Data Preprocessing")

    add_heading1(doc, "5.1 Introduction")
    add_body(doc,
        'Data preprocessing is a critical step in any machine learning pipeline, as the quality and consistency of '
        'the input data directly impacts model performance. This chapter describes the preprocessing techniques '
        'applied to the loan applicant dataset before model training and during real-time inference.'
    )

    add_heading1(doc, "5.2 Handling Missing Values")
    add_body(doc,
        'The dataset contains approximately 2% missing values across all 8 feature columns, introduced intentionally '
        'during dataset generation to simulate real-world data quality issues. Missing values were handled using '
        'scikit-learn\'s SimpleImputer with a median imputation strategy. The median was chosen over the mean because '
        'it is robust to outliers — financial features like Monthly_Income and Loan_Amount often contain extreme values '
        'that would skew mean-based imputation.'
    )
    add_body(doc,
        'The imputer was fitted exclusively on the training set and then applied (transform only) to the test set '
        'and to all real-time inference inputs. This prevents data leakage — a common pitfall where information from '
        'the test set inadvertently influences the training process. The fitted imputer is serialized as '
        'loan_risk_imputer.pkl for consistent use during deployment.'
    )

    add_heading1(doc, "5.3 Data Cleaning")
    add_body(doc,
        'Beyond missing value imputation, the preprocessing pipeline ensures data type consistency (all features cast '
        'to float), validates that feature names match the expected schema (EXPECTED_FEATURES list in preprocessing.py), '
        'and clips extreme values to realistic ranges. The DTI (Debt-to-Income) ratio is computed dynamically as '
        '(Monthly_Debt_Payment / Monthly_Income) × 100 when not provided, ensuring consistency between training '
        'data and inference inputs.'
    )

    add_heading1(doc, "5.4 Outlier Detection and Range Validation")
    add_body(doc,
        'Outlier detection is performed through range validation. Key features are constrained to realistic bounds: '
        'Age (18–75), Monthly Income (₹5,000–₹250,000), Credit Score (300–900), Loan Amount (₹10,000–₹50,000,000), '
        'and Previous Defaults (0–10). The Streamlit input widgets enforce these constraints through min_value and '
        'max_value parameters, preventing invalid data from entering the prediction pipeline. During training, '
        'the synthetic data generator uses np.clip() to enforce realistic distributions.'
    )

    add_heading1(doc, "5.5 Feature Engineering / Encoding")
    add_body(doc,
        'The primary engineered feature is the DTI (Debt-to-Income) ratio, calculated as '
        '(Monthly_Debt_Payment / Monthly_Income) × 100. This derived metric is a critical indicator of an '
        'applicant\'s ability to service additional debt and is widely used in the banking industry. '
        'All 8 input features are numerical, so no categorical encoding (one-hot or label encoding) was required. '
        'Feature scaling was not applied because tree-based models (Random Forest, Decision Tree, XGBoost) are '
        'invariant to feature scale — they make splits based on feature values, not distances.'
    )

    add_heading1(doc, "5.6 Data Visualization")
    add_body(doc,
        'Exploratory data analysis (EDA) was performed using Plotly interactive charts within the Streamlit dashboard. '
        'Key visualizations include: (1) Class distribution pie chart showing the 21.1% vs 78.9% split between Low Risk '
        'and High Risk labels; (2) Credit score distribution histogram colored by risk label, revealing that lower '
        'credit scores strongly correlate with high risk; (3) Scatter plot of Monthly Income vs. Loan Amount by risk '
        'label; (4) DTI distribution histogram by risk class; and (5) Feature importance bar charts from the trained '
        'Random Forest model.'
    )

    add_heading1(doc, "5.7 Train-Test Split")
    add_body(doc,
        'The dataset was split into 80% training (1,200 records) and 20% test (300 records) subsets using '
        'scikit-learn\'s train_test_split with random_state=42 for reproducibility. Stratified splitting '
        '(stratify=y) was applied to ensure that the class distribution (Low Risk vs. High Risk) is preserved '
        'in both the training and test sets. This is especially important given the imbalanced nature of the '
        'dataset (1:3.7 ratio).'
    )

    add_heading1(doc, "5.8 Summary")
    add_body(doc,
        'The preprocessing pipeline transforms raw applicant data into a clean, consistent, model-ready format. '
        'Median imputation handles missing values without data leakage, DTI is dynamically computed as an engineered '
        'feature, range validation prevents invalid inputs, and stratified splitting ensures balanced evaluation. '
        'The fitted imputer and feature list are serialized alongside the model for deployment consistency.'
    )

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 6: METHODOLOGY AND ALGORITHMS
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 6, "Methodology and Algorithms")

    add_heading1(doc, "6.1 Introduction")
    add_body(doc,
        'This chapter describes the machine learning algorithms implemented in the project for loan default '
        'risk classification. Four supervised classification algorithms were selected to cover a spectrum of '
        'complexity: a linear model (Logistic Regression), a single tree model (Decision Tree), an ensemble '
        'bagging model (Random Forest), and a gradient boosting model (XGBoost). Each algorithm was trained '
        'on the imputed training set and evaluated on the held-out test set using identical metrics.'
    )

    add_heading1(doc, "6.2 Classification Techniques")

    add_heading2(doc, "6.2.1 Logistic Regression")
    add_body_bold_prefix(doc, "Working: ",
        "Logistic Regression is a linear classification algorithm that models the probability of a binary outcome "
        "using the logistic (sigmoid) function. It computes a weighted linear combination of input features and "
        "passes the result through the sigmoid function σ(z) = 1 / (1 + e^(-z)) to produce a probability between "
        "0 and 1. The decision boundary is a hyperplane in the feature space. The model was configured with "
        "max_iter=1000 and random_state=42."
    )
    add_body_bold_prefix(doc, "Advantages: ",
        "Fast training and inference, interpretable coefficients, works well as a baseline model, and performs "
        "reasonably when features have approximately linear relationships with the log-odds of the outcome."
    )
    add_body_bold_prefix(doc, "Application in Project: ",
        "Used as the baseline model for comparison. It provides a reference point to measure the improvement "
        "offered by more complex algorithms."
    )

    add_heading2(doc, "6.2.2 Decision Tree Classifier")
    add_body_bold_prefix(doc, "Working: ",
        "A Decision Tree recursively partitions the feature space by selecting the feature and threshold at each "
        "node that maximizes information gain (or minimizes Gini impurity). The tree grows until a stopping criterion "
        "is met (max_depth=6 in this project), and each leaf node represents a class prediction. The model was "
        "configured with max_depth=6 and random_state=42."
    )
    add_body_bold_prefix(doc, "Advantages: ",
        "Highly interpretable (can be visualized as a tree), handles non-linear relationships, requires no feature "
        "scaling, and can model complex decision boundaries."
    )
    add_body_bold_prefix(doc, "Application in Project: ",
        "Used to demonstrate the improvement from single-tree to ensemble methods (Random Forest), and to identify "
        "the most discriminative features through feature importance analysis."
    )

    add_heading1(doc, "6.3 Ensemble Methods")

    add_heading2(doc, "6.3.1 Random Forest Classifier (Deployed Model)")
    add_body_bold_prefix(doc, "Working: ",
        "Random Forest is a bagging ensemble that trains multiple decision trees on bootstrapped subsets of the "
        "training data. Each tree also considers only a random subset of features at each split point, reducing "
        "correlation between trees. The final prediction is made by majority voting across all trees. "
        "Configuration: n_estimators=150, max_depth=10, min_samples_split=5, class_weight='balanced', random_state=42."
    )
    add_body_bold_prefix(doc, "Advantages: ",
        "Robust against overfitting due to ensemble averaging, handles missing values and imbalanced classes gracefully, "
        "provides feature importance rankings, and achieves high accuracy on tabular data without extensive hyperparameter tuning."
    )
    add_body_bold_prefix(doc, "Application in Project: ",
        "Selected as the deployed production model due to its superior performance across all evaluation metrics. "
        "The class_weight='balanced' parameter automatically adjusts sample weights inversely proportional to class "
        "frequency, addressing the 1:3.7 class imbalance. The trained model is serialized as loan_risk_random_forest.pkl."
    )

    add_heading2(doc, "6.3.2 XGBoost (eXtreme Gradient Boosting)")
    add_body_bold_prefix(doc, "Working: ",
        "XGBoost is a gradient boosting framework that sequentially trains decision trees, where each new tree "
        "corrects the errors (residuals) of the previous ensemble. It uses second-order Taylor expansion of the "
        "loss function for efficient optimization and includes built-in L1/L2 regularization to prevent overfitting. "
        "Configuration: eval_metric='logloss', random_state=42."
    )
    add_body_bold_prefix(doc, "Advantages: ",
        "State-of-the-art performance on structured/tabular data, handles missing values natively, provides "
        "regularization to control model complexity, and supports parallel computation for fast training."
    )

    add_heading1(doc, "6.4 SHAP Explainability")
    add_body(doc,
        'Beyond prediction, the system provides model explainability using SHAP (SHapley Additive exPlanations). '
        'SHAP TreeExplainer is used to compute the contribution of each feature to individual predictions. '
        'For each loan assessment, the system shows which features pushed the risk score higher (e.g., low '
        'credit score, high DTI) and which pulled it lower (e.g., high income, zero previous defaults). '
        'This transparency is critical for responsible AI deployment in financial decision-making.'
    )

    add_heading1(doc, "6.5 Model Evaluation Metrics")
    metrics_list = [
        "Accuracy — The proportion of all predictions (both risk and non-risk) that are correct",
        "Precision — Of all applicants predicted as High Risk, the proportion that are actually High Risk",
        "Recall — Of all actual High Risk applicants, the proportion correctly identified by the model",
        "F1-Score — The harmonic mean of precision and recall, balancing both in a single metric",
        "ROC-AUC — Area Under the Receiver Operating Characteristic curve, measuring the model's ability to discriminate between classes across all threshold values",
    ]
    for m in metrics_list:
        add_list_item(doc, m)

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 7: RESULTS AND ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 7, "Results and Analysis")

    add_heading1(doc, "7.1 Introduction")
    add_body(doc,
        'This chapter presents the experimental results of all four classification models trained on the '
        'loan applicant dataset. Each model was trained on the 80% training split (1,200 records) and '
        'evaluated on the 20% held-out test split (300 records). The evaluation compares models across '
        'five metrics: accuracy, precision, recall, F1-score, and ROC-AUC.'
    )

    add_heading1(doc, "7.2 Experimental Setup")
    add_body(doc,
        'All models were trained using the same preprocessed dataset with median-imputed features. '
        'The train-test split ratio was 80:20 with stratification on the target variable (Risk_Label) '
        'and random_state=42 for reproducibility. No cross-validation was applied during final evaluation; '
        'however, the Random Forest model\'s internal bootstrap aggregation provides implicit variance reduction. '
        'The evaluation metrics used are: Accuracy, Precision, Recall, F1-Score, and ROC-AUC.'
    )

    add_heading2(doc, "7.3 Logistic Regression Results")
    add_body(doc,
        'Logistic Regression served as the baseline linear model. Being a linear classifier, it assumes a '
        'linear relationship between features and the log-odds of the target. While it achieved reasonable '
        'accuracy, it was outperformed by tree-based models due to the non-linear feature interactions present '
        'in the loan risk data (e.g., the interaction between Credit Score and DTI).'
    )

    add_heading2(doc, "7.4 Decision Tree Results")
    add_body(doc,
        'The Decision Tree classifier with max_depth=6 showed improved performance over Logistic Regression '
        'by capturing non-linear decision boundaries. However, as a single tree, it is more prone to overfitting '
        'on the training data compared to ensemble methods. Its primary value was in demonstrating the baseline '
        'performance of tree-based approaches.'
    )

    add_heading2(doc, "7.5 Random Forest Results (Deployed Model)")
    add_body(doc,
        'The Random Forest classifier with 150 estimators, max_depth=10, and balanced class weights achieved '
        'the best overall performance. The ensemble averaging of 150 decorrelated trees significantly reduced '
        'variance and overfitting compared to the single Decision Tree. The balanced class weights compensated '
        'for the 1:3.7 class imbalance, improving recall for the minority class (Low Risk).'
    )

    add_heading2(doc, "7.6 XGBoost Results")
    add_body(doc,
        'XGBoost demonstrated competitive performance with the Random Forest, achieving strong ROC-AUC scores '
        'due to its gradient boosting approach. It excels at sequentially correcting the errors of weak learners '
        'but requires more careful hyperparameter tuning to avoid overfitting on small datasets.'
    )

    add_heading1(doc, "7.5 Comparison of Models")
    add_body(doc, "The following table summarizes the performance of all four models on the test set:")
    doc.add_paragraph()

    add_table(doc,
        ["Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"],
        [
            ["Logistic Regression", "0.8033", "0.8750", "0.8565", "0.8657", "0.7728"],
            ["Decision Tree", "0.8700", "0.9109", "0.9156", "0.9133", "0.8166"],
            ["Random Forest", "0.9233", "0.9433", "0.9578", "0.9505", "0.9325"],
            ["XGBoost", "0.9100", "0.9387", "0.9451", "0.9419", "0.9216"],
        ]
    )

    add_body(doc,
        'The Random Forest classifier outperformed all other models across every metric. It achieved the highest '
        'accuracy (92.33%), precision (94.33%), recall (95.78%), F1-score (95.05%), and ROC-AUC (93.25%). This '
        'confirms that ensemble bagging with balanced class weights is the most effective approach for this '
        'loan risk classification task. Accordingly, the Random Forest model was selected for production deployment.'
    )

    add_heading1(doc, "7.6 Key Findings")
    findings = [
        "Credit Score is the most influential feature in predicting loan default risk, contributing the highest feature importance in the Random Forest model",
        "DTI (Debt-to-Income) ratio is the second most critical predictor — applicants with DTI above 40% show significantly higher default rates",
        "Random Forest with balanced class weights generalizes best, achieving the highest F1-Score and ROC-AUC among all tested models",
        "Previous Defaults has a strong positive correlation with high risk — applicants with 2 or more defaults are almost always classified as high risk",
        "The ensemble approach (Random Forest) reduces overfitting compared to the single Decision Tree, improving test set performance by ~5% in accuracy",
    ]
    for f in findings:
        add_list_item(doc, f)

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 8: OUTPUT SCREENS
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 8, "Output Screens")

    add_body(doc,
        'This chapter presents screenshots of the application\'s key output screens, demonstrating the system\'s '
        'functionality across all major modules. The screenshots below showcase the Streamlit web application\'s '
        'dark-themed UI with interactive visualizations, real-time risk predictions, and comprehensive assessment reports.'
    )

    doc.add_paragraph()
    add_heading2(doc, "Loan Risk Assessment Dashboard")
    try:
        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")
    add_body(doc, "Risk Score Gauge, KPI tiles, and Financial Summary.")
    doc.add_paragraph()
    add_heading2(doc, "Customer Onboarding KYC Portal")
    try:
        doc.add_picture("2_Customer_Onboarding.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 2_Customer_Onboarding.png]")
    add_body(doc, "Registration form with Aadhaar/PAN validation.")
    doc.add_paragraph()
    add_heading2(doc, "AI-Powered Smart Suggestions")
    try:
        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")
    add_body(doc, "Categorized advisory cards (Critical, Warning, Positive, Tip).")
    doc.add_paragraph()
    add_heading2(doc, "Portfolio Analytics")
    try:
        doc.add_picture("4_Portfolio_Analytics.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 4_Portfolio_Analytics.png]")
    add_body(doc, "Class distribution pie chart, Credit Score histogram, Income vs Loan scatter plot.")
    doc.add_paragraph()
    add_heading2(doc, "Model Intelligence")
    try:
        doc.add_picture("5_Model_Intelligence.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 5_Model_Intelligence.png]")
    add_body(doc, "Feature importance bar chart, Risk Grade Mapping table.")
    doc.add_paragraph()
    add_heading2(doc, "Customer Database")
    try:
        doc.add_picture("6_Customer_Database.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 6_Customer_Database.png]")
    add_body(doc, "Registered customers table with document status and assessment counts.")
    doc.add_paragraph()
    add_heading2(doc, "Tenure Comparison")
    try:
        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")
    add_body(doc, "Tenure Comparison Table and Amortization Schedule.")
    doc.add_paragraph()
    try:
        doc.add_picture("5_Model_Intelligence.png", width=Inches(6.0))
    except:
        add_body(doc, "[Missing Model Training Screenshot]")

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 9: CONCLUSION
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 9, "Conclusion")

    add_body(doc,
        'This project successfully developed and deployed an AI/ML Powered Loan Risk Assessment System that '
        'automates the credit risk evaluation process using machine learning. The system addresses the key '
        'limitations of traditional manual underwriting — subjectivity, inconsistency, and slow processing — '
        'by providing instant, data-driven risk assessments backed by transparent, explainable predictions.'
    )
    add_body(doc,
        'The project implemented a complete machine learning pipeline covering data preprocessing (median '
        'imputation with data leakage prevention), model training and benchmarking (four classification algorithms), '
        'and production deployment (Streamlit web application with MongoDB integration). The Random Forest '
        'classifier was identified as the best-performing model with an accuracy of 92.33%, precision of 94.33%, '
        'recall of 95.78%, F1-score of 95.05%, and ROC-AUC of 93.25%.'
    )
    add_body(doc,
        'Beyond prediction, the system provides significant practical value through its integrated modules: '
        'the KYC onboarding portal with Aadhaar and PAN validation ensures compliance with identity verification '
        'requirements; the SHAP explainability layer provides transparency into model decisions; the advisory engine '
        'generates actionable financial suggestions (EMI optimization, tenure comparison, debt reduction strategies); '
        'and the downloadable assessment reports enable offline review and record-keeping.'
    )
    add_body(doc,
        'The project demonstrates that machine learning, when combined with thoughtful system design and responsible '
        'AI practices, can significantly enhance the speed, accuracy, and transparency of financial risk assessment. '
        'The modular architecture ensures that individual components (model, database, frontend) can be independently '
        'upgraded or replaced without disrupting the overall system.'
    )

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 10: FUTURE SCOPE
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 10, "Future Scope")

    future_items = [
        "Integrating real-time credit bureau data feeds (CIBIL, Experian, CRIF) for live credit score verification and automated data enrichment during the assessment process",
        "Applying deep learning models (e.g., neural networks, autoencoders for anomaly detection) to capture more complex patterns in high-dimensional applicant data and potentially improve classification accuracy beyond the current 92.33%",
        "Deploying the application as a cloud-hosted service on platforms like AWS, GCP, or Azure with load balancing, auto-scaling, and HTTPS encryption for production-grade availability and security",
        "Expanding the dataset with real-world lending data from banking institutions and incorporating additional features such as employment tenure, property ownership, education level, and transaction history",
        "Building an automated MLOps pipeline with model versioning, A/B testing, drift detection, and automated retraining triggers when model performance degrades below a threshold",
        "Implementing a mobile application (React Native or Flutter) to enable field agents and customers to submit and track loan applications from mobile devices",
        "Adding multi-language support and role-based access control (admin, loan officer, customer) to the web application for enterprise deployment",
    ]
    for item in future_items:
        add_list_item(doc, item)

    # ══════════════════════════════════════════════════════════════════════
    #  CHAPTER 11: REFERENCES
    # ══════════════════════════════════════════════════════════════════════
    add_chapter_title(doc, 11, "References")

    references = [
        '1. L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.',
        '2. T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 785–794, 2016.',
        '3. S. M. Lundberg and S. I. Lee, "A Unified Approach to Interpreting Model Predictions," Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017.',
        '4. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
        '5. Streamlit Inc., "Streamlit — The Fastest Way to Build Data Apps," streamlit.io, 2023.',
        '6. MongoDB Inc., "The MongoDB Database," mongodb.com, 2023.',
        '7. Reserve Bank of India, "Guidelines on Fair Practices Code for Lenders," RBI Circular, 2024.',
        '8. A. Géron, "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow," O\'Reilly Media, 3rd Edition, 2022.',
        '9. J. Brownlee, "Imbalanced Classification with Python: Better Metrics, Balance Skewed Classes, and Apply Cost-Sensitive Learning," Machine Learning Mastery, 2020.',
        '10. W. McKinney, "Python for Data Analysis," O\'Reilly Media, 3rd Edition, 2022.',
    ]
    for ref in references:
        p = doc.add_paragraph()
        run = p.add_run(ref)
        set_run_font(run, size=BODY_SIZE)

    # ── SAVE ─────────────────────────────────────────────────────────────
    output_path = "ML_Project_Report.docx"
    doc.save(output_path)
    print(f"[SUCCESS] Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_report()
