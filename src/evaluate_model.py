"""
Multi-Model Evaluation & Benchmark Module.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

from src import preprocessing


def evaluate_all_models(data_path: str = "data/loan_data.csv") -> pd.DataFrame:
    """Trains and benchmarks multiple algorithms on the exact dataset split."""
    if not os.path.exists(data_path):
        preprocessing.generate_synthetic_dataset().to_csv(data_path, index=False)

    df = pd.read_csv(data_path)
    X = df[preprocessing.EXPECTED_FEATURES]
    y = df["Risk_Label"] if "Risk_Label" in df.columns else df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    imputer = SimpleImputer(strategy="median")
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
    }

    if XGB_AVAILABLE:
        models["XGBoost"] = xgb.XGBClassifier(eval_metric="logloss", random_state=42)

    results = []

    for name, clf in models.items():
        clf.fit(X_train_imp, y_train)
        y_pred = clf.predict(X_test_imp)
        y_proba = clf.predict_proba(X_test_imp)[:, 1] if hasattr(clf, "predict_proba") else y_pred

        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred, zero_division=0),
            "Recall": recall_score(y_test, y_pred, zero_division=0),
            "F1 Score": f1_score(y_test, y_pred, zero_division=0),
            "ROC-AUC": roc_auc_score(y_test, y_proba)
        })

    return pd.DataFrame(results).round(4)
