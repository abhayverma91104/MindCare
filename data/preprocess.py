"""
preprocess.py
-------------
Preprocesses stress_dataset.csv and chat_dataset.csv:
  - Cleans & normalizes structured features
  - Tokenizes text for LSTM training
  - Saves scaler, tokenizer, and processed arrays to models/ directory
"""

import os, sys, joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer   # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR  = os.path.join(BASE_DIR, "..", "models")
DATA_DIR    = BASE_DIR

STRESS_CSV  = os.path.join(DATA_DIR, "stress_dataset.csv")
CHAT_CSV    = os.path.join(DATA_DIR, "chat_dataset.csv")

os.makedirs(MODELS_DIR, exist_ok=True)

STRUCTURED_FEATURES = [
    "dass_stress", "dass_anxiety", "dass_depression",
    "pss_score", "sleep_hours", "study_hours",
    "social_hours", "exercise_freq", "caffeine_cups", "screen_hours",
]

MAX_WORDS    = 5000
MAX_LEN      = 30
TEST_SIZE    = 0.2


# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------
def preprocess_stress():
    print("Preprocessing stress dataset...")
    df = pd.read_csv(STRESS_CSV)

    # Drop duplicates / na
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    X = df[STRUCTURED_FEATURES].values
    y_label = df["stress_label"].values
    y_burnout = df["burnout_score"].values.astype(float)

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_label)          # High=0, Low=1, Moderate=2

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Save artifacts
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(le,     os.path.join(MODELS_DIR, "label_encoder.pkl"))
    print(f"  Classes: {le.classes_}")

    # Save processed dataset
    processed_df = df.copy()
    processed_df[STRUCTURED_FEATURES] = X_scaled
    processed_df.to_csv(os.path.join(DATA_DIR, "processed_data.csv"), index=False)
    print(f"  Saved processed_data.csv ({len(processed_df)} rows)")

    # Train/test split
    X_train, X_test, y_train, y_test, yb_train, yb_test = train_test_split(
        X_scaled, y_encoded, y_burnout, test_size=TEST_SIZE, random_state=42, stratify=y_encoded
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    return X_train, X_test, y_train, y_test, yb_train, yb_test, le


# ---------------------------------------------------------------------------
# Text / chat data
# ---------------------------------------------------------------------------
def preprocess_chat():
    print("\nPreprocessing chat dataset...")
    df = pd.read_csv(CHAT_CSV)
    df.dropna(inplace=True)

    texts  = df["text"].values
    labels = df["emotion"].values

    # Label encode
    le_emotion = LabelEncoder()
    y_encoded = le_emotion.fit_transform(labels)
    print(f"  Emotion classes: {le_emotion.classes_}")

    # Tokenize
    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded    = pad_sequences(sequences, maxlen=MAX_LEN, padding="post", truncating="post")

    # Save artifacts
    joblib.dump(tokenizer,   os.path.join(MODELS_DIR, "tokenizer.pkl"))
    joblib.dump(le_emotion,  os.path.join(MODELS_DIR, "emotion_label_encoder.pkl"))

    X_train, X_test, y_train, y_test = train_test_split(
        padded, y_encoded, test_size=TEST_SIZE, random_state=42, stratify=y_encoded
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test, le_emotion


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    preprocess_stress()
    preprocess_chat()
    print("\nPreprocessing complete! Artifacts saved to models/")
