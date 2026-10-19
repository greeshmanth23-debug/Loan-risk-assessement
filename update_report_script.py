import re

with open("generate_report.py", "r") as f:
    content = f.read()

replacements = [
    (r'add_body\(doc, "\[Insert Screenshot: Loan Risk Assessment Dashboard — Risk Score Gauge, KPI tiles, and Financial Summary\]"\)',
     'try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")'),
    
    (r'add_body\(doc, "\[Insert Screenshot: Customer Onboarding KYC Portal — Registration form with Aadhaar/PAN validation\]"\)',
     'try:\n        doc.add_picture("2_Customer_Onboarding.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 2_Customer_Onboarding.png]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: AI-Powered Smart Suggestions — Categorized advisory cards \(Critical, Warning, Positive, Tip\)\]"\)',
     'try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing AI Suggestions Screenshot]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: Portfolio Analytics — Class distribution pie chart, Credit Score histogram, Income vs Loan scatter plot\]"\)',
     'try:\n        doc.add_picture("4_Portfolio_Analytics.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 4_Portfolio_Analytics.png]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: Model Intelligence — Feature importance bar chart, Risk Grade Mapping table\]"\)',
     'try:\n        doc.add_picture("5_Model_Intelligence.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 5_Model_Intelligence.png]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: Customer Database — Registered customers table with document status and assessment counts\]"\)',
     'try:\n        doc.add_picture("6_Customer_Database.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 6_Customer_Database.png]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: Tenure Comparison Table and Amortization Schedule\]"\)',
     'try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing Tenure Comparison Screenshot]")'),
     
    (r'add_body\(doc, "\[Insert Screenshot: Model Training Output — Classification report and ROC-AUC score\]"\)',
     'try:\n        doc.add_picture("5_Model_Intelligence.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing Model Training Screenshot]")')
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open("generate_report.py", "w") as f:
    f.write(content)

print("Updated generate_report.py")
