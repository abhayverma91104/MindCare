"""
generate_dataset.py
-------------------
Generates two synthetic datasets:
  1. stress_dataset.csv  - 2000 student records (DASS/PSS-style + behavioral)
  2. chat_dataset.csv    - 2400 labeled sentences for emotion detection (LSTM training)
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

np.random.seed(42)
N = 2000

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 1. Stress / Burnout Dataset
# ---------------------------------------------------------------------------
def generate_stress_dataset(n=N):
    # DASS-21 subscores (each 0-42)
    dass_stress    = np.random.randint(0, 43, n)
    dass_anxiety   = np.random.randint(0, 43, n)
    dass_depression = np.random.randint(0, 43, n)

    # PSS-like score (0-40)
    pss_score = np.random.randint(0, 41, n)

    # Behavioral indicators
    sleep_hours   = np.clip(np.random.normal(6.5, 1.5, n), 2, 10).round(1)
    study_hours   = np.clip(np.random.normal(7.0, 2.0, n), 1, 16).round(1)
    social_hours  = np.clip(np.random.normal(3.0, 1.5, n), 0, 8).round(1)
    exercise_freq = np.random.randint(0, 8, n)          # days/week
    caffeine_cups = np.random.randint(0, 7, n)          # cups/day
    screen_hours  = np.clip(np.random.normal(5.0, 2.0, n), 0, 14).round(1)

    # Composite stress index (higher = more stressed)
    composite = (
        dass_stress * 0.30 +
        dass_anxiety * 0.25 +
        dass_depression * 0.20 +
        pss_score * 0.25 +
        (10 - sleep_hours) * 1.5 +
        study_hours * 0.8 +
        caffeine_cups * 0.5 -
        exercise_freq * 0.7 -
        social_hours * 0.4 +
        screen_hours * 0.3
    )

    # Burnout score (0-100, normalized from composite)
    scaler = MinMaxScaler(feature_range=(0, 100))
    burnout_score = scaler.fit_transform(composite.reshape(-1, 1)).flatten().round(2)

    # Stress labels derived from burnout score
    def label(score):
        if score < 35:
            return "Low"
        elif score < 65:
            return "Moderate"
        else:
            return "High"

    stress_label = [label(s) for s in burnout_score]

    df = pd.DataFrame({
        "dass_stress":      dass_stress,
        "dass_anxiety":     dass_anxiety,
        "dass_depression":  dass_depression,
        "pss_score":        pss_score,
        "sleep_hours":      sleep_hours,
        "study_hours":      study_hours,
        "social_hours":     social_hours,
        "exercise_freq":    exercise_freq,
        "caffeine_cups":    caffeine_cups,
        "screen_hours":     screen_hours,
        "burnout_score":    burnout_score,
        "stress_label":     stress_label,
    })
    return df


# ---------------------------------------------------------------------------
# 2. Chat / Emotion Dataset
# ---------------------------------------------------------------------------
EMOTION_SENTENCES = {
    "anxious": [
        "I can't stop worrying about my upcoming exams.",
        "My heart races whenever I think about deadlines.",
        "I feel uneasy and restless all the time.",
        "I'm scared I'll fail and disappoint everyone.",
        "Everything feels overwhelming and out of control.",
        "I have trouble sleeping because of all my worries.",
        "I feel like something bad is about to happen.",
        "I'm constantly on edge and can't relax.",
        "The pressure is making it hard to breathe.",
        "I don't know how I'll manage everything this week.",
        "Every little thing stresses me out lately.",
        "I feel a constant sense of dread.",
        "My mind won't stop racing with what-ifs.",
        "I feel paralyzed by the amount of work I have.",
        "I'm terrified of making mistakes in front of others.",
        "I get panic attacks whenever exams approach.",
        "I feel jittery and nervous for no clear reason.",
        "I can't focus because I'm always worried.",
        "I keep catastrophizing even small problems.",
        "The anxiety is affecting my physical health now.",
    ],
    "sad": [
        "I feel completely hopeless about my future.",
        "Nothing seems to bring me joy anymore.",
        "I've been crying a lot without knowing why.",
        "I feel so alone even when surrounded by people.",
        "I miss feeling happy and carefree.",
        "Everything feels pointless and meaningless.",
        "I don't have the energy to do anything.",
        "I feel like a burden to everyone around me.",
        "I've lost all motivation to study or socialize.",
        "I feel empty inside, like something is missing.",
        "I can't remember the last time I smiled genuinely.",
        "My grades are slipping and I feel like a failure.",
        "I wish someone understood what I'm going through.",
        "I feel invisible and unimportant.",
        "I've stopped reaching out to friends.",
        "I spend most days feeling numb and disconnected.",
        "I feel like I'm drowning in sadness.",
        "Life feels grey and colorless right now.",
        "I'm struggling to find any reason to keep going.",
        "I feel broken and don't know how to fix myself.",
    ],
    "angry": [
        "I'm so frustrated with the unfair grading system.",
        "My professors never listen to what students need.",
        "I'm furious about the amount of work assigned.",
        "Nobody respects my time or boundaries.",
        "I feel like I'm being treated unfairly.",
        "I can't stand the constant pressure being put on me.",
        "My classmates don't pull their weight in group work.",
        "I'm done with people dismissing my feelings.",
        "I get angry just thinking about the injustice.",
        "The system is broken and nobody cares to fix it.",
        "I feel exploited and unappreciated.",
        "I'm irritable, snapping at my friends for no reason.",
        "I want to quit everything and walk away.",
        "I'm resentful of how much is expected of me.",
        "I hate feeling like I have no control over my life.",
        "I'm sick of pretending everything is fine.",
        "Why do I have to suffer while others have it easy?",
        "I'm fed up with being the responsible one.",
        "Everything and everyone is annoying me today.",
        "I feel like screaming out of sheer frustration.",
    ],
    "neutral": [
        "I had a regular day attending classes and studying.",
        "Completed my assignment and took a lunch break.",
        "Watched a lecture online and made some notes.",
        "Met a friend for coffee and caught up on life.",
        "Finished my reading for today and went for a walk.",
        "Attended a study group session this afternoon.",
        "I cooked dinner, studied for an hour, then relaxed.",
        "Did some chores and reviewed last week's material.",
        "Had an average day, nothing particularly good or bad.",
        "Organized my study schedule for the coming week.",
        "Went to the library and worked on my project.",
        "Participated in a webinar related to my course.",
        "Reviewed notes from lecture and planned my week.",
        "Spent the evening reading and listening to music.",
        "Helped a classmate understand a difficult concept.",
        "Today was uneventful; just routine study and rest.",
        "Submitted a small assignment and reviewed feedback.",
        "Had breakfast, attended class, did some exercise.",
        "Caught up on emails and updated my planner.",
        "Worked on a coding exercise for a few hours calmly.",
    ],
    "joy": [
        "I had a really great day today!",
        "I finally aced that exam and I'm so happy.",
        "I feel amazing and super productive right now.",
        "Spent the afternoon hanging out with friends and laughing.",
        "My professor praised my assignment, I'm thrilled.",
        "Everything is going perfectly, I feel so much joy.",
        "I'm so excited about the upcoming weekend trip.",
        "I solved a really hard problem today and feel proud.",
        "It's sunny outside and my mood is fantastic.",
        "I got an internship offer! Best day ever.",
        "I feel energized and ready to take on anything.",
        "Finally finished my project and it feels so good.",
        "Life is beautiful, I just feel really grateful.",
        "I had a great workout and feel wonderful.",
        "I'm in such a good mood today, nothing can bring me down.",
        "My grades were much better than expected!",
        "I feel really positive about my future.",
        "Just had the best cup of coffee and feeling joyful.",
        "My friends surprised me today, I'm overjoyed.",
        "I'm so happy I finally understand this topic."
    ],
}


def generate_chat_dataset():
    rows = []
    for label, sentences in EMOTION_SENTENCES.items():
        # Multiply each category to get 2000 samples per class (total 10000)
        for i in range(100):
            for sentence in sentences:
                # Add slight noise variation
                rows.append({
                    "text": sentence,
                    "emotion": label,
                    "iteration": i,
                })
    df = pd.DataFrame(rows)[["text", "emotion"]]
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating stress dataset...")
    stress_df = generate_stress_dataset()
    stress_path = os.path.join(OUTPUT_DIR, "stress_dataset.csv")
    stress_df.to_csv(stress_path, index=False)
    print(f"  Saved {len(stress_df)} records → {stress_path}")
    print(f"  Label distribution:\n{stress_df['stress_label'].value_counts()}\n")

    print("Generating chat / emotion dataset...")
    chat_df = generate_chat_dataset()
    chat_path = os.path.join(OUTPUT_DIR, "chat_dataset.csv")
    chat_df.to_csv(chat_path, index=False)
    print(f"  Saved {len(chat_df)} records → {chat_path}")
    print(f"  Emotion distribution:\n{chat_df['emotion'].value_counts()}\n")

    print("Dataset generation complete!")
