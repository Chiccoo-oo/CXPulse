import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

def run_statistical_analysis(df):
    """
    Executes 5 rigorous statistical analyses on customer servicing data:
    1. One-Way ANOVA (Resolution Time across Channels)
    2. Chi-Square Test (Escalation vs Issue Category)
    3. Pearson Correlation Matrix (Servicing & Customer Metrics)
    4. Parametric 95% Confidence Intervals for Core KPIs
    5. Logistic Regression for Escalation Risk & Odds Ratios
    """
    print("=== Running Statistical Analysis Engine ===")
    results = {}

    # 1. One-Way ANOVA: Resolution Time across Complaint Channels
    channels = df["complaint_channel"].unique()
    channel_groups = [df[df["complaint_channel"] == ch]["resolution_time_days"].values for ch in channels]
    f_stat, anova_p = stats.f_oneway(*channel_groups)
    
    results["anova_test"] = {
        "test_name": "One-Way ANOVA (Resolution Time across Channels)",
        "f_statistic": float(round(f_stat, 4)),
        "p_value": float(anova_p),
        "is_significant": bool(anova_p < 0.05),
        "interpretation": "Resolution time differs significantly across servicing channels." if anova_p < 0.05 else "No statistically significant difference in resolution time across channels."
    }

    # 2. Chi-Square Test: Escalation Flag vs Issue Category
    contingency_table = pd.crosstab(df["issue"], df["escalation_flag"])
    chi2_stat, chi2_p, dof, expected = stats.chi2_contingency(contingency_table)

    results["chi_square_test"] = {
        "test_name": "Chi-Square Test of Independence (Escalation vs Issue Category)",
        "chi2_statistic": float(round(chi2_stat, 4)),
        "p_value": float(chi2_p),
        "degrees_of_freedom": int(dof),
        "is_significant": bool(chi2_p < 0.05),
        "interpretation": "Complaint escalation is strongly associated with issue category." if chi2_p < 0.05 else "Escalation is independent of issue category."
    }

    # 3. Pearson Correlation Matrix
    corr_cols = ["monthly_spend", "account_tenure_months", "transaction_frequency", "resolution_time_days", "satisfaction_score", "escalation_flag", "repeat_complaint_flag"]
    corr_df = df[corr_cols].corr()
    
    results["correlation_matrix"] = corr_df.round(4).to_dict()

    # 4. Parametric 95% Confidence Intervals
    # 4a. Mean Satisfaction Score 95% CI
    n_sat = df["satisfaction_score"].count()
    mean_sat = df["satisfaction_score"].mean()
    std_sat = df["satisfaction_score"].std()
    sem_sat = std_sat / np.sqrt(n_sat)
    ci_sat = stats.t.interval(0.95, df=n_sat-1, loc=mean_sat, scale=sem_sat)

    # 4b. Escalation Rate 95% CI (Proportion CI)
    n_esc = len(df)
    p_esc = df["escalation_flag"].mean()
    se_esc = np.sqrt(p_esc * (1 - p_esc) / n_esc)
    ci_esc = (p_esc - 1.96 * se_esc, p_esc + 1.96 * se_esc)

    results["confidence_intervals"] = {
        "satisfaction_score_mean": round(float(mean_sat), 3),
        "satisfaction_score_95ci": (round(float(ci_sat[0]), 3), round(float(ci_sat[1]), 3)),
        "escalation_rate_mean_pct": round(float(p_esc * 100), 2),
        "escalation_rate_95ci_pct": (round(float(ci_esc[0] * 100), 2), round(float(ci_esc[1] * 100), 2))
    }

    # 5. Logistic Regression for Escalation Risk (Odds Ratios & p-values)
    df_reg = df.copy()
    # Dummy encoding
    df_reg = pd.get_dummies(df_reg, columns=["complaint_channel", "product"], drop_first=True, dtype=int)
    
    feature_cols = [c for c in df_reg.columns if c.startswith("complaint_channel_") or c.startswith("product_")] + ["resolution_time_days", "repeat_complaint_flag", "monthly_spend"]
    
    X = df_reg[feature_cols]
    X = sm.add_constant(X)
    y = df_reg["escalation_flag"]

    model = sm.Logit(y, X).fit(disp=0)
    conf = model.conf_int()
    
    params = model.params
    pvalues = model.pvalues
    odds_ratios = np.exp(params)

    summary_rows = []
    for feat in X.columns:
        summary_rows.append({
            "feature": feat,
            "coefficient": round(float(params[feat]), 4),
            "odds_ratio": round(float(odds_ratios[feat]), 4),
            "p_value": float(pvalues[feat]),
            "is_statistically_significant": bool(pvalues[feat] < 0.05)
        })

    results["logistic_regression"] = {
        "prsquared": round(float(model.prsquared), 4),
        "summary": summary_rows
    }

    print("Statistical Analysis completed successfully.")
    return results

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    res = run_statistical_analysis(df_clean)
    print("ANOVA P-Value:", res["anova_test"]["p_value"])
    print("Chi2 P-Value:", res["chi_square_test"]["p_value"])
