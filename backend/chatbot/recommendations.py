"""
recommendations.py
------------------
Personalization engine that generates coping strategy recommendations
based on stress level, emotion trends, and user history.
"""

from typing import List, Dict

RECOMMENDATIONS = {
    "High": {
        "anxious": [
            {"title": "Box Breathing",           "desc": "Inhale 4s → Hold 4s → Exhale 4s → Hold 4s. Repeat 5×.",        "category": "Breathing"},
            {"title": "5-4-3-2-1 Grounding",    "desc": "Name 5 things you see, 4 hear, 3 touch, 2 smell, 1 taste.",    "category": "Mindfulness"},
            {"title": "Micro-Break Every Hour",  "desc": "Set a 5-min timer. Stand, stretch, look at something 20m away.", "category": "Study"},
            {"title": "Avoid Caffeine After 2pm","desc": "Replace with chamomile tea to reduce evening anxiety.",          "category": "Lifestyle"},
            {"title": "Worry Journal",           "desc": "Write worries for 10 min, then close the journal. Schedule a 'worry time'.", "category": "Mental"},
        ],
        "sad": [
            {"title": "Reach Out to One Person", "desc": "Text or call one friend or family member today — even just 'hi'.", "category": "Social"},
            {"title": "Sunlight in the Morning", "desc": "Spend 10–15 min outside within 1 hour of waking.",               "category": "Lifestyle"},
            {"title": "Gratitude List",          "desc": "Write 3 things you are grateful for, no matter how small.",       "category": "Mental"},
            {"title": "Gentle Movement",         "desc": "A 20-min walk listening to your favourite music.",               "category": "Physical"},
            {"title": "Limit Doom-Scrolling",    "desc": "Set a 30-min social media limit using your phone's screen time settings.", "category": "Lifestyle"},
        ],
        "angry": [
            {"title": "Cold Water on Wrists",    "desc": "Cold water on pulse points can quickly lower physiological arousal.", "category": "Physical"},
            {"title": "Physical Release",        "desc": "Do 10 jumping jacks or punch a pillow to safely release tension.", "category": "Physical"},
            {"title": "STOP Technique",          "desc": "Stop → Take a breath → Observe feelings → Proceed mindfully.",    "category": "Mental"},
            {"title": "Vent in a Private Note",  "desc": "Write everything you feel — then decide if you want to send it.", "category": "Mental"},
        ],
        "neutral": [
            {"title": "Preventive Self-Care",    "desc": "High burnout score detected. Schedule one enjoyable activity today.", "category": "Lifestyle"},
            {"title": "Sleep Hygiene Review",    "desc": "Aim for 7–9 hours. Set a consistent bedtime alarm.",               "category": "Sleep"},
        ],
    },
    "Moderate": {
        "anxious": [
            {"title": "Pomodoro Technique",      "desc": "25 min focused study + 5 min break × 4, then a 30-min break.",  "category": "Study"},
            {"title": "Task Priority Matrix",    "desc": "Label tasks: Urgent+Important, Important, Urgent, Neither.",      "category": "Study"},
            {"title": "Limit News Consumption",  "desc": "Check news once a day at a fixed time.",                          "category": "Lifestyle"},
        ],
        "sad": [
            {"title": "Plan One Fun Activity",   "desc": "Schedule something you enjoy this week — treat it like a class.", "category": "Social"},
            {"title": "Mood Tracking",           "desc": "Rate your mood 1–10 at the same time each day in a notes app.",  "category": "Mental"},
        ],
        "angry": [
            {"title": "Take a 10-Minute Walk",   "desc": "Physical movement resets stress hormones within minutes.",        "category": "Physical"},
            {"title": "Communicate Assertively", "desc": "Use 'I feel ... when ...' statements instead of blame.",          "category": "Social"},
        ],
        "neutral": [
            {"title": "Exercise 3× This Week",   "desc": "Even a 30-min walk counts. Consistency matters more than intensity.", "category": "Physical"},
            {"title": "Weekly Review",           "desc": "Every Sunday: 15 min to review what worked and plan the next week.", "category": "Study"},
        ],
    },
    "Low": {
        "neutral": [
            {"title": "Maintain Your Routine",   "desc": "Your stress is low — great! Keep consistent sleep and study hours.", "category": "Lifestyle"},
            {"title": "Help a Classmate",        "desc": "Teaching others reinforces your own learning and boosts mood.",    "category": "Social"},
        ],
        "anxious": [
            {"title": "Mild Anxiety is Normal",  "desc": "Some anxiety improves performance. Practice deep breaths before exams.", "category": "Mental"},
        ],
        "sad": [
            {"title": "Connect Socially",        "desc": "Join a study group or club to fight mild isolation.",               "category": "Social"},
        ],
        "angry": [
            {"title": "Reflect on the Trigger",  "desc": "Journal about what made you angry and what you can control.",     "category": "Mental"},
        ],
    },
}

DEFAULT_RECS = [
    {"title": "Stay Hydrated",        "desc": "Drink 8 glasses of water a day — dehydration worsens brain fog.", "category": "Lifestyle"},
    {"title": "Digital Detox Hour",   "desc": "One hour before bed: no screens. Read or journal instead.",       "category": "Sleep"},
]


def get_recommendations(
    stress_level: str = "Moderate",
    emotion:      str = "neutral",
    history_emotions: List[str] = None,
    max_recs:     int = 5,
) -> List[Dict]:
    """
    Returns up to `max_recs` personalized recommendations.

    Args:
        stress_level:     "High" | "Moderate" | "Low"
        emotion:          Current detected emotion
        history_emotions: List of past emotions (for trending)
        max_recs:         Max number of recommendations to return
    """
    level_map = RECOMMENDATIONS.get(stress_level, RECOMMENDATIONS["Moderate"])
    recs      = list(level_map.get(emotion, level_map.get("neutral", [])))

    # Add trending recs if a different emotion has dominated history
    if history_emotions:
        dominant = max(set(history_emotions), key=history_emotions.count)
        if dominant != emotion and dominant in level_map:
            trending = level_map[dominant][:2]
            recs = recs + [r for r in trending if r not in recs]

    # Pad with defaults if needed
    recs = recs + [r for r in DEFAULT_RECS if r not in recs]

    return recs[:max_recs]


if __name__ == "__main__":
    recs = get_recommendations("High", "anxious", history_emotions=["sad", "anxious", "angry", "anxious"])
    for i, r in enumerate(recs, 1):
        print(f"{i}. [{r['category']}] {r['title']}: {r['desc']}")
