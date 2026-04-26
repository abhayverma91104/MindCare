"""
train_lstm.py
-------------
Trains a Keras LSTM model on the chat_dataset.csv for 4-class emotion
detection: anxious / sad / angry / neutral.

Outputs:
  - models/lstm_emotion.h5 (or .keras)
  - models/tokenizer.pkl
  - models/emotion_label_encoder.pkl
"""

import os, sys, joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import LabelEncoder
from sklearn.metrics         import classification_report, f1_score

import tensorflow as tf
from tensorflow.keras.preprocessing.text     import Tokenizer        # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences    # type: ignore
from tensorflow.keras.models   import Sequential                     # type: ignore
from tensorflow.keras.layers   import (Embedding, LSTM, Dropout,     # type: ignore
                                        Dense, Bidirectional,
                                        GlobalMaxPooling1D)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau  # type: ignore
from tensorflow.keras.utils    import to_categorical                  # type: ignore

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = BASE_DIR

CHAT_CSV   = os.path.join(DATA_DIR, "chat_dataset.csv")
MAX_WORDS  = 5000
MAX_LEN    = 30
EMBED_DIM  = 64
LSTM_UNITS = 64
BATCH_SIZE = 32
EPOCHS     = 20
DROPOUT    = 0.4


def load_chat_data():
    if not os.path.exists(CHAT_CSV):
        raise FileNotFoundError(
            "chat_dataset.csv not found. Run `python data/generate_dataset.py` first."
        )
    df = pd.read_csv(CHAT_CSV).dropna()
    return df["text"].values, df["emotion"].values


def build_model(vocab_size, num_classes):
    model = Sequential([
        Embedding(vocab_size, EMBED_DIM, input_length=MAX_LEN),
        Bidirectional(LSTM(LSTM_UNITS, return_sequences=True)),
        Dropout(DROPOUT),
        Bidirectional(LSTM(32)),
        Dropout(DROPOUT),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(num_classes, activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    print("Loading chat dataset...")
    texts, labels = load_chat_data()
    print(f"  Total samples: {len(texts)}")

    # Label encode
    le = LabelEncoder()
    y_encoded = le.fit_transform(labels)
    num_classes = len(le.classes_)
    print(f"  Classes ({num_classes}): {le.classes_}")

    # Tokenize
    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    X = pad_sequences(sequences, maxlen=MAX_LEN, padding="post", truncating="post")
    y = to_categorical(y_encoded, num_classes)

    # Split
    X_tr, X_te, y_tr, y_te, y_raw_tr, y_raw_te = train_test_split(
        X, y, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"  Train: {len(X_tr)}, Test: {len(X_te)}")

    # Build & train
    print("\nBuilding LSTM model...")
    model = build_model(MAX_WORDS, num_classes)
    model.summary()

    callbacks = [
        EarlyStopping(patience=4, restore_best_weights=True, monitor="val_accuracy"),
        ReduceLROnPlateau(factor=0.5, patience=2, min_lr=1e-5),
    ]

    print("\nTraining...")
    history = model.fit(
        X_tr, y_tr,
        validation_data=(X_te, y_te),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    print("\nEvaluating...")
    y_pred_probs = model.predict(X_te)
    y_pred = np.argmax(y_pred_probs, axis=1)

    report = classification_report(y_raw_te, y_pred, target_names=le.classes_)
    f1 = f1_score(y_raw_te, y_pred, average="weighted")
    print(f"\nF1 (weighted): {f1:.4f}")
    print(f"Classification Report:\n{report}")

    # Save
    model_path = os.path.join(MODELS_DIR, "lstm_emotion.keras")
    model.save(model_path)
    print(f"  Saved → {model_path}")

    joblib.dump(tokenizer, os.path.join(MODELS_DIR, "tokenizer.pkl"))
    joblib.dump(le,        os.path.join(MODELS_DIR, "emotion_label_encoder.pkl"))
    print("  Saved → tokenizer.pkl, emotion_label_encoder.pkl")

    print("\nLSTM training complete!")


if __name__ == "__main__":
    main()
