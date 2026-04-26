"""
nlp_analyzer.py
---------------
NLP analysis utilities:
  - Preprocessing: tokenization, lemmatization, stopword removal (NLTK)
  - Sentiment scoring (VADER)
  - Named-entity helper (spaCy, optional)
  - Emotion → stress signal mapping

Usage:
    from utils.nlp_analyzer import analyze_text
    result = analyze_text("I feel overwhelmed and exhausted")
    # → {emotion, sentiment_score, stress_signal, keywords}
"""

import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus          import stopwords
from nltk.tokenize        import word_tokenize
from nltk.stem            import WordNetLemmatizer

# Download required NLTK data (silent if already present)
for pkg in ["vader_lexicon", "punkt", "stopwords", "wordnet", "averaged_perceptron_tagger", "punkt_tab"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

_sia       = SentimentIntensityAnalyzer()
_lemma     = WordNetLemmatizer()
_STOPWORDS = set(stopwords.words("english"))

# ── Emotion → Stress Signal Mapping ─────────────────────────────────────────
# Maps a predicted emotion to a numeric stress modifier (-1=low, +1=high scale)
EMOTION_STRESS_MAP = {
    "anxious": {"stress_modifier": +20, "signal": "elevated_anxiety"},
    "sad":     {"stress_modifier": +15, "signal": "depressive_tendency"},
    "angry":   {"stress_modifier": +10, "signal": "frustration_burnout"},
    "neutral": {"stress_modifier":   0, "signal": "stable_baseline"},
}

# Crisis keywords that override normal flow
CRISIS_KEYWORDS = [
    r"\bsuicid\w*\b", r"\bkill\s+myself\b", r"\bend\s+my\s+life\b",
    r"\bself[\s\-]?harm\b", r"\bcut\s+myself\b", r"\bwant\s+to\s+die\b",
    r"\bnot\s+worth\s+living\b", r"\bgive\s+up\s+on\s+life\b",
]

# ── Core functions ─────────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """Lowercase, remove special chars, lemmatize, remove stopwords."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z\s']", " ", text)
    tokens = word_tokenize(text)
    tokens = [_lemma.lemmatize(t) for t in tokens if t not in _STOPWORDS and len(t) > 2]
    return " ".join(tokens)


def get_sentiment(text: str) -> float:
    """Returns VADER compound score in [-1, 1]. Negative = negative sentiment."""
    scores = _sia.polarity_scores(text)
    return round(scores["compound"], 4)


def extract_keywords(text: str, n: int = 8) -> list:
    """Return top N non-stopword tokens by frequency."""
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalpha() and t not in _STOPWORDS]
    freq   = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:n]


def is_crisis(text: str) -> bool:
    """Returns True if text contains self-harm / suicidal keywords."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in CRISIS_KEYWORDS)


def map_emotion_to_stress(emotion: str, sentiment_score: float) -> dict:
    """
    Combine emotion label with VADER sentiment to compute a stress signal.
    """
    mapping  = EMOTION_STRESS_MAP.get(emotion, EMOTION_STRESS_MAP["neutral"])
    modifier = mapping["stress_modifier"]

    # Boost modifier based on negativity depth
    if sentiment_score < -0.5:
        modifier = int(modifier * 1.4)
    elif sentiment_score < -0.2:
        modifier = int(modifier * 1.2)

    return {
        "stress_modifier": modifier,
        "signal":          mapping["signal"],
    }


def analyze_text(text: str, emotion: str = "neutral") -> dict:
    """
    Full NLP analysis pipeline.

    Args:
        text:    Raw user message
        emotion: Predicted emotion label from LSTM (or default "neutral")

    Returns:
        dict with keys: preprocessed, sentiment_score, emotion,
                        stress_signal, stress_modifier, keywords, crisis
    """
    preprocessed   = preprocess_text(text)
    sentiment_score = get_sentiment(text)
    keywords        = extract_keywords(text)
    crisis          = is_crisis(text)
    stress_info     = map_emotion_to_stress(emotion, sentiment_score)

    return {
        "preprocessed":    preprocessed,
        "sentiment_score": sentiment_score,
        "emotion":         emotion,
        "stress_signal":   stress_info["signal"],
        "stress_modifier": stress_info["stress_modifier"],
        "keywords":        keywords,
        "crisis":          crisis,
    }


if __name__ == "__main__":
    samples = [
        ("I'm terrified of failing my exams and I can't sleep.", "anxious"),
        ("Today was okay, just finished my assignment.", "neutral"),
        ("I feel so hopeless and empty inside.", "sad"),
        ("I want to end my suffering permanently.", "sad"),
    ]
    for text, emotion in samples:
        result = analyze_text(text, emotion)
        print(f"\nText: {text!r}")
        print(f"  Sentiment: {result['sentiment_score']}")
        print(f"  Emotion:   {result['emotion']}")
        print(f"  Signal:    {result['stress_signal']} (+{result['stress_modifier']})")
        print(f"  Crisis:    {result['crisis']}")
        print(f"  Keywords:  {result['keywords']}")
