"""
Preprocessing utilities for the Loan Risk Assessment System.
Ensures consistency between raw inputs, training data, and inference pipelines.
"""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

EXPECTED_FEATURES = [
    "Age",
    "Monthly_Income",
    "Loan_Amount",
    "Loan_Term_Months",
    "Credit_Score",
    "Previous_Defaults",
    "Monthly_Debt_Payment",
    "DTI"
]


def calculate_dti(monthly_debt_payment: float, monthly_income: float) -> float:
    """Calculates Debt-to-Income (DTI) ratio percentage."""
    if monthly_income <= 0:
        return 0.0
    return float((monthly_debt_payment / monthly_income) * 100.0)


def prepare_input_dataframe(
    age: float,
    monthly_income: float,
    loan_amount: float,
    loan_term_months: float,
    credit_score: float,
    previous_defaults: float,
    monthly_debt_payment: float,
    dti: float = None
) -> pd.DataFrame:
    """Constructs a single-row Pandas DataFrame matching exact feature names and order."""
    if dti is None:
        dti = calculate_dti(monthly_debt_payment, monthly_income)

    data = {
        "Age": [float(age)],
        "Monthly_Income": [float(monthly_income)],
        "Loan_Amount": [float(loan_amount)],
        "Loan_Term_Months": [float(loan_term_months)],
        "Credit_Score": [float(credit_score)],
        "Previous_Defaults": [float(previous_defaults)],
        "Monthly_Debt_Payment": [float(monthly_debt_payment)],
        "DTI": [float(dti)]
    }

    df = pd.DataFrame(data)
    return df[EXPECTED_FEATURES]


def apply_imputation(df: pd.DataFrame, imputer: SimpleImputer) -> pd.DataFrame:
    """Applies a fitted SimpleImputer to the feature DataFrame."""
    imputed_array = imputer.transform(df)
    return pd.DataFrame(imputed_array, columns=df.columns)


def generate_synthetic_dataset(num_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """Generates a realistic synthetic loan applicant dataset if no dataset exists."""
    np.random.seed(random_state)

    age = np.random.randint(20, 68, size=num_samples)
    monthly_income = np.random.exponential(scale=35000, size=num_samples) + 15000
    monthly_income = np.clip(monthly_income, 12000, 250000)

    loan_amount = monthly_income * np.random.uniform(2, 24, size=num_samples)
    loan_amount = np.clip(loan_amount, 20000, 5000000)

    loan_term_months = np.random.choice([12, 24, 36, 48, 60, 72, 84, 120, 180, 240, 360], size=num_samples)
    credit_score = np.random.normal(loc=650, scale=100, size=num_samples)
    credit_score = np.clip(credit_score, 300, 850).astype(int)

    previous_defaults = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=[0.72, 0.18, 0.06, 0.03, 0.01])
    monthly_debt_payment = monthly_income * np.random.uniform(0.05, 0.65, size=num_samples)
    dti = (monthly_debt_payment / monthly_income) * 100.0

    risk_score_raw = (
        (800 - credit_score) * 0.35 +
        (dti) * 1.8 +
        (previous_defaults * 45) +
        (loan_amount / monthly_income) * 2.5 -
        (age * 0.2)
    )

    probability = 1 / (1 + np.exp(-(risk_score_raw - 120) / 35))
    risk_label = (probability > 0.45).astype(int)

    df = pd.DataFrame({
        "Age": age,
        "Monthly_Income": np.round(monthly_income, 2),
        "Loan_Amount": np.round(loan_amount, 2),
        "Loan_Term_Months": loan_term_months,
        "Credit_Score": credit_score,
        "Previous_Defaults": previous_defaults,
        "Monthly_Debt_Payment": np.round(monthly_debt_payment, 2),
        "DTI": np.round(dti, 2),
        "Risk_Label": risk_label
    })

    mask = np.random.rand(*df.iloc[:, :-1].shape) < 0.02
    df_features = df.iloc[:, :-1].mask(mask)
    df_features["Risk_Label"] = df["Risk_Label"]

    return df_features