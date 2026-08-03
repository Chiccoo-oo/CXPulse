import os
import sys

# Ensure root project directory is in Python path for module imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import streamlit as st

from src.eda_analysis import perform_eda
from src.statistical_analysis import run_statistical_analysis
from src.sentiment_nlp import analyze_sentiment_and_topics
from src.customer_segmentation import perform_customer_segmentation
from src.escalation_model import train_escalation_model
from src.business_insights import generate_business_insights

# Page Config & Dark Theme Aesthetics
st.set_page_config(
    page_title="CXPulse — Customer Experience Analytics Platform",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium dark theme UI
st.markdown("""
    <style>
        /* Main Application Dark Background */
        .stApp { background-color: #0e1117 !important; color: #e0e6ed !important; }
        .main { background-color: #0e1117 !important; }
        
        /* Metric Card Dark Styling */
        div[data-testid="stMetric"] {
            background-color: #1e222d !important;
            padding: 16px 20px !important;
            border-radius: 12px !important;
            border: 1px solid #2e3440 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        div[data-testid="stMetric"] label {
            color: #8892b0 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stMetricValue"] div {
            color: #00d2ff !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #161922 !important;
            border-right: 1px solid #2e3440 !important;
        }
        
        /* Custom Cards */
        .insight-card {
            background-color: #1e222d;
            padding: 18px 22px;
            border-radius: 10px;
            border-left: 5px solid #00d2ff;
            margin-bottom: 14px;
            color: #e0e6ed;
            font-size: 0.98rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        .recommendation-card {
            background-color: #1e222d;
            padding: 18px 22px;
            border-radius: 10px;
            border-left: 5px solid #00e676;
            margin-bottom: 14px;
            color: #e0e6ed;
            font-size: 0.98rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        
        /* Headings & Text */
        h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-family: 'Segoe UI', Roboto, sans-serif; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    db_path = os.path.join("data", "processed", "cxpulse.db")
    csv_path = os.path.join("data", "processed", "cleaned_complaints.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM fact_complaints", conn)
        conn.close()
    else:
        from src.data_pipeline import run_data_pipeline
        df = run_data_pipeline()
        
    df["complaint_date"] = pd.to_datetime(df["complaint_date"])
    return df

df_raw = load_data()

# SIDEBAR FILTERS
st.sidebar.title("💳 CXPulse Analytics Filters")
st.sidebar.markdown("---")

min_date = df_raw["complaint_date"].min().date()
max_date = df_raw["complaint_date"].max().date()

date_range = st.sidebar.date_input("Date Range", value=[min_date, max_date], min_value=min_date, max_value=max_date)

products = st.sidebar.multiselect("Product Line", options=sorted(df_raw["product"].unique()), default=sorted(df_raw["product"].unique()))
channels = st.sidebar.multiselect("Complaint Channel", options=sorted(df_raw["complaint_channel"].unique()), default=sorted(df_raw["complaint_channel"].unique()))
segments = st.sidebar.multiselect("Customer Segment", options=sorted(df_raw["customer_segment"].unique()), default=sorted(df_raw["customer_segment"].unique()))
severities = st.sidebar.multiselect("Severity Level", options=["LOW", "MEDIUM", "HIGH", "CRITICAL"], default=["LOW", "MEDIUM", "HIGH", "CRITICAL"])

# Apply Filters
start_dt = pd.to_datetime(date_range[0])
end_dt = pd.to_datetime(date_range[1]) if len(date_range) > 1 else start_dt + pd.Timedelta(days=1)

mask = (
    (df_raw["complaint_date"] >= start_dt) & 
    (df_raw["complaint_date"] <= end_dt) &
    (df_raw["product"].isin(products)) &
    (df_raw["complaint_channel"].isin(channels)) &
    (df_raw["customer_segment"].isin(segments)) &
    (df_raw["severity_level"].isin(severities))
)

df = df_raw[mask].copy()

# Header Banner
st.title("💳 CXPulse: Customer Complaints & Servicing Analytics Platform")
st.caption("SQL-Driven Customer Complaints, Sentiment & Operational Performance Analytics Platform")
st.markdown("---")

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview",
    "🧠 Customer Experience & Sentiment",
    "⚙️ Operational Performance & SLA",
    "🎯 Risk & Predictive Insights"
])

# ----------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ----------------------------------------------------
with tab1:
    st.subheader("Executive Servicing Dashboard")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    tot_complaints = len(df)
    uniq_cust = df["customer_id"].nunique()
    esc_rate = (df["escalation_flag"].mean() * 100) if tot_complaints > 0 else 0
    avg_res = df["resolution_time_days"].mean() if tot_complaints > 0 else 0
    sla_breach_rate = (df["sla_breach_flag"].mean() * 100) if tot_complaints > 0 else 0
    avg_csat = df["satisfaction_score"].mean() if tot_complaints > 0 else 0

    col1.metric("Total Complaints", f"{tot_complaints:,}")
    col2.metric("Unique Customers", f"{uniq_cust:,}")
    col3.metric("Escalation Rate", f"{esc_rate:.1f}%")
    col4.metric("Avg Resolution Time", f"{avg_res:.1f} Days")
    col5.metric("SLA Breach Rate", f"{sla_breach_rate:.1f}%")
    col6.metric("Average CSAT", f"{avg_csat:.2f} / 5.0")

    st.markdown("---")

    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("##### Monthly Complaint Volume & Escalation Rate Trend")
        df_monthly = df.set_index("complaint_date").resample("ME").agg(
            total_complaints=("complaint_id", "count"),
            escalation_rate=("escalation_flag", lambda x: x.mean() * 100)
        ).reset_index()

        fig_trend = px.line(
            df_monthly, x="complaint_date", y="total_complaints",
            title="Monthly Complaint Volume Trend",
            labels={"complaint_date": "Month", "total_complaints": "Complaint Count"},
            markers=True, template="plotly_dark"
        )
        fig_trend.update_traces(line_color="#00d2ff", line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.markdown("##### Complaints by Product Line")
        df_prod = df["product"].value_counts().reset_index()
        df_prod.columns = ["Product", "Count"]
        
        fig_prod = px.bar(
            df_prod, x="Count", y="Product", orientation="h",
            title="Complaint Distribution by Product",
            color="Count", color_continuous_scale="Blues", template="plotly_dark"
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("##### Channel Distribution")
        df_chan = df["complaint_channel"].value_counts().reset_index()
        df_chan.columns = ["Channel", "Count"]
        fig_chan = px.pie(
            df_chan, names="Channel", values="Count", hole=0.4,
            title="Servicing Channel Breakdown", template="plotly_dark"
        )
        st.plotly_chart(fig_chan, use_container_width=True)

    with c4:
        st.markdown("##### Severity Level Breakdown")
        df_sev = df["severity_level"].value_counts().reset_index()
        df_sev.columns = ["Severity", "Count"]
        fig_sev = px.bar(
            df_sev, x="Severity", y="Count", color="Severity",
            color_discrete_map={"LOW": "#4caf50", "MEDIUM": "#ff9800", "HIGH": "#f44336", "CRITICAL": "#d32f2f"},
            title="Complaint Volume by Severity", template="plotly_dark"
        )
        st.plotly_chart(fig_sev, use_container_width=True)

# ----------------------------------------------------
# TAB 2: CUSTOMER EXPERIENCE & SENTIMENT
# ----------------------------------------------------
with tab2:
    st.subheader("Customer Listening & Sentiment Analytics")

    if tot_complaints > 0:
        df_nlp, theme_df = analyze_sentiment_and_topics(df)
        df_seg, seg_summary = perform_customer_segmentation(df)

        sc1, sc2, sc3 = st.columns(3)
        neg_pct = (df_nlp["sentiment_label"] == "NEGATIVE").mean() * 100
        repeat_pct = df["repeat_complaint_flag"].mean() * 100
        
        sc1.metric("Negative Sentiment Share", f"{neg_pct:.1f}%")
        sc2.metric("Repeat Complaint Rate", f"{repeat_pct:.1f}%")
        sc3.metric("Customer Segments Identified", f"{len(seg_summary)}")

        st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### Sentiment Distribution")
            df_sent = df_nlp["sentiment_label"].value_counts().reset_index()
            df_sent.columns = ["Sentiment", "Count"]
            fig_sent = px.pie(
                df_sent, names="Sentiment", values="Count", hole=0.4,
                color="Sentiment", color_discrete_map={"NEGATIVE": "#f44336", "NEUTRAL": "#ffc107", "POSITIVE": "#4caf50"},
                title="Narrative Sentiment Breakdown", template="plotly_dark"
            )
            st.plotly_chart(fig_sent, use_container_width=True)

        with col_b:
            st.markdown("##### Top Complaint Themes (TF-IDF Narrative Extraction)")
            st.dataframe(theme_df, use_container_width=True, height=280)

        st.markdown("##### Customer Behavioral Segmentation (K-Means)")
        fig_cluster = px.scatter(
            df_seg, x="monthly_spend", y="resolution_time_days", color="cluster_name",
            size="satisfaction_score", hover_data=["customer_id", "product"],
            title="Customer Persona Map: Spend vs. Resolution Time", template="plotly_dark"
        )
        st.plotly_chart(fig_cluster, use_container_width=True)
    else:
        st.warning("No data available for current filter selection.")

# ----------------------------------------------------
# TAB 3: OPERATIONAL PERFORMANCE & SLA
# ----------------------------------------------------
with tab3:
    st.subheader("Operational Performance & Servicing Efficiency")

    if tot_complaints > 0:
        o1, o2 = st.columns(2)

        with o1:
            st.markdown("##### Resolution Time by Support Team & Channel")
            df_ops = df.groupby(["agent_team", "complaint_channel"])["resolution_time_days"].mean().unstack().fillna(0)
            fig_heat = px.imshow(
                df_ops, labels=dict(x="Channel", y="Support Team", color="Avg Days"),
                title="Average Resolution Days Heatmap", color_continuous_scale="Reds", template="plotly_dark"
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with o2:
            st.markdown("##### Resolution Time Distribution across Products")
            fig_box = px.box(
                df, x="product", y="resolution_time_days", color="product",
                title="Resolution Time Spread (Days)", template="plotly_dark"
            )
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("##### Operational SLA Breach Breakdown")
        df_sla = df.groupby(["product", "agent_team"]).agg(
            Total_Handled=("complaint_id", "count"),
            SLA_Breaches=("sla_breach_flag", "sum"),
            SLA_Breach_Pct=("sla_breach_flag", lambda x: round(x.mean() * 100, 2))
        ).reset_index()
        st.dataframe(df_sla, use_container_width=True)
    else:
        st.warning("No data available for operational analysis.")

# ----------------------------------------------------
# TAB 4: RISK & PREDICTIVE INSIGHTS
# ----------------------------------------------------
with tab4:
    st.subheader("Predictive Risk Modeling & Strategic Recommendations")

    if tot_complaints > 100:
        model_results = train_escalation_model(df)
        rf_metrics = model_results["random_forest"]
        top_feats = pd.DataFrame(model_results["top_feature_importance"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Escalation Model ROC-AUC", f"{rf_metrics['roc_auc']:.3f}")
        m2.metric("PR-AUC (Precision-Recall)", f"{rf_metrics['pr_auc']:.3f}")
        m3.metric("F1-Score", f"{rf_metrics['f1_score']:.3f}")
        m4.metric("Model Precision", f"{rf_metrics['precision']:.3f}")

        st.markdown("---")

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("##### Top Escalation Risk Factors (Model Feature Importance)")
            fig_feat = px.bar(
                top_feats, x="importance", y="feature", orientation="h",
                title="Random Forest Feature Importance",
                color="importance", color_continuous_scale="Viridis", template="plotly_dark"
            )
            st.plotly_chart(fig_feat, use_container_width=True)

        with rc2:
            st.markdown("##### Daily Complaint Volume & Anomaly Spikes")
            df_daily = df.set_index("complaint_date").resample("D")["complaint_id"].count().reset_index()
            df_daily["rolling_avg"] = df_daily["complaint_id"].rolling(14, min_periods=1).mean()
            df_daily["rolling_std"] = df_daily["complaint_id"].rolling(14, min_periods=1).std().fillna(1.0)
            df_daily["z_score"] = (df_daily["complaint_id"] - df_daily["rolling_avg"]) / df_daily["rolling_std"]
            df_daily["is_anomaly"] = df_daily["z_score"] >= 2.0

            fig_anom = px.line(df_daily, x="complaint_date", y="complaint_id", title="Daily Volume with 14-Day Rolling Baseline", template="plotly_dark")
            fig_anom.add_trace(gg.Scatter(
                x=df_daily[df_daily["is_anomaly"]]["complaint_date"],
                y=df_daily[df_daily["is_anomaly"]]["complaint_id"],
                mode="markers", name="Spike Anomaly (Z >= 2.0)", marker=dict(color="red", size=10, symbol="x")
            ))
            st.plotly_chart(fig_anom, use_container_width=True)

        st.markdown("---")
        st.subheader("💡 Key Business Insights & Actionable Recommendations")

        biz_insights = generate_business_insights(df)
        
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("#### Key Quantitative Insights")
            for ins in biz_insights["key_insights"]:
                st.markdown(f"<div class='insight-card'>📌 {ins}</div>", unsafe_allow_html=True)

        with ic2:
            st.markdown("#### Strategic Business Recommendations")
            for rec in biz_insights["recommended_actions"]:
                st.markdown(f"<div class='recommendation-card'>✅ {rec}</div>", unsafe_allow_html=True)

    else:
        st.warning("Insufficient records selected for predictive modeling. Expand filter criteria.")
