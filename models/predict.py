"""
predict.py
----------
Inference module used by the Django backend.
Provides two callable functions:
  - predict_stress(features_dict) → {stress_level, burnout_score, probabilities}
  - predict_emotion(text)         → {emotion, confidence, all_scores}
"""

import os, joblib
import numpy as np
from tensorflow.keras.models             import load_model        # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = BASE_DIR

STRUCTURED_FEATURES = [
    "dass_stress", "dass_anxiety", "dass_depression",
    "pss_score", "sleep_hours", "study_hours",
    "social_hours", "exercise_freq", "caffeine_cups", "screen_hours",
]
MAX_LEN = 30

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_scaler              = None
_label_encoder       = None
_classifier          = None
_burnout_reg         = None
_lstm_model          = None
_tokenizer           = None
_emotion_le          = None


def _get_stress_artifacts():
    global _scaler, _label_encoder, _classifier, _burnout_reg
    if _scaler is None:
        _scaler        = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        _label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
        _classifier    = joblib.load(os.path.join(MODELS_DIR, "best_classifier.pkl"))
        _burnout_reg   = joblib.load(os.path.join(MODELS_DIR, "burnout_regressor.pkl"))
    return _scaler, _label_encoder, _classifier, _burnout_reg


def _get_emotion_artifacts():
    global _lstm_model, _tokenizer, _emotion_le
    if _lstm_model is None:
        _lstm_model = load_model(os.path.join(MODELS_DIR, "lstm_emotion.keras"))
        _tokenizer  = joblib.load(os.path.join(MODELS_DIR, "tokenizer.pkl"))
        _emotion_le = joblib.load(os.path.join(MODELS_DIR, "emotion_label_encoder.pkl"))
    return _lstm_model, _tokenizer, _emotion_le


# ── Public API ────────────────────────────────────────────────────────────────

def predict_stress(features_dict: dict) -> dict:
    """
    Given a dict of feature values, return:
      {stress_level: str, burnout_score: float, probabilities: dict}
    """
    scaler, le, clf, reg = _get_stress_artifacts()

    # Build feature vector in correct order
    try:
        x = np.array([[float(features_dict.get(f, 0)) for f in STRUCTURED_FEATURES]])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid feature input: {e}")

    x_scaled = scaler.transform(x)

    # Classification
    label_idx  = clf.predict(x_scaled)[0]
    stress_label = le.inverse_transform([label_idx])[0]

    probs_raw = (
        clf.predict_proba(x_scaled)[0]
        if hasattr(clf, "predict_proba")
        else np.zeros(len(le.classes_))
    )
    prob_dict = {cls: round(float(p), 4) for cls, p in zip(le.classes_, probs_raw)}

    # Regression
    burnout_score = float(reg.predict(x_scaled)[0])
    burnout_score = round(min(max(burnout_score, 0.0), 100.0), 2)

    return {
        "stress_level":  stress_label,
        "burnout_score": burnout_score,
        "probabilities": prob_dict,
    }


def predict_emotion(text: str) -> dict:
    """
    Given a text string, return:
      {emotion: str, confidence: float, all_scores: dict}
    """
    model, tokenizer, le = _get_emotion_artifacts()

    seq     = tokenizer.texts_to_sequences([text])
    padded  = pad_sequences(seq, maxlen=MAX_LEN, padding="post", truncating="post")
    probs   = model.predict(padded, verbose=0)[0]

    label_idx  = int(np.argmax(probs))
    emotion    = le.inverse_transform([label_idx])[0]
    confidence = float(probs[label_idx])
    all_scores = {cls: round(float(p), 4) for cls, p in zip(le.classes_, probs)}

    return {
        "emotion":    emotion,
        "confidence": round(confidence, 4),
        "all_scores": all_scores,
    }


if __name__ == "__main__":
    # Quick smoke test (requires trained models)
    sample_features = {
        "dass_stress": 28, "dass_anxiety": 22, "dass_depression": 18,
        "pss_score": 30, "sleep_hours": 4.5, "study_hours": 12,
        "social_hours": 1, "exercise_freq": 0, "caffeine_cups": 4, "screen_hours": 8,
    }
    result = predict_stress(sample_features)
    print("Stress Prediction:", result)

    text = "I'm so anxious about my final exams, I can't sleep at all."
    emotion_result = predict_emotion(text)
    print("Emotion Prediction:", emotion_result)
