"""
Training Pipeline for the Loan Risk Assessment System.
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

from src import preprocessing


def train_and_save_pipeline(data_path: str = "data/loan_data.csv", model_dir: str = "model"):
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    if not os.path.exists(data_path):
        print(f"[INFO] Dataset not found at {data_path}. Generating dataset...")
        df = preprocessing.generate_synthetic_dataset(num_samples=1500)
        df.to_csv(data_path, index=False)
        print(f"[SUCCESS] Dataset saved to {data_path}")
    else:
        df = pd.read_csv(data_path)

    X = df[preprocessing.EXPECTED_FEATURES]
    y = df["Risk_Label"] if "Risk_Label" in df.columns else df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    imputer = SimpleImputer(strategy="median")
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight="balanced"
    )
    rf_model.fit(X_train_imp, y_train)

    y_pred = rf_model.predict(X_test_imp)
    y_proba = rf_model.predict_proba(X_test_imp)[:, 1]

    print("\n================ MODEL EVALUATION REPORT ================")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")
    print("=========================================================\n")

    joblib.dump(rf_model, os.path.join(model_dir, "loan_risk_random_forest.pkl"))
    joblib.dump(imputer, os.path.join(model_dir, "loan_risk_imputer.pkl"))
    joblib.dump(preprocessing.EXPECTED_FEATURES, os.path.join(model_dir, "loan_risk_features.pkl"))

    print(f"[SUCCESS] Model artifacts saved to '{model_dir}/'")


if __name__ == "__main__":
    train_and_save_pipeline()