"""
feature_engineering.py
-----------------------
Additional feature engineering on top of raw data:
  - Composite stress index
  - Sleep quality score
  - TF-IDF features for text (optional, used by classical NLP path)
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_DIR   = BASE_DIR

os.makedirs(MODELS_DIR, exist_ok=True)


def add_structured_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered columns to the stress dataframe."""
    df = df.copy()

    # Sleep quality: penalize < 6 or > 9 hours
    df["sleep_quality"] = df["sleep_hours"].apply(
        lambda h: 1.0 if 6 <= h <= 9 else (h / 6.0 if h < 6 else 9 / h)
    )

    # Work-life balance ratio (social vs study)
    df["balance_ratio"] = df["social_hours"] / (df["study_hours"] + 1e-6)

    # Composite wellness index (higher = better)
    df["wellness_index"] = (
        df["sleep_quality"] * 30 +
        df["exercise_freq"] * 5 +
        df["balance_ratio"] * 10 -
        df["caffeine_cups"] * 3 -
        df["screen_hours"] * 2
    )

    return df


def build_tfidf(texts, max_features=3000):
    """Fit TF-IDF vectorizer on text corpus and save it."""
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        stop_words="english",
    )
    X_tfidf = vectorizer.fit_transform(texts)
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"))
    print(f"  TF-IDF shape: {X_tfidf.shape}")
    return X_tfidf


if __name__ == "__main__":
    print("Running feature engineering...")

    # Structured features
    stress_path = os.path.join(DATA_DIR, "stress_dataset.csv")
    df = pd.read_csv(stress_path)
    df_feat = add_structured_features(df)
    out_path = os.path.join(DATA_DIR, "stress_features.csv")
    df_feat.to_csv(out_path, index=False)
    print(f"  Saved enriched dataset → {out_path}")
    print(f"  New columns: sleep_quality, balance_ratio, wellness_index")

    # TF-IDF on chat sentences
    chat_path = os.path.join(DATA_DIR, "chat_dataset.csv")
    chat_df   = pd.read_csv(chat_path)
    print("\nBuilding TF-IDF on chat corpus...")
    build_tfidf(chat_df["text"].values)
    print("  Saved tfidf_vectorizer.pkl")

    print("\nFeature engineering complete!")
