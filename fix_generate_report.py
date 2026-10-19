import re
import os

with open("generate_report.py", "r") as f:
    content = f.read()

# I need to revert my changes or just manually replace the tries with what the user wants.
# Let's write the correct blocks directly.

new_content = re.sub(
    r'try:\s*doc\.add_picture\("1_Loan_Risk_Assessment\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing 1_Loan_Risk_Assessment\.png\]"\)',
    r'add_heading2(doc, "Loan Risk Assessment Dashboard")\n    try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")\n    add_body(doc, "Risk Score Gauge, KPI tiles, and Financial Summary.")',
    content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("2_Customer_Onboarding\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing 2_Customer_Onboarding\.png\]"\)',
    r'add_heading2(doc, "Customer Onboarding KYC Portal")\n    try:\n        doc.add_picture("2_Customer_Onboarding.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 2_Customer_Onboarding.png]")\n    add_body(doc, "Registration form with Aadhaar/PAN validation.")',
    new_content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("1_Loan_Risk_Assessment\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing AI Suggestions Screenshot\]"\)',
    r'add_heading2(doc, "AI-Powered Smart Suggestions")\n    try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")\n    add_body(doc, "Categorized advisory cards (Critical, Warning, Positive, Tip).")',
    new_content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("4_Portfolio_Analytics\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing 4_Portfolio_Analytics\.png\]"\)',
    r'add_heading2(doc, "Portfolio Analytics")\n    try:\n        doc.add_picture("4_Portfolio_Analytics.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 4_Portfolio_Analytics.png]")\n    add_body(doc, "Class distribution pie chart, Credit Score histogram, Income vs Loan scatter plot.")',
    new_content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("5_Model_Intelligence\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing 5_Model_Intelligence\.png\]"\)',
    r'add_heading2(doc, "Model Intelligence")\n    try:\n        doc.add_picture("5_Model_Intelligence.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 5_Model_Intelligence.png]")\n    add_body(doc, "Feature importance bar chart, Risk Grade Mapping table.")',
    new_content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("6_Customer_Database\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing 6_Customer_Database\.png\]"\)',
    r'add_heading2(doc, "Customer Database")\n    try:\n        doc.add_picture("6_Customer_Database.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 6_Customer_Database.png]")\n    add_body(doc, "Registered customers table with document status and assessment counts.")',
    new_content, count=1
)

new_content = re.sub(
    r'try:\s*doc\.add_picture\("1_Loan_Risk_Assessment\.png", width=Inches\(6\.0\)\)\s*except:\s*add_body\(doc, "\[Missing Tenure Comparison Screenshot\]"\)',
    r'add_heading2(doc, "Tenure Comparison")\n    try:\n        doc.add_picture("1_Loan_Risk_Assessment.png", width=Inches(6.0))\n    except:\n        add_body(doc, "[Missing 1_Loan_Risk_Assessment.png]")\n    add_body(doc, "Tenure Comparison Table and Amortization Schedule.")',
    new_content, count=1
)

with open("generate_report.py", "w") as f:
    f.write(new_content)

print("generate_report.py updated with headings and captions!")
