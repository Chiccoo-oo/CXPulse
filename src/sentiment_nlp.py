import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def analyze_sentiment_and_topics(df):
    """
    Performs sentiment analysis and TF-IDF topic theme extraction on complaint text narratives.
    Returns DataFrame with derived sentiment scores and summary theme table.
    """
    print("=== Running NLP & Sentiment Analysis Engine ===")
    df_nlp = df.copy()

    # Rule-based / Lexicon Sentiment Engine (Lightweight, robust, fast)
    neg_words = set([
        "frustrated", "disappointed", "severe", "unauthorized", "failed", "crash",
        "crashing", "crashed", "terrible", "delay", "delayed", "error", "unresponsive",
        "worst", "poor", "unacceptable", "dispute", "disputed", "stolen", "locked",
        "refund", "unrecognized", "chargeback", "penalty", "wrongfully"
    ])
    pos_words = set([
        "resolved", "helpful", "prompt", "appreciated", "good", "satisfied", "thanks",
        "pleased", "great", "excellent", "fast"
    ])

    def compute_sentiment(text):
        if not isinstance(text, str) or not text.strip():
            return 0.0, "NEUTRAL"
        
        words = re.findall(r'\w+', text.lower())
        if not words:
            return 0.0, "NEUTRAL"
            
        neg_count = sum(1 for w in words if w in neg_words)
        pos_count = sum(1 for w in words if w in pos_words)
        
        score = (pos_count - neg_count) / float(len(words) + 1)
        
        if score < -0.05 or neg_count >= 1:
            label = "NEGATIVE"
        elif score > 0.05:
            label = "POSITIVE"
        else:
            label = "NEUTRAL"
            
        return round(float(score), 4), label

    sent_res = df_nlp["complaint_text"].apply(compute_sentiment)
    df_nlp["sentiment_score"] = [r[0] for r in sent_res]
    df_nlp["sentiment_label"] = [r[1] for r in sent_res]

    # Theme Extraction via TF-IDF Bigrams
    texts = df_nlp["complaint_text"].dropna().astype(str).tolist()
    
    vectorizer = TfidfVectorizer(ngram_range=(2, 3), max_features=10, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    theme_rows = []
    for feat in feature_names:
        mask = df_nlp["complaint_text"].str.contains(re.escape(feat), case=False, na=False)
        sub_df = df_nlp[mask]
        vol = len(sub_df)
        if vol > 0:
            neg_pct = (sub_df["sentiment_label"] == "NEGATIVE").mean() * 100
            avg_res = sub_df["resolution_time_days"].mean()
            theme_rows.append({
                "theme": feat.title(),
                "complaint_volume": vol,
                "negative_sentiment_pct": round(float(neg_pct), 2),
                "avg_resolution_time_days": round(float(avg_res), 2)
            })

    theme_df = pd.DataFrame(theme_rows).sort_values(by="complaint_volume", ascending=False)

    print("NLP Sentiment & Topic Analysis completed.")
    return df_nlp, theme_df

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    df_out, themes = analyze_sentiment_and_topics(df_clean)
    print("Sentiment Distribution:\n", df_out["sentiment_label"].value_counts())
    print("\nTop Themes:\n", themes)
