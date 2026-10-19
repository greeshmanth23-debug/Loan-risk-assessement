"""
Inference & Explainability Engine for Loan Risk Assessment.
"""

import os
import joblib
import numpy as np
import pandas as pd

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


class LoanRiskPredictor:
    def __init__(self, model_dir: str = "model"):
        self.model_dir = model_dir
        self.rf_model = None
        self.imputer = None
        self.expected_features = None
        self.is_loaded = False
        self.load_artifacts()

    def load_artifacts(self):
        """Loads serialized model, imputer, and feature list safely."""
        model_path = os.path.join(self.model_dir, "loan_risk_random_forest.pkl")
        imputer_path = os.path.join(self.model_dir, "loan_risk_imputer.pkl")
        features_path = os.path.join(self.model_dir, "loan_risk_features.pkl")

        if not (os.path.exists(model_path) and os.path.exists(imputer_path) and os.path.exists(features_path)):
            raise FileNotFoundError("Model files missing. Run 'python -m src.train_model' first.")

        self.rf_model = joblib.load(model_path)
        self.imputer = joblib.load(imputer_path)
        self.expected_features = joblib.load(features_path)
        self.is_loaded = True

    def predict(self, input_df: pd.DataFrame) -> dict:
        """Runs feature alignment, imputation, inference, and risk scoring."""
        if not self.is_loaded:
            self.load_artifacts()

        input_aligned = input_df[self.expected_features]
        imputed_array = self.imputer.transform(input_aligned)
        imputed_df = pd.DataFrame(imputed_array, columns=self.expected_features)

        raw_prediction = int(self.rf_model.predict(imputed_df)[0])
        probabilities = self.rf_model.predict_proba(imputed_df)[0]

        low_risk_prob = float(probabilities[0])
        high_risk_prob = float(probabilities[1])
        risk_score = float(np.round(high_risk_prob * 100.0, 2))

        if high_risk_prob <= 0.30:
            presentation_category = "Low Risk"
            risk_color = "#28a745"
        elif high_risk_prob <= 0.60:
            presentation_category = "Moderate Risk"
            risk_color = "#ffc107"
        else:
            presentation_category = "High Risk"
            risk_color = "#dc3545"

        shap_values_dict = self.compute_shap_explanations(imputed_df)

        return {
            "binary_prediction": raw_prediction,
            "raw_class_label": "HIGH RISK" if raw_prediction == 1 else "LOW RISK",
            "presentation_category": presentation_category,
            "risk_color": risk_color,
            "low_risk_probability": np.round(low_risk_prob * 100.0, 2),
            "high_risk_probability": np.round(high_risk_prob * 100.0, 2),
            "risk_score": risk_score,
            "shap_explanation": shap_values_dict,
            "feature_importances": dict(zip(self.expected_features, self.rf_model.feature_importances_))
        }

    def compute_shap_explanations(self, imputed_df: pd.DataFrame) -> dict:
        """Computes SHAP values for explainability."""
        if not SHAP_AVAILABLE:
            return {"status": "unavailable", "reason": "SHAP library not installed"}

        try:
            explainer = shap.TreeExplainer(self.rf_model)
            shap_values = explainer.shap_values(imputed_df)

            if isinstance(shap_values, list):
                vals = shap_values[1][0]
            elif len(shap_values.shape) == 3:
                vals = shap_values[0, :, 1]
            else:
                vals = shap_values[0]

            contributions = dict(zip(self.expected_features, [float(v) for v in vals]))
            return {"status": "success", "contributions": contributions}
        except Exception as e:
            return {"status": "error", "reason": str(e)}