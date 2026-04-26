"""
train_classical.py
------------------
Trains Logistic Regression, Random Forest, and SVM on the structured
stress dataset. Outputs:
  - models/logistic_regression.pkl
  - models/random_forest.pkl
  - models/svm.pkl
  - models/best_model.pkl  (highest F1)
  - Prints accuracy, F1, and confusion matrix for each model.
"""

import os, sys, joblib, json
import numpy as np
import pandas as pd
from sklearn.linear_model   import LogisticRegression
from sklearn.ensemble       import RandomForestClassifier
from sklearn.svm            import SVC
from sklearn.preprocessing  import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics        import (accuracy_score, f1_score,
                                    classification_report, confusion_matrix)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = BASE_DIR

STRUCTURED_FEATURES = [
    "dass_stress", "dass_anxiety", "dass_depression",
    "pss_score", "sleep_hours", "study_hours",
    "social_hours", "exercise_freq", "caffeine_cups", "screen_hours",
]


def load_data():
    stress_path = os.path.join(DATA_DIR, "stress_dataset.csv")
    if not os.path.exists(stress_path):
        raise FileNotFoundError(
            f"stress_dataset.csv not found. Run `python data/generate_dataset.py` first."
        )
    df = pd.read_csv(stress_path).dropna().drop_duplicates()

    X = df[STRUCTURED_FEATURES].values
    y_label   = df["stress_label"].values
    y_burnout = df["burnout_score"].values.astype(float)

    le = LabelEncoder()
    y_encoded = le.fit_transform(y_label)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(le,     os.path.join(MODELS_DIR, "label_encoder.pkl"))

    X_tr, X_te, y_tr, y_te, yb_tr, yb_te = train_test_split(
        X_scaled, y_encoded, y_burnout,
        test_size=0.2, random_state=42, stratify=y_encoded
    )
    return X_tr, X_te, y_tr, y_te, yb_tr, yb_te, le, scaler


def train_and_evaluate(name, model, X_tr, X_te, y_tr, y_te, le):
    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)

    acc  = accuracy_score(y_te, y_pred)
    f1   = f1_score(y_te, y_pred, average="weighted")
    cm   = confusion_matrix(y_te, y_pred)
    report = classification_report(y_te, y_pred, target_names=le.classes_)

    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  F1 Score : {f1:.4f}")
    print(f"  Confusion Matrix:\n{cm}")
    print(f"  Classification Report:\n{report}")

    filename = name.lower().replace(" ", "_") + ".pkl"
    joblib.dump(model, os.path.join(MODELS_DIR, filename))
    print(f"  Saved → models/{filename}")

    return acc, f1


def train_burnout_regressor(X_tr, X_te, yb_tr, yb_te):
    """Train Random Forest regressor for burnout score prediction."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics  import mean_absolute_error, r2_score

    reg = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    reg.fit(X_tr, yb_tr)
    y_pred = reg.predict(X_te)

    mae = mean_absolute_error(yb_te, y_pred)
    r2  = r2_score(yb_te, y_pred)

    print(f"\n{'='*55}")
    print(f"  Burnout Score Regressor (RandomForestRegressor)")
    print(f"{'='*55}")
    print(f"  MAE : {mae:.4f}")
    print(f"  R²  : {r2:.4f}")

    joblib.dump(reg, os.path.join(MODELS_DIR, "burnout_regressor.pkl"))
    print(f"  Saved → models/burnout_regressor.pkl")
    return reg


def main():
    print("Loading data...")
    X_tr, X_te, y_tr, y_te, yb_tr, yb_te, le, scaler = load_data()
    print(f"  Train size: {len(X_tr)}, Test size: {len(X_te)}")

    classifiers = [
        ("Logistic Regression",
         LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
        ("Random Forest",
         RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)),
        ("SVM",
         SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)),
    ]

    results = {}
    best_f1, best_name = 0, ""

    for name, clf in classifiers:
        acc, f1 = train_and_evaluate(name, clf, X_tr, X_te, y_tr, y_te, le)
        results[name] = {"accuracy": round(acc, 4), "f1": round(f1, 4)}
        if f1 > best_f1:
            best_f1, best_name = f1, name

    # Save best model alias
    best_filename = best_name.lower().replace(" ", "_") + ".pkl"
    import shutil
    shutil.copy(
        os.path.join(MODELS_DIR, best_filename),
        os.path.join(MODELS_DIR, "best_classifier.pkl")
    )
    print(f"\n  Best model: {best_name} (F1={best_f1:.4f}) → models/best_classifier.pkl")

    # Burnout regressor
    train_burnout_regressor(X_tr, X_te, yb_tr, yb_te)

    # Save summary
    summary = {
        "best_classifier": best_name,
        "results": results,
        "features": STRUCTURED_FEATURES,
        "classes": list(le.classes_),
    }
    with open(os.path.join(MODELS_DIR, "training_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\n  Saved training_summary.json")
    print("\nClassical model training complete!")


if __name__ == "__main__":
    main()
