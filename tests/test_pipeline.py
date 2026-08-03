import os
import sqlite3
import pandas as pd
import pytest

from src.data_generator import generate_synthetic_complaints
from src.data_pipeline import run_data_pipeline
from src.eda_analysis import perform_eda
from src.statistical_analysis import run_statistical_analysis
from src.sentiment_nlp import analyze_sentiment_and_topics
from src.customer_segmentation import perform_customer_segmentation
from src.escalation_model import train_escalation_model
from src.business_insights import generate_business_insights

def test_data_generation():
    """Verify synthetic dataset generator produces valid shape & schema."""
    df = generate_synthetic_complaints(num_records=500, seed=123)
    assert len(df) == 500
    assert "complaint_id" in df.columns
    assert "customer_id" in df.columns
    assert "escalation_flag" in df.columns
    assert df["escalation_flag"].isin([0, 1]).all()

def test_data_pipeline_and_sqlite():
    """Verify data pipeline runs ETL and populates SQLite database."""
    db_test = os.path.join("data", "processed", "cxpulse.db")
    df_clean = run_data_pipeline(db_path=db_test)
    
    assert len(df_clean) > 0
    assert os.path.exists(db_test)

    conn = sqlite3.connect(db_test)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_complaints")
    fact_count = cursor.fetchone()[0]
    conn.close()

    assert fact_count > 0

def test_statistical_analysis():
    """Verify statistical engine outputs valid p-values and confidence intervals."""
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    stats_res = run_statistical_analysis(df_clean)

    assert 0.0 <= stats_res["anova_test"]["p_value"] <= 1.0
    assert 0.0 <= stats_res["chi_square_test"]["p_value"] <= 1.0
    assert "satisfaction_score_mean" in stats_res["confidence_intervals"]

def test_sentiment_nlp():
    """Verify sentiment engine classifies narratives and extracts themes."""
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    df_nlp, theme_df = analyze_sentiment_and_topics(df_clean.head(500))

    assert "sentiment_label" in df_nlp.columns
    assert set(df_nlp["sentiment_label"].unique()).issubset({"POSITIVE", "NEUTRAL", "NEGATIVE"})
    assert len(theme_df) > 0

def test_escalation_ml_model():
    """Verify predictive escalation model trains and achieves valid evaluation metrics."""
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    model_res = train_escalation_model(df_clean.head(2000))

    rf_metrics = model_res["random_forest"]
    assert 0.5 <= rf_metrics["roc_auc"] <= 1.0
    assert 0.0 <= rf_metrics["f1_score"] <= 1.0
    assert len(model_res["top_feature_importance"]) > 0

def test_business_insights():
    """Verify programmatic insight engine returns valid structured recommendations."""
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    insights = generate_business_insights(df_clean)

    assert len(insights["key_insights"]) >= 3
    assert len(insights["recommended_actions"]) >= 3
