import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    precision_recall_curve, auc, confusion_matrix
)
from sklearn.preprocessing import StandardScaler

def train_escalation_model(df, random_state=42):
    """
    Trains Logistic Regression Baseline and Random Forest for complaint escalation risk.
    Handles class imbalance via class weighting, evaluates F1/ROC-AUC/PR-AUC, and computes feature importance.
    """
    print("=== Training Complaint Escalation Risk Model ===")
    df_ml = df.copy()

    # Define Feature Matrix X and Target y
    categorical_cols = ["product", "complaint_channel", "issue", "customer_segment"]
    df_encoded = pd.get_dummies(df_ml, columns=categorical_cols, drop_first=True, dtype=int)

    numerical_cols = [
        "resolution_time_days", "repeat_complaint_flag", "monthly_spend",
        "account_tenure_months", "transaction_frequency", "customer_age"
    ]
    
    # Feature columns
    dummy_cols = [c for c in df_encoded.columns if any(c.startswith(prefix + "_") for prefix in categorical_cols)]
    feature_cols = numerical_cols + dummy_cols

    X = df_encoded[feature_cols]
    y = df_encoded["escalation_flag"]

    # Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Baseline Model: Logistic Regression with Class Weighting
    log_reg = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state)
    log_reg.fit(X_train_scaled, y_train)

    y_pred_log = log_reg.predict(X_test_scaled)
    y_prob_log = log_reg.predict_proba(X_test_scaled)[:, 1]

    prec_log, rec_log, _ = precision_recall_curve(y_test, y_prob_log)
    pr_auc_log = auc(rec_log, prec_log)

    metrics_log = {
        "model": "Logistic Regression (Baseline)",
        "precision": round(float(precision_score(y_test, y_pred_log)), 4),
        "recall": round(float(recall_score(y_test, y_pred_log)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred_log)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob_log)), 4),
        "pr_auc": round(float(pr_auc_log), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_log).tolist()
    }

    # 2. Main Model: Random Forest Classifier with Class Weighting
    rf_clf = RandomForestClassifier(
        n_estimators=150, max_depth=10, class_weight="balanced_subsample",
        random_state=random_state, n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)

    y_pred_rf = rf_clf.predict(X_test)
    y_prob_rf = rf_clf.predict_proba(X_test)[:, 1]

    prec_rf, rec_rf, _ = precision_recall_curve(y_test, y_prob_rf)
    pr_auc_rf = auc(rec_rf, prec_rf)

    metrics_rf = {
        "model": "Random Forest Classifier",
        "precision": round(float(precision_score(y_test, y_pred_rf)), 4),
        "recall": round(float(recall_score(y_test, y_pred_rf)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred_rf)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob_rf)), 4),
        "pr_auc": round(float(pr_auc_rf), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_rf).tolist()
    }

    # Feature Importance (Random Forest)
    importances = rf_clf.feature_importances_
    feat_imp_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    top_features = feat_imp_df.head(10).to_dict(orient="records")

    print(f"Model Training complete. RF ROC-AUC: {metrics_rf['roc_auc']}, PR-AUC: {metrics_rf['pr_auc']}")

    return {
        "logistic_regression": metrics_log,
        "random_forest": metrics_rf,
        "top_feature_importance": top_features,
        "y_test": y_test.values,
        "y_prob_rf": y_prob_rf
    }

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    res = train_escalation_model(df_clean)
    print("Random Forest Metrics:", res["random_forest"])
    print("Top Features:", res["top_feature_importance"][:5])
