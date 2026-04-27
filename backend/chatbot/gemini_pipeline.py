"""
gemini_pipeline.py
------------------
Full Gemini chatbot pipeline:

  User Input
      ↓ (emotion detection via LSTM)
  Emotion Detection
      ↓ (classify stress via ML)
  Stress/Burnout Prediction
      ↓ (assemble context-rich system prompt)
  Context Builder
      ↓ (call Gemini API with rolling memory)
  Gemini API Call
      ↓ (check for crisis / medical advice)
  Safety Filter
      ↓
  Final Response

Key features:
  - System prompt engineering (role, restrictions, coping strategies)
  - Rolling memory (last 20 messages)
  - Safety override for self-harm keywords
  - Personality modes: coach | calm | listener
  - Multilingual support via Gemini's native capabilities
"""

import os, re, sys
from datetime import datetime
from typing   import Optional

import google.generativeai as genai  # type: ignore

# Add project root to path for model imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from utils.nlp_analyzer import is_crisis, analyze_text

# ── Configuration ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # fast & cost-efficient

MEMORY_LIMIT   = 20          # max messages kept per session
CRISIS_HOTLINE = "iCall (India): 9152987821  |  Vandrevala Foundation: 1860-2662-345  |  International: befrienders.org"

PERSONALITY_MODES = {
    "coach": (
        "You are a proactive, solution-focused mental wellness coach. "
        "Motivate the student, celebrate small wins, and offer concrete action steps."
    ),
    "calm": (
        "You are a gentle, grounding therapist who specializes in mindfulness and breathing. "
        "Use a calm, slow tone with reassuring language."
    ),
    "listener": (
        "You are an empathetic, non-judgmental listener. "
        "Validate feelings before offering any suggestions. Ask open-ended questions."
    ),
}

CRISIS_RESPONSE = (
    "I'm really concerned about what you just shared. You are not alone, and your life has value. "
    "Please reach out to a crisis helpline immediately:\n\n"
    f"📞 **{CRISIS_HOTLINE}**\n\n"
    "If you are in immediate danger, please call emergency services (112 in India / 911 in the US). "
    "I'm here with you. Would you like me to help you find local support resources?"
)


# ── Gemini client (lazy init) ─────────────────────────────────────────────────
_gemini_model = None

def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        if not GEMINI_API_KEY:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                "Add it to your .env file."
            )
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    return _gemini_model


# ── System Prompt Builder ─────────────────────────────────────────────────────

def build_system_prompt(
    stress_level:    str,
    burnout_score:   float,
    emotion:         str,
    sentiment_score: float,
    personality:     str = "calm",
    language_hint:   str = "English",
) -> str:
    """
    Constructs a rich system prompt that:
      - Sets role and restrictions
      - Injects current stress/emotion context
      - Forces coping-strategy focus
      - Prevents medical advice
    """
    personality_desc = PERSONALITY_MODES.get(personality, PERSONALITY_MODES["calm"])

    urgency_note = ""
    if stress_level == "High" or burnout_score > 70:
        urgency_note = (
            "\n⚠️  The student is currently experiencing HIGH STRESS or HIGH BURNOUT. "
            "Prioritize grounding techniques, breathing exercises, and immediate relief strategies."
        )
    elif stress_level == "Moderate":
        urgency_note = (
            "\nThe student is experiencing MODERATE STRESS. "
            "Balance validation with practical strategies."
        )

    return f"""You are MindCare, an AI-powered mental wellness companion for university students.
{personality_desc}

CURRENT STUDENT CONTEXT (updated every message):
  • Stress Level  : {stress_level}
  • Burnout Score : {burnout_score:.1f} / 100
  • Detected Emotion : {emotion}
  • Sentiment Score  : {sentiment_score:.2f} (range -1 to +1, lower = more negative)
  • Response Language: {language_hint}
{urgency_note}

STRICT RULES YOU MUST FOLLOW:
1. NEVER provide medical diagnoses or prescribe medication.
2. NEVER replace professional therapy — always encourage seeking professional help when appropriate.
3. ALWAYS offer at least one concrete, actionable coping strategy per response.
4. If the user mentions self-harm or suicidal thoughts, respond with compassion and immediately provide crisis resources.
5. Keep responses concise (3–5 sentences + bullet points), warm, and non-clinical.
6. Respond in {language_hint}. If the user writes in a different language, match their language automatically.
7. Do NOT repeat the same coping strategy twice in a session.

EFFECTIVE COPING STRATEGIES TO DRAW FROM:
  - Box breathing (4-4-4-4), progressive muscle relaxation, 5-4-3-2-1 grounding
  - Pomodoro study technique, task chunking, priority matrix
  - Social connection prompts, journaling, gratitude practice
  - Sleep hygiene tips, caffeine reduction, phone-free wind-down routine
  - Physical activity: walks, stretches, yoga for students
  - Cognitive reframing: "I am doing my best" affirmations

Remember: You are a supportive companion, not a medical professional."""


# ── Context Builder ───────────────────────────────────────────────────────────

def build_context_summary(history: list) -> str:
    """
    Summarize recurring themes from chat history for richer personalization.
    """
    if not history:
        return "No prior conversation context."

    recent = history[-10:]                          # last 10 messages
    user_msgs = [m["content"] for m in recent if m["role"] == "user"]
    keywords_all = []
    for msg in user_msgs:
        analysis = analyze_text(msg)
        keywords_all.extend(analysis.get("keywords", []))

    freq = {}
    for k in keywords_all:
        freq[k] = freq.get(k, 0) + 1
    top_keywords = sorted(freq, key=freq.get, reverse=True)[:6]

    return (
        f"Recurring themes in this session: {', '.join(top_keywords) or 'none detected'}. "
        f"Session length: {len(history)} messages."
    )


# ── Safety Filter ─────────────────────────────────────────────────────────────
MEDICAL_ADVICE_PATTERNS = [
    r"\bprescri\w+\b", r"\btake\s+\w+\s+mg\b", r"\bdiagnos\w+\b",
    r"\bmedication\s+for\b", r"\bpsychiatric\s+disorder\b",
]

def safety_filter(response_text: str, user_text: str) -> tuple[str, bool]:
    """
    Returns (final_response, was_overridden).
    - Overrides with crisis response if user text contains crisis keywords.
    - Removes medical advice if Gemini accidentally slipped one in.
    """
    # Crisis override (check user input, not model output)
    if is_crisis(user_text):
        return CRISIS_RESPONSE, True

    # Strip medical advice patterns from model output
    filtered = response_text
    for pattern in MEDICAL_ADVICE_PATTERNS:
        if re.search(pattern, filtered, re.IGNORECASE):
            filtered = re.sub(
                r"[^.!?]*" + pattern + r"[^.!?]*[.!?]",
                "",
                filtered,
                flags=re.IGNORECASE,
            ).strip()

    return filtered or response_text, False


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def chat(
    user_message:  str,
    history:       list,                # list of {"role": ..., "content": ...}
    stress_result: Optional[dict] = None,
    emotion_result: Optional[dict] = None,
    personality:   str = "calm",
    language_hint: str = "English",
) -> dict:
    """
    Full pipeline entry point.

    Args:
        user_message:  The raw user text
        history:       Rolling list of past messages (mutated in-place)
        stress_result: Output of predict_stress() or None
        emotion_result: Output of predict_emotion() or None
        personality:   "coach" | "calm" | "listener"
        language_hint: Language to respond in

    Returns:
        dict with keys: response, crisis, emotion, stress_level,
                        burnout_score, personality
    """
    # Defaults if models haven't been run
    stress_level   = (stress_result  or {}).get("stress_level",  "Moderate")
    burnout_score  = (stress_result  or {}).get("burnout_score",  50.0)
    emotion        = (emotion_result or {}).get("emotion",        "neutral")
    confidence     = (emotion_result or {}).get("confidence",     0.5)

    # Dynamic stress and burnout adjustment based on chat emotion
    if emotion == "fear":
        stress_level = "High"
        burnout_score = min(100.0, burnout_score + 3.0)
    elif emotion == "sadness" or emotion == "anger":
        stress_level = "High" if burnout_score > 65 else "Moderate"
        burnout_score = min(100.0, burnout_score + 2.0)
    elif emotion == "joy" or emotion == "love":
        stress_level = "Low"
        burnout_score = max(0.0, burnout_score - 4.0)
    else: # surprise or neutral
        stress_level = "Low" if burnout_score < 40 else "Moderate"
        burnout_score = max(0.0, burnout_score - 1.0)

    # NLP analysis
    nlp = analyze_text(user_message, emotion)
    sentiment_score = nlp["sentiment_score"]

    # Crisis check (short-circuit before API call)
    if nlp["crisis"]:
        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant", "content": CRISIS_RESPONSE})
        history[:] = history[-MEMORY_LIMIT:]
        return {
            "response":     CRISIS_RESPONSE,
            "crisis":       True,
            "emotion":      emotion,
            "stress_level": stress_level,
            "burnout_score":burnout_score,
            "personality":  personality,
        }

    # System prompt
    system_prompt = build_system_prompt(
        stress_level, burnout_score, emotion, sentiment_score,
        personality, language_hint,
    )

    context_summary = build_context_summary(history)

    # Build Gemini conversation history
    gemini_history = []
    for msg in history[-MEMORY_LIMIT:]:
        role    = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Full prompt = system + context + latest user message
    full_user_msg = (
        f"[Session Context: {context_summary}]\n\n"
        f"{user_message}"
    )

    try:
        model = _get_gemini_model()
        chat_session = model.start_chat(
            history=[
                {"role": "user",  "parts": [system_prompt]},
                {"role": "model", "parts": ["Understood. I'm ready to support the student."]},
                *gemini_history,
            ]
        )
        gemini_response = chat_session.send_message(full_user_msg)
        raw_response    = gemini_response.text.strip()

    except Exception as e:
        raw_response = (
            "I'm having a moment of connection trouble. "
            "But I'm still here for you — could you share what's on your mind? "
            f"(Technical note: {str(e)[:120]})"
        )

    # Safety filter on output
    final_response, was_overridden = safety_filter(raw_response, user_message)

    # Update rolling memory
    history.append({"role": "user",      "content": user_message})
    history.append({"role": "assistant", "content": final_response})
    history[:] = history[-MEMORY_LIMIT:]

    return {
        "response":      final_response,
        "crisis":        was_overridden,
        "emotion":       emotion,
        "confidence":    confidence,
        "stress_level":  stress_level,
        "burnout_score": burnout_score,
        "personality":   personality,
        "sentiment":     sentiment_score,
    }


if __name__ == "__main__":
    # Quick CLI test (requires trained models & GEMINI_API_KEY)
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))

    hist = []
    msgs = [
        "I've been feeling really burned out lately, I can't focus at all.",
        "Yeah, I sleep only 4 hours and study for 12 hours every day.",
        "I just feel like giving up.",
    ]
    for msg in msgs:
        print(f"\nUser: {msg}")
        result = chat(msg, hist, stress_result={"stress_level": "High", "burnout_score": 78})
        print(f"MindCare [{result['emotion']}]: {result['response'][:300]}...")
