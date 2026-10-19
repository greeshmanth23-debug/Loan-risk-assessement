"""
AI/ML Powered Loan Risk Assessment System
With MongoDB-backed Customer KYC Onboarding, Smart Prediction & Advisory Engine
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.preprocessing import calculate_dti, prepare_input_dataframe
from src.prediction import LoanRiskPredictor
from src.evaluate_model import evaluate_all_models
from src.database import DatabaseManager
from src.validators import (
    validate_aadhaar, validate_pan, validate_file_upload,
    validate_phone, validate_email, validate_address,
    verify_file_content, validate_document_complete,
    verify_aadhaar_name_match, extract_text_from_document,
    mask_aadhaar, mask_pan, sanitize_filename
)
import base64

# ─── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinTech Risk Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom Dark Theme CSS ──────────────────────────────────────────────────
CSS_STYLE = r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    .stApp {
        background-color: #0D0E15;
        color: #E2E8F0;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }
    .top-bar {
        background: linear-gradient(135deg, #151824, #1A1F35);
        padding: 14px 24px;
        border-radius: 12px;
        border: 1px solid #2A2E3F;
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
    }
    .top-bar::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #8B5CF6, #38BDF8, #22C55E);
    }
    .top-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
    }
    .top-subtitle {
        font-size: 0.8rem;
        color: #94A3B8;
        margin: 2px 0 0 0;
    }
    .kpi-tile {
        background-color: #151824;
        border: 1px solid #2A2E3F;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-tile:hover {
        transform: translateY(-2px);
        border-color: #8B5CF6;
    }
    .kpi-title {
        font-size: 0.7rem;
        color: #94A3B8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 4px;
    }
    .glass-box {
        background-color: #151824;
        border: 1px solid #2A2E3F;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .profile-card {
        background: linear-gradient(135deg, #151824 0%, #1A1E2E 100%);
        border: 1px solid #2A2E3F;
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .profile-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #8B5CF6, #38BDF8, #22C55E);
    }
    .doc-badge-ok {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(34, 197, 94, 0.12);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.25);
        margin: 2px 4px;
    }
    .doc-badge-miss {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(239, 68, 68, 0.12);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.25);
        margin: 2px 4px;
    }
    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 54px; height: 54px;
        border-radius: 14px;
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: -0.03em;
    }
    .suggestion-card {
        background: #151824;
        border-left: 4px solid;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .sug-critical { border-left-color: #EF4444; }
    .sug-warning  { border-left-color: #F59E0B; }
    .sug-positive { border-left-color: #22C55E; }
    .sug-tip      { border-left-color: #38BDF8; }
    .sug-title {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 2px;
    }
    .sug-detail {
        color: #94A3B8;
        font-size: 0.82rem;
        margin: 0;
    }
    .sug-action {
        color: #CBD5E1;
        font-size: 0.78rem;
        margin-top: 4px;
        font-style: italic;
    }
    .success-box {
        background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.03));
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    section[data-testid="stSidebar"] {
        background-color: #08090E !important;
        border-right: 1px solid #2A2E3F;
    }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .dot-green { background: #22C55E; box-shadow: 0 0 6px #22C55E; }
    .dot-red   { background: #EF4444; box-shadow: 0 0 6px #EF4444; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)


# ─── Load Resources ─────────────────────────────────────────────────────────

@st.cache_resource
def get_predictor():
    try:
        return LoanRiskPredictor(model_dir="model"), None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def get_database():
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        try:
            mongo_uri = st.secrets.get("MONGO_URI")
        except Exception:
            pass
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017/loanriskmodel"
    return DatabaseManager(uri=mongo_uri)


predictor, load_error = get_predictor()
db = get_database()

# Load historical dataset for analytics
DATA_PATH = "data/loan_data.csv"
if os.path.exists(DATA_PATH):
    df_raw = pd.read_csv(DATA_PATH)
else:
    np.random.seed(42)
    df_raw = pd.DataFrame({
        "Credit_Score": np.random.randint(400, 850, 200),
        "Risk_Label": np.random.choice([0, 1], 200, p=[0.7, 0.3]),
        "DTI": np.random.uniform(10, 65, 200),
        "Loan_Amount": np.random.randint(50000, 1000000, 200),
        "Monthly_Income": np.random.randint(25000, 200000, 200)
    })


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def compute_emi(principal, annual_rate_pct, months):
    """Compute Equated Monthly Installment."""
    if months <= 0 or principal <= 0:
        return 0.0
    if annual_rate_pct <= 0:
        return principal / months
    r = annual_rate_pct / 12.0 / 100.0
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return float(emi)


def get_interest_rate(risk_score):
    """Determine indicative interest rate based on risk score."""
    if risk_score <= 20:
        return 8.5
    elif risk_score <= 35:
        return 10.5
    elif risk_score <= 50:
        return 13.0
    elif risk_score <= 65:
        return 16.0
    elif risk_score <= 80:
        return 19.0
    else:
        return 23.0


def get_risk_grade(risk_score):
    """Assign a letter grade based on risk score."""
    if risk_score <= 10:
        return "A+", "#22C55E", "Exceptional"
    elif risk_score <= 20:
        return "A", "#34D399", "Excellent"
    elif risk_score <= 30:
        return "B+", "#A3E635", "Very Good"
    elif risk_score <= 40:
        return "B", "#FACC15", "Good"
    elif risk_score <= 50:
        return "C+", "#FB923C", "Fair"
    elif risk_score <= 60:
        return "C", "#F97316", "Below Average"
    elif risk_score <= 75:
        return "D", "#EF4444", "Poor"
    else:
        return "E", "#DC2626", "Very High Risk"


def generate_tenure_comparison(principal, monthly_income, risk_score):
    """Generate a comparison table for different loan tenures."""
    rate = get_interest_rate(risk_score)
    tenures = [6, 12, 18, 24, 36, 48, 60, 84, 120]
    rows = []
    for t in tenures:
        emi = compute_emi(principal, rate, t)
        total_paid = emi * t
        total_interest = total_paid - principal
        emi_ratio = (emi / monthly_income * 100) if monthly_income > 0 else 0
        if emi_ratio <= 30:
            feasibility = "✅ Ideal"
        elif emi_ratio <= 40:
            feasibility = "🟡 Feasible"
        elif emi_ratio <= 50:
            feasibility = "🟠 Stretching"
        else:
            feasibility = "🔴 Too High"
        rows.append({
            "Tenure": f"{t} months",
            "EMI (₹)": f"₹{emi:,.0f}",
            "Total Interest (₹)": f"₹{total_interest:,.0f}",
            "Total Payable (₹)": f"₹{total_paid:,.0f}",
            "EMI/Income": f"{emi_ratio:.1f}%",
            "Feasibility": feasibility
        })
    return pd.DataFrame(rows)


def compute_max_eligible_loan(monthly_income, monthly_debt, annual_rate, months, max_emi_pct=40):
    """Calculate maximum loan amount at given EMI/income ceiling."""
    available_emi = (monthly_income * max_emi_pct / 100.0) - monthly_debt
    if available_emi <= 0:
        return 0
    if annual_rate <= 0:
        return available_emi * months
    r = annual_rate / 12.0 / 100.0
    max_loan = available_emi * ((1 + r) ** months - 1) / (r * (1 + r) ** months)
    return max(0, float(max_loan))


def generate_amortization_schedule(principal, annual_rate, months):
    """Generate month-by-month amortization schedule."""
    emi = compute_emi(principal, annual_rate, months)
    r = annual_rate / 12.0 / 100.0 if annual_rate > 0 else 0
    balance = principal
    schedule = []
    for m in range(1, months + 1):
        interest = balance * r
        principal_part = emi - interest
        balance -= principal_part
        schedule.append({
            "Month": m,
            "EMI": round(emi, 2),
            "Principal": round(principal_part, 2),
            "Interest": round(interest, 2),
            "Balance": round(max(balance, 0), 2)
        })
    return pd.DataFrame(schedule)


def generate_smart_suggestions(risk_score, emi, monthly_income, loan_amount,
                               loan_term_months, dti, credit_score,
                               previous_defaults, interest_rate):
    """Generate intelligent, actionable suggestions for the applicant."""
    suggestions = []
    emi_pct = (emi / monthly_income * 100) if monthly_income > 0 else 100

    # ── EMI Affordability ────────────────────────────────────────────────
    if emi_pct > 50:
        suggestions.append(("critical", "🚨", "EMI Burden Critical",
            f"Your EMI takes {emi_pct:.1f}% of income. Experts recommend below 40%.",
            f"Increase tenure or reduce loan by ₹{loan_amount * 0.25:,.0f} to bring it under control."))
    elif emi_pct > 40:
        suggestions.append(("warning", "⚠️", "EMI Burden Elevated",
            f"EMI is {emi_pct:.1f}% of income — slightly above the ideal 35-40% threshold.",
            "Consider extending tenure by 12 months to reduce monthly pressure."))
    else:
        suggestions.append(("positive", "✅", "Healthy EMI Ratio",
            f"EMI is only {emi_pct:.1f}% of income — well within the affordable range.",
            "You have comfortable headroom for monthly repayments."))

    # ── DTI Analysis ─────────────────────────────────────────────────────
    if dti > 50:
        suggestions.append(("critical", "🚨", "High Debt-to-Income Ratio",
            f"DTI is {dti:.1f}% — lenders typically reject above 50%.",
            "Pay off smaller debts first to improve your profile significantly."))
    elif dti > 36:
        suggestions.append(("warning", "⚠️", "Elevated DTI Ratio",
            f"DTI is {dti:.1f}% — above the ideal 36% benchmark.",
            "Consolidating existing debts could improve your DTI by 5-10%."))

    # ── Credit Score ─────────────────────────────────────────────────────
    if credit_score < 580:
        rate_diff = get_interest_rate(risk_score) - get_interest_rate(max(risk_score - 25, 0))
        total_savings = emi * loan_term_months * (rate_diff / interest_rate) if interest_rate > 0 else 0
        suggestions.append(("critical", "📊", "Poor Credit Score",
            f"CIBIL {credit_score} is below the acceptable threshold (650+).",
            f"Improving to 700+ could save ~₹{total_savings:,.0f} over the loan life."))
    elif credit_score < 700:
        suggestions.append(("warning", "📊", "Fair Credit Score",
            f"CIBIL {credit_score} is acceptable but leaves room for improvement.",
            "Reaching 750+ could reduce your interest rate by 1.5-3%."))
    elif credit_score >= 750:
        suggestions.append(("positive", "🌟", "Excellent Credit Score",
            f"CIBIL {credit_score} qualifies you for the best available interest rates.",
            "Maintain this by keeping credit utilization below 30%."))

    # ── Previous Defaults ────────────────────────────────────────────────
    if previous_defaults >= 2:
        suggestions.append(("critical", "⚡", "Multiple Default History",
            f"{previous_defaults} previous defaults severely impact approval odds.",
            "Maintain clean repayment for 18+ months and consider a secured loan option."))
    elif previous_defaults == 1:
        suggestions.append(("warning", "⚡", "Previous Default Recorded",
            "1 past default is on record — lenders will apply stricter scrutiny.",
            "12+ months of clean repayment history will help rebuild trust."))

    # ── Optimal Tenure ───────────────────────────────────────────────────
    best_tenure = None
    for t in [12, 18, 24, 36, 48, 60]:
        test_emi = compute_emi(loan_amount, interest_rate, t)
        test_ratio = (test_emi / monthly_income * 100) if monthly_income > 0 else 100
        if test_ratio <= 35:
            best_tenure = t
            best_emi = test_emi
            best_interest = test_emi * t - loan_amount
            break

    if best_tenure and best_tenure != loan_term_months:
        chosen_interest = emi * loan_term_months - loan_amount
        savings = chosen_interest - best_interest if best_tenure < loan_term_months else 0
        if savings > 0:
            suggestions.append(("tip", "💡", f"Consider {best_tenure}-Month Tenure",
                f"EMI ₹{best_emi:,.0f} ({(best_emi / monthly_income * 100):.1f}% of income) — saves ₹{savings:,.0f} in interest.",
                "Shorter tenure with affordable EMI is the sweet spot for total savings."))
        elif best_tenure > loan_term_months:
            suggestions.append(("tip", "💡", f"Switch to {best_tenure}-Month Tenure",
                f"Your current EMI may be too high. {best_tenure} months keeps EMI at ₹{best_emi:,.0f} ({(best_emi / monthly_income * 100):.1f}% of income).",
                "A longer affordable tenure is safer than a shorter unaffordable one."))

    # ── Loan-to-Income Ratio ─────────────────────────────────────────────
    lti = loan_amount / (monthly_income * 12) if monthly_income > 0 else 0
    if lti > 5:
        suggestions.append(("warning", "📐", "High Loan-to-Annual-Income Ratio",
            f"Loan is {lti:.1f}x your annual income — banks prefer below 4x.",
            f"Consider limiting the loan to ₹{monthly_income * 12 * 4:,.0f} for better approval chances."))

    return suggestions


def render_suggestion_card(stype, icon, title, detail, action=""):
    """Render a styled suggestion card in HTML."""
    css_class = f"sug-{stype}"
    color_map = {"critical": "#EF4444", "warning": "#F59E0B", "positive": "#22C55E", "tip": "#38BDF8"}
    title_color = color_map.get(stype, "#CBD5E1")
    action_html = f'<p class="sug-action">→ {action}</p>' if action else ""
    return f"""
    <div class="suggestion-card {css_class}">
        <div class="sug-title" style="color:{title_color};">{icon} {title}</div>
        <p class="sug-detail">{detail}</p>
        {action_html}
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("### ⚡ **FINTECH RISK AI**")
st.sidebar.caption("AI-Powered Loan Risk Assessment System")

# MongoDB connection status
if db.connected:
    st.sidebar.markdown(
        '<span class="status-dot dot-green"></span> MongoDB Connected',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<span class="status-dot dot-red"></span> MongoDB Offline',
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🔍 Loan Risk Assessment",
        "📝 Customer Onboarding",
        "📋 Customer Database",
        "📊 Portfolio Analytics",
        "🤖 Model Intelligence"
    ]
)

# Sidebar quick stats
if db.connected:
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 📊 Quick Stats")
    st.sidebar.metric("Registered Customers", db.get_customer_count())
    st.sidebar.metric("Total Assessments", db.get_application_count())


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 1 — COMMAND CENTER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

if False: # Command Center removed
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ **DASHBOARD FILTERS**")
    score_filter = st.sidebar.slider("Credit Score Range", 300, 850, (400, 850))
    dti_filter = st.sidebar.slider("Max DTI Threshold (%)", 0.0, 100.0, 65.0)
    income_filter = st.sidebar.number_input("Min Monthly Income (₹)", value=20000, step=5000)

    db_apps = db.get_all_applications() if db.connected else []
    if db_apps:
        df_live = pd.DataFrame(db_apps)
        df_live.rename(columns={
            "customer_credit_score": "Credit_Score",
            "customer_income": "Monthly_Income",
            "loan_amount": "Loan_Amount",
            "customer_dti": "DTI",
        }, inplace=True)
        if "verdict" in df_live.columns:
            df_live["Risk_Label"] = df_live["verdict"].apply(lambda x: 1 if "High Risk" in str(x) or "Default" in str(x) else 0)
        else:
            df_live["Risk_Label"] = 0
        if "DTI" not in df_live.columns:
            df_live["DTI"] = 0.0
            
        for col in ["Credit_Score", "Monthly_Income", "Loan_Amount", "DTI", "Risk_Label"]:
            if col not in df_live.columns:
                df_live[col] = 0
    else:
        df_live = pd.DataFrame(columns=["Credit_Score", "DTI", "Monthly_Income", "Risk_Label", "Loan_Amount"])

    df_filtered = df_live[
        (df_live["Credit_Score"] >= score_filter[0]) &
        (df_live["Credit_Score"] <= score_filter[1]) &
        (df_live["DTI"] <= dti_filter) &
        (df_live["Monthly_Income"] >= income_filter)
    ]

    total_apps = len(df_filtered)
    default_count = int(df_filtered["Risk_Label"].sum()) if total_apps > 0 and "Risk_Label" in df_filtered.columns else 0
    default_rate = (default_count / total_apps * 100) if total_apps > 0 else 0.0
    good_loans_pct = 100.0 - default_rate
    total_risk_val = (df_filtered[df_filtered["Risk_Label"] == 1]["Loan_Amount"].sum() / 1e6) if total_apps > 0 and "Loan_Amount" in df_filtered.columns else 0.0

    st.markdown("""
    <div class="top-bar">
        <div class="top-title">⚡ LOAN RISK ASSESSMENT COMMAND CENTER</div>
        <div class="top-subtitle">Real-time Portfolio Monitoring & Risk Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    cust_count = db.get_customer_count() if db.connected else "—"
    with k1:
        st.markdown(f'<div class="kpi-tile"><div class="kpi-title">Good Loans %</div><div class="kpi-value" style="color:#22C55E;">{good_loans_pct:.1f}%</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-tile"><div class="kpi-title">Default Rate %</div><div class="kpi-value" style="color:#EF4444;">{default_rate:.1f}%</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-tile"><div class="kpi-title">Portfolio Risk</div><div class="kpi-value" style="color:#A855F7;">₹{total_risk_val:.2f}M</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-tile"><div class="kpi-title">KYC Customers</div><div class="kpi-value" style="color:#38BDF8;">{cust_count}</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown(f'<div class="kpi-tile"><div class="kpi-title">Deployed Model</div><div class="kpi-value" style="color:#F59E0B; font-size:1.1rem; margin-top:4px;">Random Forest</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total_apps == 0:
        st.warning("⚠️ No records match the selected sidebar filters. Adjust sliders to view dynamic results.")
    else:
        c_left, c_mid, c_right = st.columns([1.2, 1.8, 1.2])

        with c_left:
            st.markdown("### 🎯 Portfolio Breakdown")
            risk_counts = df_filtered["Risk_Label"].value_counts().reset_index()
            risk_counts.columns = ["Status", "Count"]
            risk_counts["Status"] = risk_counts["Status"].map({0: "Approved (Low)", 1: "Default (High)"})
            fig_donut = px.pie(
                risk_counts, values="Count", names="Status",
                hole=0.55, color="Status",
                color_discrete_map={"Approved (Low)": "#22C55E", "Default (High)": "#A855F7"}
            )
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8', size=11),
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            st.markdown("##### Default Rate by DTI Band")
            df_filtered_copy = df_filtered.copy()
            df_filtered_copy["DTI_Band"] = pd.cut(df_filtered_copy["DTI"], bins=[0, 20, 40, 60, 100], labels=["<20%", "20-40%", "40-60%", ">60%"])
            dti_summary = df_filtered_copy.groupby("DTI_Band", observed=False)["Risk_Label"].mean().reset_index()
            dti_summary["Risk_Label"] = (dti_summary["Risk_Label"] * 100).round(1).astype(str) + "%"
            dti_summary.columns = ["DTI Band", "Default Rate"]
            st.dataframe(dti_summary, hide_index=True, use_container_width=True)

        with c_mid:
            st.markdown("### 📈 Credit Band Analysis")
            df_filtered_copy2 = df_filtered.copy()
            df_filtered_copy2["Score_Band"] = pd.cut(
                df_filtered_copy2["Credit_Score"],
                bins=[300, 580, 670, 740, 850],
                labels=["Poor", "Fair", "Good", "Excellent"]
            )
            band_df = df_filtered_copy2.groupby("Score_Band", observed=False).agg(
                Total_Loans=("Risk_Label", "count"),
                Default_Rate=("Risk_Label", "mean")
            ).reset_index()
            band_df["Default_Rate_Pct"] = band_df["Default_Rate"] * 100

            fig_combo = go.Figure()
            fig_combo.add_trace(go.Bar(
                x=band_df["Score_Band"], y=band_df["Total_Loans"],
                name="Loan Volume", marker_color="#8B5CF6"
            ))
            fig_combo.add_trace(go.Scatter(
                x=band_df["Score_Band"], y=band_df["Default_Rate_Pct"],
                name="Default Rate %", yaxis="y2", mode="lines+markers",
                line=dict(color="#38BDF8", width=3)
            ))
            fig_combo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8'), margin=dict(t=20, b=20, l=10, r=10),
                yaxis=dict(title="Loan Volume", gridcolor="#2A2E3F"),
                yaxis2=dict(title="Default Rate %", overlaying="y", side="right", range=[0, 100]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig_combo, use_container_width=True)

            st.markdown("##### Income Distribution vs. Risk")
            fig_hist = px.histogram(
                df_filtered, x="Monthly_Income", color="Risk_Label",
                color_discrete_map={0: "#22C55E", 1: "#A855F7"}, nbins=20
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8'), margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with c_right:
            st.markdown("### ⚡ Smart Assessment")
            st.info("The manual risk evaluator has been upgraded!\n\nPlease navigate to the **🔍 Loan Risk Assessment** page from the sidebar to automatically fetch customer KYC details from MongoDB and predict risk.")



# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 2 — CUSTOMER ONBOARDING (KYC)
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📝 Customer Onboarding":
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">📝 CUSTOMER ONBOARDING — KYC PORTAL</div>
        <div class="top-subtitle">Register new customers with identity verification & document upload</div>
    </div>
    """, unsafe_allow_html=True)

    if not db.connected:
        st.error("🔴 MongoDB is offline. Please start your MongoDB server and refresh the page.")
        st.stop()

    with st.form("kyc_registration_form", clear_on_submit=False):
        # ── Personal Information ─────────────────────────────────────────
        st.markdown("#### 👤 Personal Information")
        pc1, pc2 = st.columns(2)
        with pc1:
            reg_name = st.text_input("Full Name *", placeholder="Enter full legal name")
        with pc2:
            reg_father = st.text_input("Father's / Guardian's Name *", placeholder="Enter father's name")

        pc3, pc4, pc5, pc6 = st.columns(4)
        with pc3:
            reg_dob = st.date_input(
                "Date of Birth *",
                value=None,
                min_value=datetime(1940, 1, 1),
                max_value=datetime.now(),
                help="Used to auto-calculate age"
            )
        with pc4:
            reg_gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
        with pc5:
            reg_marital = st.selectbox("Marital Status *", ["Single", "Married", "Divorced", "Widowed"])
        with pc6:
            reg_employment = st.selectbox("Employment Type *", [
                "Salaried - Private", "Salaried - Government",
                "Self-Employed", "Business Owner", "Freelancer", "Student", "Retired"
            ])

        st.markdown("---")

        # ── Contact Information ──────────────────────────────────────────
        st.markdown("#### 📞 Contact Information")
        ct1, ct2 = st.columns(2)
        with ct1:
            reg_phone = st.text_input("Mobile Number (10 digits) *", placeholder="9876543210", max_chars=10)
        with ct2:
            reg_email = st.text_input("Email Address *", placeholder="name@example.com")

        reg_address = st.text_area(
            "Full Address *",
            placeholder="House No, Street, Locality, City, State, PIN Code",
            height=80
        )

        st.markdown("---")

        # ── Financial Information ────────────────────────────────────────
        st.markdown("#### 💰 Financial Information")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            reg_income = st.number_input("Monthly Income (₹) *", min_value=5000.0, value=50000.0, step=5000.0)
        with fc2:
            reg_debt = st.number_input("Monthly Debt Payments (₹)", min_value=0.0, value=8000.0, step=1000.0)
        with fc3:
            reg_credit = st.number_input("Credit Score (CIBIL) *", min_value=300, max_value=900, value=700)

        fc4, fc5 = st.columns(2)
        with fc4:
            reg_prev_loans = st.number_input("Total Previous Loans", min_value=0, max_value=20, value=0)
        with fc5:
            reg_prev_defaults = st.number_input("Previous Loan Defaults", min_value=0, max_value=10, value=0)

        st.markdown("---")

        # ── Identity Verification ────────────────────────────────────────
        st.markdown("#### 🔐 Identity Verification")
        id1, id2 = st.columns(2)
        with id1:
            reg_aadhaar = st.text_input(
                "Aadhaar Number (12 digits) *",
                placeholder="2345 6789 0124",
                max_chars=14,
                help="12 digits, cannot start with 0 or 1, non-repetitive, verified via UIDAI Verhoeff algorithm"
            )
        with id2:
            reg_pan = st.text_input(
                "PAN Card Number *",
                placeholder="ABCPS1234E",
                max_chars=10,
                help="5 letters + 4 digits + 1 letter. 4th char must be 'P' (Individual) and 5th char must match applicant surname initial"
            )

        st.markdown("---")

        # ── Document Uploads ─────────────────────────────────────────────
        st.markdown("#### 📎 Document Uploads")
        st.caption("Accepted formats: PNG, JPEG, PDF | Max size: 2MB per file | Files are verified for authenticity and name matching")
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            reg_aadhaar_file = st.file_uploader(
                "Aadhaar Card Copy *", type=["png", "jpg", "jpeg", "pdf"],
                key="aadhaar_upload",
                help="Applicant name will be extracted and verified against entered name (at least one matching word required)"
            )
        with dc2:
            reg_pan_file = st.file_uploader(
                "PAN Card Copy *", type=["png", "jpg", "jpeg", "pdf"],
                key="pan_upload"
            )
        with dc3:
            reg_salary_file = st.file_uploader(
                "Salary Slip / Income Proof *", type=["png", "jpg", "jpeg", "pdf"],
                key="salary_upload"
            )

        st.markdown("---")
        submit_kyc = st.form_submit_button("📋 REGISTER CUSTOMER", use_container_width=True)

    # ── Form Validation & Submission ─────────────────────────────────────
    if submit_kyc:
        errors = []

        # Required fields
        if not reg_name.strip():
            errors.append("Full Name is required")
        if not reg_father.strip():
            errors.append("Father's / Guardian's Name is required")

        # DOB & Age validation
        if reg_dob is None:
            errors.append("Date of Birth is required")
            calc_age = 0
        else:
            today = datetime.now().date()
            calc_age = today.year - reg_dob.year - ((today.month, today.day) < (reg_dob.month, reg_dob.day))
            if calc_age < 18:
                errors.append(f"Applicant must be at least 18 years old (calculated age: {calc_age})")
            elif calc_age > 75:
                errors.append(f"Applicant age exceeds maximum limit of 75 years (calculated age: {calc_age})")

        # Phone validation
        phone_valid, phone_msg = validate_phone(reg_phone)
        if not phone_valid:
            errors.append(f"Phone: {phone_msg}")

        # Email validation
        email_valid, email_msg = validate_email(reg_email)
        if not email_valid:
            errors.append(f"Email: {email_msg}")

        # Address validation
        addr_valid, addr_msg = validate_address(reg_address)
        if not addr_valid:
            errors.append(f"Address: {addr_msg}")

        # Aadhaar validation (real-world rules: 12 digits, non-0/1, non-repetitive, non-sequential, Verhoeff checksum)
        aadhaar_valid, aadhaar_msg = validate_aadhaar(reg_aadhaar)
        if not aadhaar_valid:
            errors.append(f"Aadhaar: {aadhaar_msg}")

        # PAN validation (real-world rules: Individual 'P', surname initial match, digits != 0000)
        pan_valid, pan_msg = validate_pan(reg_pan, reg_name)
        if not pan_valid:
            errors.append(f"PAN: {pan_msg}")

        # ── Document File Validations (type + size + content authenticity + name extraction) ──
        aadhaar_doc_ok = False
        aadhaar_name_ok = False
        aadhaar_name_msg = ""
        if reg_aadhaar_file:
            doc_ok, doc_msgs = validate_document_complete(reg_aadhaar_file, "Aadhaar Card")
            if not doc_ok:
                for dm in doc_msgs:
                    if not dm.startswith("✅"):
                        errors.append(f"Aadhaar file: {dm}")
            else:
                aadhaar_doc_ok = True
                # Concurrently extract name from Aadhaar and verify relation (liberal rules: at least one word match)
                name_ok, name_msg, name_details = verify_aadhaar_name_match(reg_aadhaar_file, reg_name)
                if not name_ok:
                    errors.append(name_msg)
                else:
                    aadhaar_name_ok = True
                    aadhaar_name_msg = name_msg
        else:
            errors.append("Aadhaar Card copy is required for KYC verification")

        pan_doc_ok = False
        if reg_pan_file:
            doc_ok, doc_msgs = validate_document_complete(reg_pan_file, "PAN Card")
            if not doc_ok:
                for dm in doc_msgs:
                    if not dm.startswith("✅"):
                        errors.append(f"PAN file: {dm}")
            else:
                pan_doc_ok = True
        else:
            errors.append("PAN Card copy is required for KYC verification")

        salary_doc_ok = False
        if reg_salary_file:
            doc_ok, doc_msgs = validate_document_complete(reg_salary_file, "Salary Slip")
            if not doc_ok:
                for dm in doc_msgs:
                    if not dm.startswith("✅"):
                        errors.append(f"Salary slip file: {dm}")
            else:
                salary_doc_ok = True
        else:
            errors.append("Salary Slip / Income Proof copy is required for KYC verification")

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            # Build customer document
            clean_aadhaar = reg_aadhaar.strip().replace(" ", "").replace("-", "")
            clean_pan = reg_pan.strip().upper()
            clean_phone = reg_phone.strip().replace(" ", "").replace("-", "")
            clean_email = reg_email.strip().lower()

            kyc_all_verified = (
                aadhaar_valid and pan_valid and phone_valid and email_valid and
                aadhaar_doc_ok and aadhaar_name_ok and pan_doc_ok and salary_doc_ok
            )

            customer_data = {
                "name": reg_name.strip().title(),
                "father_name": reg_father.strip().title(),
                "dob": datetime(reg_dob.year, reg_dob.month, reg_dob.day) if reg_dob else None,
                "age": int(calc_age),
                "gender": reg_gender,
                "marital_status": reg_marital,
                "employment_type": reg_employment,
                "phone_number": clean_phone,
                "email": clean_email,
                "address": reg_address.strip(),
                "monthly_income": float(reg_income),
                "monthly_debt_payment": float(reg_debt),
                "credit_score": int(reg_credit),
                "previous_loans": int(reg_prev_loans),
                "previous_defaults": int(reg_prev_defaults),
                "aadhaar_number": clean_aadhaar,
                "pan_number": clean_pan,
                "aadhaar_verified": aadhaar_valid and aadhaar_doc_ok and aadhaar_name_ok,
                "pan_verified": pan_valid and pan_doc_ok,
                "phone_verified": phone_valid,
                "email_verified": email_valid,
                "salary_slip_uploaded": salary_doc_ok,
                "aadhaar_name_verified": aadhaar_name_ok,
                "aadhaar_name_match_details": aadhaar_name_msg,
                "kyc_status": "verified" if kyc_all_verified else "pending",
            }

            documents = {
                "aadhaar": reg_aadhaar_file,
                "pan": reg_pan_file,
                "salary_slip": reg_salary_file,
            }

            with st.spinner("Registering customer & verifying KYC documents..."):
                inserted_id, error = db.add_customer(customer_data, documents)

            if error:
                st.error(f"❌ Registration Failed: {error}")
            else:
                st.balloons()
                is_verified = customer_data["kyc_status"] == "verified"
                status_badge = '<span style="color:#22C55E; font-weight:700;">✅ Verified (3/3 Required Docs Authenticated)</span>' if is_verified else '<span style="color:#F59E0B; font-weight:700;">⏳ Pending Verification</span>'
                eligible_note = "Customer has completed full KYC and is <b>authorized for Loan Risk Assessment</b>." if is_verified else "Please complete all document requirements to enable Loan Risk Assessment."

                st.markdown(f"""
                <div class="success-box">
                    <h2 style="color:#22C55E; margin:0 0 8px 0;">✅ Customer Registered Successfully!</h2>
                    <p style="color:#94A3B8; margin:4px 0; font-size:1rem;">
                        <b>{customer_data['name']}</b> has been onboarded to the system.
                    </p>
                    <p style="color:#64748B; font-size:0.85rem;">
                        Aadhaar: {mask_aadhaar(clean_aadhaar)} &nbsp;|&nbsp; PAN: {mask_pan(clean_pan)}
                    </p>
                    <p style="color:#64748B; font-size:0.85rem;">
                        📞 {clean_phone} &nbsp;|&nbsp; ✉️ {clean_email}
                    </p>
                    <p style="color:#64748B; font-size:0.85rem;">
                        Customer ID: <code>{inserted_id}</code> &nbsp;|&nbsp;
                        KYC Status: {status_badge}
                    </p>
                    <p style="color:#22C55E; font-size:0.85rem; margin:4px 0;">
                        {aadhaar_name_msg if aadhaar_name_msg else "📋 Aadhaar Document Verified"}
                    </p>
                    <p style="color:#38BDF8; font-size:0.85rem; margin-top:12px;">
                        {eligible_note} Navigate to <b>Loan Risk Assessment</b> to evaluate risk.
                    </p>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 3 — LOAN RISK ASSESSMENT (SMART PREDICTION)
# ═══════════════════════════════════════════════════════════════════════════

elif page == "🔍 Loan Risk Assessment":
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">🔍 SMART LOAN RISK ASSESSMENT</div>
        <div class="top-subtitle">Search registered customer → Enter loan parameters → AI-powered risk analysis & advisory</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    **🤖 Deployed Model Summary:**
    - **Algorithm:** Random Forest Classifier (150 trees, max depth 10)
    - **Features Analyzed:** Age, Monthly Income, Loan Amount, Loan Term, Credit Score, Previous Defaults, Monthly Debt, DTI %
    - **Preprocessing:** Median SimpleImputer (prevents data leakage)
    - **Explainability:** SHAP TreeExplainer for feature-level contribution analysis
    """)

    if not db.connected:
        st.error("🔴 MongoDB is offline. Please start your MongoDB server.")
        st.stop()
    if load_error:
        st.error(f"⚠️ Model Error: {load_error}")
        st.stop()

    # ── Step 1: Customer Search ──────────────────────────────────────────
    st.markdown("### 🔎 Step 1: Find Customer")
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        search_name = st.text_input("Enter Customer Name", placeholder="Start typing to search...", label_visibility="collapsed")
    with btn_col:
        search_btn = st.button("🔍 Search", use_container_width=True)

    if search_btn and search_name.strip():
        results = db.search_customers(search_name.strip())
        st.session_state["search_results"] = results
        st.session_state["selected_customer_name"] = None

    if search_btn and not search_name.strip():
        st.warning("Please enter a customer name to search.")

    # ── Display Search Results ───────────────────────────────────────────
    if "search_results" in st.session_state:
        results = st.session_state["search_results"]
        if not results:
            st.info("🔍 No customers found with that name. Please check the spelling or register the customer first.")
        else:
            # Build display labels
            options = []
            for c in results:
                aadhaar_last4 = c.get("aadhaar_number", "")[-4:] if c.get("aadhaar_number") else "—"
                label = f"{c['name']}  |  Age: {c.get('age', '—')}  |  Aadhaar: ****{aadhaar_last4}"
                options.append(label)

            selected_label = st.selectbox("Select Customer", options, key="customer_select")
            selected_idx = options.index(selected_label)
            customer = results[selected_idx]
            st.session_state["selected_customer_name"] = customer["name"]

            # ── Customer Profile Card ────────────────────────────────────
            aadhaar_display = mask_aadhaar(customer.get("aadhaar_number", ""))
            pan_display = mask_pan(customer.get("pan_number", ""))
            dti_display = calculate_dti(customer.get("monthly_debt_payment", 0), customer.get("monthly_income", 1))

            docs = customer.get("documents", {})
            has_aadhaar = "aadhaar" in docs
            has_pan = "pan" in docs
            has_salary_slip = "salary_slip" in docs
            all_docs_present = has_aadhaar and has_pan and has_salary_slip
            identity_verified = bool(customer.get("aadhaar_verified", False) and customer.get("pan_verified", False))

            # Strict rule: KYC is ONLY verified if all 3 mandatory docs are present, identity verified, and status is verified
            is_kyc_verified = (customer.get("kyc_status") == "verified") and all_docs_present and identity_verified

            aadhaar_badge = '<span class="doc-badge-ok">Aadhaar ✓</span>' if has_aadhaar else '<span class="doc-badge-miss">Aadhaar ✗</span>'
            pan_badge = '<span class="doc-badge-ok">PAN ✓</span>' if has_pan else '<span class="doc-badge-miss">PAN ✗</span>'
            salary_badge = '<span class="doc-badge-ok">Salary Slip ✓</span>' if has_salary_slip else '<span class="doc-badge-miss">Salary Slip ✗</span>'

            # KYC Status Badge - strictly given only when verified with all documents
            if is_kyc_verified:
                kyc_badge = '<span class="doc-badge-ok">KYC ✅ Verified</span>'
            elif customer.get("kyc_status") == "rejected":
                kyc_badge = '<span class="doc-badge-miss">KYC ❌ Rejected</span>'
            else:
                doc_count = sum(1 for d in (has_aadhaar, has_pan, has_salary_slip) if d)
                kyc_badge = f'<span class="doc-badge-miss">KYC ⏳ Incomplete ({doc_count}/3 Docs)</span>'

            # Credit score color
            cs = customer.get("credit_score", 0)
            cs_color = "#22C55E" if cs >= 750 else "#FACC15" if cs >= 650 else "#EF4444"

            # Gender display
            gender_display = customer.get("gender", "—")

            st.markdown(f"""
            <div class="profile-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
                    <div>
                        <h2 style="color:#F8FAFC; margin:0 0 2px 0; font-size:1.4rem;">👤 {customer['name']}</h2>
                        <p style="color:#94A3B8; margin:0; font-size:0.85rem;">
                            S/o {customer.get('father_name', '—')} &nbsp;|&nbsp;
                            {gender_display} &nbsp;|&nbsp;
                            {customer.get('marital_status', '—')} &nbsp;|&nbsp;
                            {customer.get('employment_type', '—')}
                        </p>
                    </div>
                    <div style="text-align:right;">
                        {kyc_badge}<br style="margin:4px 0;">
                        {aadhaar_badge} {pan_badge} {salary_badge}
                    </div>
                </div>
                <hr style="border-color:#2A2E3F; margin:14px 0;">
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px,1fr)); gap:12px;">
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">Age</span><br>
                        <span style="color:#F8FAFC; font-size:1.1rem; font-weight:700;">{customer.get('age', '—')} yrs</span>
                    </div>
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">Monthly Income</span><br>
                        <span style="color:#22C55E; font-size:1.1rem; font-weight:700;">₹{customer.get('monthly_income', 0):,.0f}</span>
                    </div>
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">Monthly Debt</span><br>
                        <span style="color:#F59E0B; font-size:1.1rem; font-weight:700;">₹{customer.get('monthly_debt_payment', 0):,.0f}</span>
                    </div>
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">Credit Score</span><br>
                        <span style="color:{cs_color}; font-size:1.1rem; font-weight:700;">{cs}</span>
                    </div>
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">DTI Ratio</span><br>
                        <span style="color:#38BDF8; font-size:1.1rem; font-weight:700;">{dti_display:.1f}%</span>
                    </div>
                    <div>
                        <span style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; font-weight:600;">Prev. Defaults</span><br>
                        <span style="color:{'#EF4444' if customer.get('previous_defaults', 0) > 0 else '#22C55E'}; font-size:1.1rem; font-weight:700;">{customer.get('previous_defaults', 0)}</span>
                    </div>
                </div>
                <div style="margin-top:10px;">
                    <span style="color:#64748B; font-size:0.75rem;">
                        Aadhaar: {aadhaar_display} &nbsp;|&nbsp; PAN: {pan_display}
                        {' &nbsp;|&nbsp; 📞 ' + customer.get('phone_number', '') if customer.get('phone_number') else ''}
                        {' &nbsp;|&nbsp; ✉️ ' + customer.get('email', '') if customer.get('email') else ''}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Strict KYC Completeness & Loan Risk Gate ─────────────────
            if not is_kyc_verified:
                st.markdown(f"""
                <div style="background:rgba(239, 68, 68, 0.12); border:1.5px solid #EF4444; border-radius:12px; padding:20px; margin:20px 0;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:2rem;">🔒</span>
                        <div>
                            <h3 style="color:#EF4444; margin:0 0 4px 0; font-size:1.2rem;">Loan Risk Evaluation Locked — KYC Verification Required</h3>
                            <p style="color:#FCA5A5; margin:0; font-size:0.9rem;">
                                Per banking regulations, <b>loan risk calculation, interest rate pricing, and EMI schedules cannot be computed</b>
                                until all 3 mandatory KYC documents (Aadhaar, PAN, and Salary Slip / Income Proof) are uploaded and verified.
                            </p>
                        </div>
                    </div>
                    <hr style="border-color:rgba(239, 68, 68, 0.3); margin:14px 0;">
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.85rem;">
                        <div>
                            <b>Aadhaar Card Copy:</b> {('<span style="color:#22C55E;">✅ Uploaded & Verified</span>' if has_aadhaar else '<span style="color:#EF4444;">❌ Missing (Mandatory)</span>')}
                        </div>
                        <div>
                            <b>PAN Card Copy:</b> {('<span style="color:#22C55E;">✅ Uploaded & Verified</span>' if has_pan else '<span style="color:#EF4444;">❌ Missing (Mandatory)</span>')}
                        </div>
                        <div>
                            <b>Salary Slip / Income Proof:</b> {('<span style="color:#22C55E;">✅ Uploaded & Verified</span>' if has_salary_slip else '<span style="color:#EF4444;">❌ Missing (Mandatory)</span>')}
                        </div>
                        <div>
                            <b>Identity Credentials:</b> {('<span style="color:#22C55E;">✅ Formats Verified</span>' if identity_verified else '<span style="color:#EF4444;">❌ Not Verified</span>')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Missing Document Uploader to resolve KYC right here
                with st.expander("📎 Upload & Verify Missing KYC Documents to Unlock Risk Assessment", expanded=True):
                    st.markdown(f"Upload the missing required documents for **{customer['name']}** to authenticate them and unlock loan risk calculation:")
                    up_c1, up_c2, up_c3 = st.columns(3)
                    new_docs = {}

                    with up_c1:
                        if not has_aadhaar:
                            up_aadhaar = st.file_uploader("Upload Aadhaar Copy *", type=["png", "jpg", "jpeg", "pdf"], key=f"up_adh_{customer['_id']}")
                            if up_aadhaar:
                                new_docs["aadhaar"] = up_aadhaar
                        else:
                            st.success("✅ Aadhaar Card on file")

                    with up_c2:
                        if not has_pan:
                            up_pan = st.file_uploader("Upload PAN Card *", type=["png", "jpg", "jpeg", "pdf"], key=f"up_pan_{customer['_id']}")
                            if up_pan:
                                new_docs["pan"] = up_pan
                        else:
                            st.success("✅ PAN Card on file")

                    with up_c3:
                        if not has_salary_slip:
                            up_salary = st.file_uploader("Upload Salary Slip *", type=["png", "jpg", "jpeg", "pdf"], key=f"up_sal_{customer['_id']}")
                            if up_salary:
                                new_docs["salary_slip"] = up_salary
                        else:
                            st.success("✅ Salary Slip on file")

                    if st.button("🚀 Verify & Update Documents", key=f"up_submit_{customer['_id']}", use_container_width=True):
                        # Validate each file
                        val_errs = []
                        valid_docs_map = {}
                        for doc_k, doc_f in new_docs.items():
                            doc_label = "Aadhaar Card" if doc_k == "aadhaar" else "PAN Card" if doc_k == "pan" else "Salary Slip"
                            v_ok, v_msgs = validate_document_complete(doc_f, doc_label)
                            if not v_ok:
                                for vm in v_msgs:
                                    if not vm.startswith("✅"):
                                        val_errs.append(f"{doc_label}: {vm}")
                            else:
                                valid_docs_map[doc_k] = doc_f

                        if val_errs:
                            for ve in val_errs:
                                st.error(f"❌ {ve}")
                        elif not valid_docs_map:
                            st.warning("Please select at least one document to upload.")
                        else:
                            saved_ok, save_msg = db.upload_customer_documents(str(customer["_id"]), valid_docs_map)
                            if saved_ok:
                                st.success(f"✅ {save_msg}")
                                # Update customer in session_state results so rerendering reflects changes
                                updated_rec = db.get_customer_by_id(str(customer["_id"]))
                                if updated_rec:
                                    for idx, r in enumerate(st.session_state["search_results"]):
                                        if str(r.get("_id")) == str(customer["_id"]):
                                            st.session_state["search_results"][idx] = updated_rec
                                            break
                                st.rerun()
                            else:
                                st.error(f"❌ Upload failed: {save_msg}")

                # Lock the page — do not render Step 2 (Loan Parameters) or risk calculation
                st.stop()

            # ── KYC IS FULLY VERIFIED: Authorized to calculate loan risk ──
            st.markdown("""
            <div style="background:rgba(34, 197, 94, 0.1); border:1px solid #22C55E; border-radius:10px; padding:12px 18px; margin:16px 0; display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.4rem;">✅</span>
                <div>
                    <b style="color:#22C55E;">KYC Fully Verified & Authenticated</b>
                    <span style="color:#94A3B8; font-size:0.85rem; margin-left:8px;">All 3 mandatory documents (Aadhaar, PAN, Salary Slip) are verified. This customer is authorized for Loan Risk Evaluation.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Step 2: Loan Parameters ──────────────────────────────────
            st.markdown("### 💰 Step 2: Enter Loan Parameters")
            with st.form("loan_params_form"):
                lp1, lp2, lp3 = st.columns(3)
                with lp1:
                    loan_amount = st.number_input(
                        "Loan Amount Requested (₹) *",
                        min_value=10000.0, max_value=50000000.0,
                        value=500000.0, step=25000.0
                    )
                with lp2:
                    emi_afforded = st.number_input(
                        "EMI Afforded (₹) *",
                        min_value=500.0, max_value=500000.0,
                        value=15000.0, step=1000.0,
                        help="The monthly EMI the customer expects to be able to afford."
                    )
                with lp3:
                    loan_tenure = st.selectbox(
                        "Repayment Tenure (Months) *",
                        options=[6, 12, 18, 24, 36, 48, 60, 84, 120, 180, 240, 360],
                        index=4
                    )
                predict_btn = st.form_submit_button("🔮 GENERATE RISK ASSESSMENT", use_container_width=True)

            # ── Step 3: Run Prediction & Generate Report ─────────────────
            if predict_btn:
                c_income = float(customer.get("monthly_income", 50000))
                c_debt = float(customer.get("monthly_debt_payment", 0))
                c_age = int(customer.get("age", 30))
                c_credit = int(customer.get("credit_score", 650))
                c_defaults = int(customer.get("previous_defaults", 0))
                # Project the new debt and DTI using the afforded EMI
                projected_debt = c_debt + emi_afforded
                c_dti = calculate_dti(projected_debt, c_income)

                # Prepare input and predict
                input_df = prepare_input_dataframe(
                    age=c_age, monthly_income=c_income, loan_amount=loan_amount,
                    loan_term_months=loan_tenure, credit_score=c_credit,
                    previous_defaults=c_defaults, monthly_debt_payment=projected_debt, dti=c_dti
                )
                res = predictor.predict(input_df)
                risk_score = res["risk_score"]

                # Derived metrics
                grade, grade_color, grade_label = get_risk_grade(risk_score)
                interest_rate = get_interest_rate(risk_score)
                emi = compute_emi(loan_amount, interest_rate, loan_tenure)
                total_payable = emi * loan_tenure
                total_interest = total_payable - loan_amount
                emi_to_income = (emi / c_income * 100) if c_income > 0 else 0
                max_eligible = compute_max_eligible_loan(c_income, c_debt, interest_rate, loan_tenure)

                # Save to DB
                app_data = {
                    "customer_name": customer["name"],
                    "customer_age": c_age,
                    "customer_income": c_income,
                    "customer_credit_score": c_credit,
                    "customer_dti": c_dti,
                    "loan_amount": loan_amount,
                    "loan_tenure_months": loan_tenure,
                    "risk_score": risk_score,
                    "risk_grade": grade,
                    "risk_category": res["presentation_category"],
                    "default_probability": res["high_risk_probability"],
                    "interest_rate": interest_rate,
                    "emi": round(emi, 2),
                    "total_payable": round(total_payable, 2),
                    "total_interest": round(total_interest, 2),
                    "verdict": res["raw_class_label"],
                }
                app_id = db.save_application(app_data)

                st.markdown("---")
                st.markdown("## 📊 Comprehensive Risk Assessment Report")
                if app_id:
                    st.caption(f"Application Reference: **{app_id}** | Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

                # ── KPI Row ──────────────────────────────────────────────
                r1, r2, r3, r4, r5 = st.columns(5)
                with r1:
                    st.markdown(f"""<div class="kpi-tile">
                        <div class="kpi-title">Risk Score</div>
                        <div class="kpi-value" style="color:{res['risk_color']};">{risk_score}</div>
                    </div>""", unsafe_allow_html=True)
                with r2:
                    st.markdown(f"""<div class="kpi-tile">
                        <div class="kpi-title">Risk Grade</div>
                        <div class="grade-badge" style="background:{grade_color}22; color:{grade_color}; margin:4px auto 0;">{grade}</div>
                    </div>""", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"""<div class="kpi-tile">
                        <div class="kpi-title">Monthly EMI</div>
                        <div class="kpi-value" style="color:#38BDF8;">₹{emi:,.0f}</div>
                    </div>""", unsafe_allow_html=True)
                with r4:
                    st.markdown(f"""<div class="kpi-tile">
                        <div class="kpi-title">Interest Rate</div>
                        <div class="kpi-value" style="color:#A855F7;">{interest_rate}%</div>
                    </div>""", unsafe_allow_html=True)
                with r5:
                    verdict_color = "#22C55E" if res["binary_prediction"] == 0 else "#EF4444"
                    st.markdown(f"""<div class="kpi-tile">
                        <div class="kpi-title">Verdict</div>
                        <div class="kpi-value" style="color:{verdict_color}; font-size:1rem;">{res['raw_class_label']}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Gauge & Financial Summary ────────────────────────────
                gc1, gc2 = st.columns([1.3, 1])
                with gc1:
                    st.markdown("#### 🎯 Risk Score Gauge")
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"Risk Grade: {grade} ({grade_label})", 'font': {'color': '#F8FAFC', 'size': 16}},
                        number={'font': {'color': '#F8FAFC', 'size': 42}, 'suffix': '/100'},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': '#94A3B8'},
                            'bar': {'color': grade_color},
                            'bgcolor': "#151824",
                            'steps': [
                                {'range': [0, 20], 'color': "rgba(34, 197, 94, 0.15)"},
                                {'range': [20, 40], 'color': "rgba(163, 230, 53, 0.12)"},
                                {'range': [40, 60], 'color': "rgba(250, 204, 21, 0.12)"},
                                {'range': [60, 80], 'color': "rgba(239, 68, 68, 0.12)"},
                                {'range': [80, 100], 'color': "rgba(220, 38, 38, 0.18)"},
                            ],
                            'threshold': {
                                'line': {'color': "#F8FAFC", 'width': 2},
                                'thickness': 0.8,
                                'value': risk_score
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=10))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with gc2:
                    st.markdown("#### 💵 Financial Summary")
                    st.markdown(f"""
                    <div class="glass-box">
                        <table style="width:100%; border-collapse:collapse;">
                            <tr><td style="color:#94A3B8; padding:6px 0;">Loan Amount</td>
                                <td style="color:#F8FAFC; text-align:right; font-weight:700; padding:6px 0;">₹{loan_amount:,.0f}</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Tenure</td>
                                <td style="color:#F8FAFC; text-align:right; font-weight:700;">{loan_tenure} months</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Interest Rate (p.a.)</td>
                                <td style="color:#A855F7; text-align:right; font-weight:700;">{interest_rate}%</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Monthly EMI</td>
                                <td style="color:#38BDF8; text-align:right; font-weight:700;">₹{emi:,.0f}</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Total Interest</td>
                                <td style="color:#F59E0B; text-align:right; font-weight:700;">₹{total_interest:,.0f}</td></tr>
                            <tr style="border-top:1px solid #2A2E3F;">
                                <td style="color:#94A3B8; padding:8px 0; font-weight:700;">Total Payable</td>
                                <td style="color:#F8FAFC; text-align:right; font-weight:900; font-size:1.1rem;">₹{total_payable:,.0f}</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">EMI / Income</td>
                                <td style="color:{'#22C55E' if emi_to_income <= 40 else '#EF4444'}; text-align:right; font-weight:700;">{emi_to_income:.1f}%</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Max Eligible Loan</td>
                                <td style="color:#38BDF8; text-align:right; font-weight:700;">₹{max_eligible:,.0f}</td></tr>
                            <tr><td style="color:#94A3B8; padding:6px 0;">Default Probability</td>
                                <td style="color:{res['risk_color']}; text-align:right; font-weight:700;">{res['high_risk_probability']}%</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Affordability Pie Chart ──────────────────────────────
                aff1, aff2 = st.columns(2)
                with aff1:
                    st.markdown("#### 📊 Monthly Income Allocation")
                    remaining = max(c_income - emi - c_debt, 0)
                    fig_aff = px.pie(
                        names=["Proposed EMI", "Existing Debt", "Disposable Income"],
                        values=[emi, c_debt, remaining],
                        color_discrete_sequence=["#38BDF8", "#F59E0B", "#22C55E"],
                        hole=0.5
                    )
                    fig_aff.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'),
                        margin=dict(t=10, b=10, l=10, r=10),
                        legend=dict(orientation="h", y=-0.15)
                    )
                    st.plotly_chart(fig_aff, use_container_width=True)

                with aff2:
                    st.markdown("#### 📈 Tenure vs. Total Cost Analysis")
                    rate_for_chart = interest_rate
                    chart_tenures = [12, 24, 36, 48, 60, 84, 120]
                    chart_emis = [compute_emi(loan_amount, rate_for_chart, t) for t in chart_tenures]
                    chart_interests = [e * t - loan_amount for e, t in zip(chart_emis, chart_tenures)]
                    fig_tc = go.Figure()
                    fig_tc.add_trace(go.Bar(
                        x=[f"{t}m" for t in chart_tenures], y=[loan_amount] * len(chart_tenures),
                        name="Principal", marker_color="#8B5CF6"
                    ))
                    fig_tc.add_trace(go.Bar(
                        x=[f"{t}m" for t in chart_tenures], y=chart_interests,
                        name="Interest", marker_color="#F59E0B"
                    ))
                    fig_tc.update_layout(
                        barmode="stack",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#94A3B8'), margin=dict(t=10, b=10, l=10, r=10),
                        yaxis=dict(gridcolor="#2A2E3F", title="Amount (₹)"),
                        legend=dict(orientation="h", y=1.1)
                    )
                    st.plotly_chart(fig_tc, use_container_width=True)

                # ── Smart Suggestions ────────────────────────────────────
                st.markdown("### 💡 AI-Powered Smart Suggestions")
                suggestions = generate_smart_suggestions(
                    risk_score, emi, c_income, loan_amount,
                    loan_tenure, c_dti, c_credit, c_defaults, interest_rate
                )
                for s in suggestions:
                    st.markdown(render_suggestion_card(*s), unsafe_allow_html=True)

                # ── Tenure Comparison Table ──────────────────────────────
                with st.expander("📋 Detailed Tenure Comparison Table", expanded=False):
                    tenure_df = generate_tenure_comparison(loan_amount, c_income, risk_score)
                    st.dataframe(tenure_df, hide_index=True, use_container_width=True)

                # ── Amortization Schedule ────────────────────────────────
                with st.expander("📆 Amortization Schedule", expanded=False):
                    amort_df = generate_amortization_schedule(loan_amount, interest_rate, loan_tenure)
                    st.dataframe(amort_df.head(24), hide_index=True, use_container_width=True)
                    if len(amort_df) > 24:
                        st.caption(f"Showing first 24 of {len(amort_df)} months. Full schedule available in the downloaded report.")

                    fig_amort = go.Figure()
                    fig_amort.add_trace(go.Scatter(
                        x=amort_df["Month"], y=amort_df["Principal"],
                        name="Principal", fill='tonexty', line=dict(color="#8B5CF6"),
                        fillcolor="rgba(139, 92, 246, 0.15)"
                    ))
                    fig_amort.add_trace(go.Scatter(
                        x=amort_df["Month"], y=amort_df["Interest"],
                        name="Interest", fill='tonexty', line=dict(color="#F59E0B"),
                        fillcolor="rgba(245, 158, 11, 0.15)"
                    ))
                    fig_amort.update_layout(
                        title="Principal vs Interest Over Time",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#94A3B8'), margin=dict(t=40, b=10),
                        yaxis=dict(gridcolor="#2A2E3F", title="Amount (₹)"),
                        xaxis=dict(title="Month"),
                        legend=dict(orientation="h", y=1.1)
                    )
                    st.plotly_chart(fig_amort, use_container_width=True)

                # ── Feature Importance ───────────────────────────────────
                with st.expander("🧠 Feature Importance (Model Explainability)", expanded=False):
                    fi = res.get("feature_importances", {})
                    if fi:
                        fi_df = pd.DataFrame({
                            "Feature": list(fi.keys()),
                            "Importance": list(fi.values())
                        }).sort_values("Importance", ascending=True)
                        fig_fi = px.bar(
                            fi_df, x="Importance", y="Feature", orientation="h",
                            color="Importance",
                            color_continuous_scale=["#38BDF8", "#8B5CF6", "#EF4444"]
                        )
                        fig_fi.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#94A3B8'), margin=dict(t=10, b=10, l=10, r=10),
                            xaxis=dict(gridcolor="#2A2E3F"),
                            showlegend=False, coloraxis_showscale=False
                        )
                        st.plotly_chart(fig_fi, use_container_width=True)

                # ── Application History ──────────────────────────────────
                past_apps = db.get_customer_applications(customer["name"])
                if len(past_apps) > 1:
                    with st.expander(f"📜 Application History ({len(past_apps)} assessments)", expanded=False):
                        history_rows = []
                        for pa in past_apps:
                            history_rows.append({
                                "Ref": pa.get("application_id", "—"),
                                "Date": pa.get("created_at", "").strftime("%d-%b-%Y %I:%M %p") if hasattr(pa.get("created_at", ""), "strftime") else "—",
                                "Loan": f"₹{pa.get('loan_amount', 0):,.0f}",
                                "Tenure": f"{pa.get('loan_tenure_months', 0)} mo",
                                "Risk Score": pa.get("risk_score", "—"),
                                "Grade": pa.get("risk_grade", "—"),
                                "Verdict": pa.get("verdict", "—"),
                            })
                        st.dataframe(pd.DataFrame(history_rows), hide_index=True, use_container_width=True)

                        # Risk trend chart
                        if len(past_apps) >= 2:
                            trend_data = []
                            for pa in reversed(past_apps):
                                trend_data.append({
                                    "Assessment": pa.get("application_id", ""),
                                    "Risk Score": pa.get("risk_score", 0)
                                })
                            fig_trend = px.line(
                                pd.DataFrame(trend_data), x="Assessment", y="Risk Score",
                                markers=True, line_shape="spline"
                            )
                            fig_trend.update_traces(line_color="#A855F7", line_width=3, marker_size=10)
                            fig_trend.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#94A3B8'), margin=dict(t=10, b=10),
                                yaxis=dict(gridcolor="#2A2E3F", range=[0, 100])
                            )
                            st.plotly_chart(fig_trend, use_container_width=True)

                # ── Downloadable Report ──────────────────────────────────
                st.markdown("### 📋 Downloadable Report")
                report_text = f"""═══════════════════════════════════════════════════════════
        LOAN RISK ASSESSMENT REPORT
        Application ID: {app_id or 'N/A'}
        Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}
═══════════════════════════════════════════════════════════

APPLICANT PROFILE
─────────────────────────────────────────────────────────
Name:               {customer['name']}
Father's Name:      {customer.get('father_name', '—')}
Age:                {c_age} years
Employment:         {customer.get('employment_type', '—')}
Monthly Income:     ₹{c_income:,.0f}
Monthly Debt:       ₹{c_debt:,.0f}
Credit Score:       {c_credit}
Previous Defaults:  {c_defaults}
DTI Ratio:          {c_dti:.2f}%

LOAN DETAILS
─────────────────────────────────────────────────────────
Requested Amount:   ₹{loan_amount:,.0f}
Tenure:             {loan_tenure} months
Interest Rate:      {interest_rate}% p.a.
Monthly EMI:        ₹{emi:,.0f}
Total Interest:     ₹{total_interest:,.0f}
Total Payable:      ₹{total_payable:,.0f}

RISK ASSESSMENT
─────────────────────────────────────────────────────────
Risk Score:         {risk_score} / 100
Risk Grade:         {grade} ({grade_label})
Category:           {res['presentation_category']}
Default Probability:{res['high_risk_probability']}%
Verdict:            {res['raw_class_label']}

FINANCIAL ANALYSIS
─────────────────────────────────────────────────────────
EMI / Income Ratio: {emi_to_income:.1f}%
Max Eligible Loan:  ₹{max_eligible:,.0f}

RECOMMENDATIONS
─────────────────────────────────────────────────────────
"""
                for s in suggestions:
                    report_text += f"{s[1]} {s[2]}: {s[3]}\n"
                    if s[4]:
                        report_text += f"   → {s[4]}\n"
                    report_text += "\n"
                report_text += "═══════════════════════════════════════════════════════════\n"
                report_text += "Generated by FinTech Risk AI — Loan Risk Assessment System\n"

                cp1, cp2 = st.columns(2)
                with cp1:
                    st.download_button(
                        "📥 Download Report (TXT)",
                        data=report_text,
                        file_name=f"risk_report_{app_id or 'report'}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with cp2:
                    json_payload = json.dumps({
                        "application_id": app_id,
                        "customer": customer["name"],
                        "risk_score": risk_score,
                        "risk_grade": grade,
                        "verdict": res["raw_class_label"],
                        "default_probability": res["high_risk_probability"],
                        "loan_amount": loan_amount,
                        "tenure_months": loan_tenure,
                        "emi": round(emi, 2),
                        "interest_rate": interest_rate,
                        "total_payable": round(total_payable, 2),
                    }, indent=2)
                    st.download_button(
                        "📥 Download Payload (JSON)",
                        data=json_payload,
                        file_name=f"risk_payload_{app_id or 'payload'}.json",
                        mime="application/json",
                        use_container_width=True
                    )


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 4 — CUSTOMER DATABASE
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📋 Customer Database":
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">📋 CUSTOMER DATABASE</div>
        <div class="top-subtitle">View all registered customers, document status & application history</div>
    </div>
    """, unsafe_allow_html=True)

    if not db.connected:
        st.error("🔴 MongoDB is offline.")
        st.stop()

    customers = db.get_all_customers()
    if not customers:
        st.info("📭 No customers registered yet. Use the **Customer Onboarding** page to register.")
    else:
        st.markdown(f"##### Total Registered: **{len(customers)}** customers")

        # Search / filter
        filter_name = st.text_input("🔍 Filter by name", placeholder="Type to filter...")

        rows = []
        filtered_customers = []
        for c in customers:
            if filter_name and filter_name.lower() not in c.get("name", "").lower():
                continue

            docs = c.get("documents", {})
            doc_status = ""
            doc_status += "✅" if "aadhaar" in docs else "❌"
            doc_status += " | "
            doc_status += "✅" if "pan" in docs else "❌"
            doc_status += " | "
            doc_status += "✅" if "salary_slip" in docs else "❌"

            kyc = c.get("kyc_status", "pending")
            has_aadhaar = "aadhaar" in docs
            has_pan = "pan" in docs
            has_salary_slip = "salary_slip" in docs
            has_all_docs = has_aadhaar and has_pan and has_salary_slip
            is_cust_verified = (kyc == "verified") and has_all_docs

            if is_cust_verified:
                kyc_display = "✅ Verified"
            elif kyc == "rejected":
                kyc_display = "❌ Rejected"
            else:
                doc_count = sum(1 for d in (has_aadhaar, has_pan, has_salary_slip) if d)
                kyc_display = f"⏳ Incomplete ({doc_count}/3 Docs)"

            apps = db.get_customer_applications(c["name"])

            rows.append({
                "Name": c.get("name", "—"),
                "Gender": c.get("gender", "—"),
                "Age": c.get("age", "—"),
                "Phone": c.get("phone_number", "—"),
                "Income (₹)": f"₹{c.get('monthly_income', 0):,.0f}",
                "Credit Score": c.get("credit_score", "—"),
                "Employment": c.get("employment_type", "—"),
                "KYC Status": kyc_display,
                "Docs (Aadhaar|PAN|Salary)": doc_status,
                "Assessments": len(apps),
                "Registered": c.get("created_at", "").strftime("%d-%b-%Y") if hasattr(c.get("created_at", ""), "strftime") else "—"
            })
            filtered_customers.append(c)

        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("No customers match the filter.")

        # ── Document Download Section ────────────────────────────────────
        if filtered_customers:
            st.markdown("---")
            st.markdown("### 📎 Document Viewer & Download")
            st.caption("Select a customer to view and download their uploaded KYC documents.")

            cust_names = [c.get("name", "Unknown") for c in filtered_customers]
            selected_cust_name = st.selectbox("Select Customer", cust_names, key="doc_viewer_select")

            selected_cust = None
            for c in filtered_customers:
                if c.get("name") == selected_cust_name:
                    selected_cust = c
                    break

            if selected_cust:
                cust_id = str(selected_cust["_id"])
                docs = selected_cust.get("documents", {})

                if not docs:
                    st.info("No documents uploaded for this customer.")
                else:
                    doc_cols = st.columns(3)
                    doc_types = [
                        ("aadhaar", "🪪 Aadhaar Card", doc_cols[0]),
                        ("pan", "💳 PAN Card", doc_cols[1]),
                        ("salary_slip", "📄 Salary Slip", doc_cols[2]),
                    ]

                    for doc_key, doc_label, col in doc_types:
                        with col:
                            if doc_key in docs:
                                doc_meta = docs[doc_key]
                                st.markdown(f"""
                                <div class="glass-box" style="text-align:center; padding:14px;">
                                    <p style="color:#22C55E; font-weight:700; margin:0 0 4px 0;">{doc_label}</p>
                                    <p style="color:#94A3B8; font-size:0.75rem; margin:0;">
                                        {doc_meta.get('filename', 'unnamed')} ({doc_meta.get('size_bytes', 0) / 1024:.1f} KB)
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

                                # Fetch full document data for download
                                full_doc = db.get_customer_document(cust_id, doc_key)
                                if full_doc and "data" in full_doc:
                                    file_data = base64.b64decode(full_doc["data"])
                                    st.download_button(
                                        f"📥 Download {doc_label}",
                                        data=file_data,
                                        file_name=full_doc.get("filename", f"{doc_key}_document"),
                                        mime=full_doc.get("content_type", "application/octet-stream"),
                                        use_container_width=True,
                                        key=f"dl_{cust_id}_{doc_key}"
                                    )
                            else:
                                st.markdown(f"""
                                <div class="glass-box" style="text-align:center; padding:14px;">
                                    <p style="color:#EF4444; font-weight:700; margin:0 0 4px 0;">{doc_label}</p>
                                    <p style="color:#64748B; font-size:0.75rem; margin:0;">Not uploaded</p>
                                </div>
                                """, unsafe_allow_html=True)

        # Recent applications summary
        st.markdown("---")
        st.markdown("### 📊 Recent Loan Assessments")
        all_apps = db.get_all_applications()
        if all_apps:
            app_rows = []
            for a in all_apps[:20]:
                app_rows.append({
                    "Ref ID": a.get("application_id", "—"),
                    "Customer": a.get("customer_name", "—"),
                    "Loan (₹)": f"₹{a.get('loan_amount', 0):,.0f}",
                    "Tenure": f"{a.get('loan_tenure_months', 0)} mo",
                    "Risk Score": a.get("risk_score", "—"),
                    "Grade": a.get("risk_grade", "—"),
                    "Verdict": a.get("verdict", "—"),
                    "Date": a.get("created_at", "").strftime("%d-%b-%Y %I:%M %p") if hasattr(a.get("created_at", ""), "strftime") else "—"
                })
            st.dataframe(pd.DataFrame(app_rows), hide_index=True, use_container_width=True)
        else:
            st.info("No loan assessments yet.")


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 5 — WHAT-IF SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════

elif False: # What-If Simulator disabled
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">🎛️ INTERACTIVE WHAT-IF SIMULATOR</div>
        <div class="top-subtitle">Adjust financial levers in real-time to simulate risk migration & EMI impact</div>
    </div>
    """, unsafe_allow_html=True)

    if load_error:
        st.error("Model unavailable.")
    else:
        sc1, sc2 = st.columns(2)
        with sc1:
            sim_income = st.slider("Monthly Income (₹)", 15000, 250000, 75000, step=5000)
            sim_debt = st.slider("Monthly Debt Payments (₹)", 0, 120000, 20000, step=2000)
            sim_credit = st.slider("Credit Score (CIBIL)", 300, 850, 720, step=10)
        with sc2:
            sim_loan = st.slider("Requested Loan Amount (₹)", 50000, 3000000, 500000, step=25000)
            sim_term = st.slider("Loan Tenure (Months)", 6, 360, 36, step=6)
            sim_defaults = st.slider("Previous Defaults", 0, 5, 0)
            sim_age = st.slider("Age", 20, 70, 32)

        sim_dti = calculate_dti(sim_debt, sim_income)
        sim_df = prepare_input_dataframe(
            age=sim_age, monthly_income=sim_income, loan_amount=sim_loan,
            loan_term_months=sim_term, credit_score=sim_credit,
            previous_defaults=sim_defaults, monthly_debt_payment=sim_debt, dti=sim_dti
        )
        sim_res = predictor.predict(sim_df)
        sim_grade, sim_grade_color, sim_grade_label = get_risk_grade(sim_res["risk_score"])
        sim_rate = get_interest_rate(sim_res["risk_score"])
        sim_emi = compute_emi(sim_loan, sim_rate, sim_term)
        sim_emi_pct = (sim_emi / sim_income * 100) if sim_income > 0 else 0

        st.markdown("---")
        st.markdown("### ⚡ Real-time Simulated Results")

        sm1, sm2, sm3, sm4, sm5 = st.columns(5)
        with sm1:
            st.metric("RISK SCORE", f"{sim_res['risk_score']} / 100")
        with sm2:
            st.metric("RISK GRADE", f"{sim_grade} ({sim_grade_label})")
        with sm3:
            st.metric("MONTHLY EMI", f"₹{sim_emi:,.0f}")
        with sm4:
            st.metric("EMI / INCOME", f"{sim_emi_pct:.1f}%")
        with sm5:
            st.metric("DTI RATIO", f"{sim_dti:.1f}%")

        st.progress(min(sim_res["risk_score"] / 100.0, 1.0))

        # Show affordability gauge
        wif1, wif2 = st.columns(2)
        with wif1:
            fig_sim = go.Figure(go.Indicator(
                mode="gauge+number", value=sim_res["risk_score"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Score", 'font': {'color': '#F8FAFC', 'size': 14}},
                number={'font': {'color': '#F8FAFC', 'size': 32}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#94A3B8'},
                    'bar': {'color': sim_grade_color},
                    'bgcolor': "#151824",
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(34, 197, 94, 0.15)"},
                        {'range': [30, 60], 'color': "rgba(234, 179, 8, 0.15)"},
                        {'range': [60, 100], 'color': "rgba(239, 68, 68, 0.15)"},
                    ]
                }
            ))
            fig_sim.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=10))
            st.plotly_chart(fig_sim, use_container_width=True)

        with wif2:
            remaining = max(sim_income - sim_emi - sim_debt, 0)
            fig_sim_aff = px.pie(
                names=["EMI", "Existing Debt", "Disposable"],
                values=[sim_emi, sim_debt, remaining],
                color_discrete_sequence=["#38BDF8", "#F59E0B", "#22C55E"],
                hole=0.55, title="Income Allocation"
            )
            fig_sim_aff.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'),
                margin=dict(t=40, b=10), height=250
            )
            st.plotly_chart(fig_sim_aff, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 6 — PORTFOLIO ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📊 Portfolio Analytics":
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">📊 LOAN PORTFOLIO ANALYTICS</div>
        <div class="top-subtitle">Exploratory distribution patterns across historical applicant records</div>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists(DATA_PATH):
        st.dataframe(df_raw.head(10), use_container_width=True)

        ac1, ac2 = st.columns(2)
        with ac1:
            fig_p = px.pie(
                df_raw, names="Risk_Label", title="Class Ratio (0=Low Risk, 1=High Risk)",
                color_discrete_sequence=["#22C55E", "#EF4444"], hole=0.4
            )
            fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
            st.plotly_chart(fig_p, use_container_width=True)
        with ac2:
            fig_h = px.histogram(
                df_raw, x="Credit_Score", color="Risk_Label",
                title="Credit Score Distribution vs. Risk Label", nbins=30,
                color_discrete_map={0: "#22C55E", 1: "#EF4444"}
            )
            fig_h.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
            st.plotly_chart(fig_h, use_container_width=True)

        # Additional analytics
        ac3, ac4 = st.columns(2)
        with ac3:
            if "Loan_Amount" in df_raw.columns and "Monthly_Income" in df_raw.columns:
                fig_scatter = px.scatter(
                    df_raw, x="Monthly_Income", y="Loan_Amount", color="Risk_Label",
                    title="Income vs Loan Amount",
                    color_discrete_map={0: "#22C55E", 1: "#EF4444"},
                    opacity=0.6
                )
                fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
                st.plotly_chart(fig_scatter, use_container_width=True)
        with ac4:
            if "DTI" in df_raw.columns:
                fig_dti = px.histogram(
                    df_raw, x="DTI", color="Risk_Label",
                    title="DTI Distribution by Risk",
                    color_discrete_map={0: "#22C55E", 1: "#EF4444"}, nbins=25
                )
                fig_dti.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
                st.plotly_chart(fig_dti, use_container_width=True)
    else:
        st.warning("Dataset not found at expected path.")


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 7 — MODEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════

elif page == "🤖 Model Intelligence":
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">🤖 MODEL ARCHITECTURE & XAI</div>
        <div class="top-subtitle">Explainable AI — Understanding the prediction engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-box">
        <h3 style="color:#F8FAFC;">Model Technical Architecture</h3>
        <ul style="color:#CBD5E1;">
            <li><b style="color:#8B5CF6;">Ensemble Classifier:</b> Random Forest (150 trees, max depth = 10, balanced class weights)</li>
            <li><b style="color:#38BDF8;">Preprocessing:</b> Median SimpleImputer for handling missing entries without data leakage</li>
            <li><b style="color:#22C55E;">Feature Attributes:</b> Age, Monthly Income, Loan Amount, Loan Term, Credit Score, Previous Defaults, Monthly Debt Payment, DTI %</li>
            <li><b style="color:#F59E0B;">Explainability:</b> SHAP (SHapley Additive exPlanations) TreeExplainer for feature-level contribution analysis</li>
            <li><b style="color:#A855F7;">Risk Grading:</b> A+ to E scale based on predicted default probability, mapped to indicative interest rates</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-box">
        <h3 style="color:#F8FAFC;">System Pipeline</h3>
        <ol style="color:#CBD5E1;">
            <li><b>Customer Registration (KYC)</b> → Identity verification (Aadhaar + PAN format validation) + document upload → MongoDB</li>
            <li><b>Data Retrieval</b> → Search customer by name → auto-fetch financial profile from database</li>
            <li><b>Feature Engineering</b> → DTI calculation, feature alignment with training schema</li>
            <li><b>Imputation</b> → Median imputer handles any missing values consistently</li>
            <li><b>ML Inference</b> → Random Forest predicts default probability</li>
            <li><b>Risk Scoring</b> → Probability mapped to 0-100 risk score and A+-E grade</li>
            <li><b>Advisory Engine</b> → EMI calculation, tenure optimization, smart suggestions</li>
            <li><b>Report Generation</b> → Comprehensive downloadable assessment report</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Show feature importances if model loaded
    if predictor and predictor.is_loaded:
        st.markdown("#### 🧠 Feature Importance (Global)")
        fi = dict(zip(
            predictor.expected_features,
            predictor.rf_model.feature_importances_
        ))
        fi_df = pd.DataFrame({
            "Feature": list(fi.keys()),
            "Importance": list(fi.values())
        }).sort_values("Importance", ascending=True)
        fig_fi = px.bar(
            fi_df, x="Importance", y="Feature", orientation="h",
            color="Importance",
            color_continuous_scale=["#38BDF8", "#8B5CF6", "#EF4444"]
        )
        fig_fi.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8'), margin=dict(t=10, b=10),
            xaxis=dict(gridcolor="#2A2E3F"),
            showlegend=False, coloraxis_showscale=False, height=350
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    # Risk grading table
    st.markdown("#### 📊 Risk Grade Mapping")
    grade_data = [
        {"Grade": "A+", "Score Range": "0 – 10", "Category": "Exceptional", "Interest Rate": "8.5%", "Color": "🟢"},
        {"Grade": "A", "Score Range": "11 – 20", "Category": "Excellent", "Interest Rate": "8.5%", "Color": "🟢"},
        {"Grade": "B+", "Score Range": "21 – 30", "Category": "Very Good", "Interest Rate": "10.5%", "Color": "🟡"},
        {"Grade": "B", "Score Range": "31 – 40", "Category": "Good", "Interest Rate": "10.5%", "Color": "🟡"},
        {"Grade": "C+", "Score Range": "41 – 50", "Category": "Fair", "Interest Rate": "13.0%", "Color": "🟠"},
        {"Grade": "C", "Score Range": "51 – 60", "Category": "Below Average", "Interest Rate": "13.0%", "Color": "🟠"},
        {"Grade": "D", "Score Range": "61 – 75", "Category": "Poor", "Interest Rate": "17.0-19.0%", "Color": "🔴"},
        {"Grade": "E", "Score Range": "76 – 100", "Category": "Very High Risk", "Interest Rate": "23.0%", "Color": "🔴"},
    ]
    st.dataframe(pd.DataFrame(grade_data), hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 8 — PERFORMANCE BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════

elif False: # Performance Benchmark disabled
    st.markdown("""
    <div class="top-bar">
        <div class="top-title">📈 COMPARATIVE MODEL BENCHMARK</div>
        <div class="top-subtitle">Benchmark Random Forest against alternative ML classification algorithms</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ EXECUTE MULTI-MODEL BENCHMARK", use_container_width=True):
        with st.spinner("Training and evaluating algorithms..."):
            res_df = evaluate_all_models()
            st.dataframe(res_df, use_container_width=True)

            fig_bm = px.bar(
                res_df.melt(id_vars=["Model"], var_name="Metric", value_name="Score"),
                x="Model", y="Score", color="Metric", barmode="group",
                title="Algorithm Performance Comparison",
                color_discrete_sequence=["#38BDF8", "#818CF8", "#22C55E", "#EAB308", "#EF4444"]
            )
            fig_bm.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8')
            )
            st.plotly_chart(fig_bm, use_container_width=True)

            # Radar chart
            st.markdown("#### 🕸️ Model Performance Radar")
            metrics = [c for c in res_df.columns if c != "Model"]
            fig_radar = go.Figure()
            colors = ["#38BDF8", "#22C55E", "#A855F7", "#F59E0B"]
            for i, (_, row) in enumerate(res_df.iterrows()):
                vals = [row[m] for m in metrics] + [row[metrics[0]]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals, theta=metrics + [metrics[0]],
                    name=row["Model"], fill='toself',
                    line=dict(color=colors[i % len(colors)])
                ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(range=[0, 1], gridcolor="#2A2E3F", tickcolor="#94A3B8"),
                    angularaxis=dict(gridcolor="#2A2E3F")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8'),
                showlegend=True, height=450
            )
            st.plotly_chart(fig_radar, use_container_width=True)
