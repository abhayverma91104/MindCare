"""
api/views.py
------------
Three REST endpoints:
  POST /api/predict   → stress level + burnout score
  POST /api/chat      → Gemini-powered chatbot response
  GET  /api/recommend → personalized recommendations
  GET  /api/history/<user_id> → chat history
"""

import os, sys, json
from django.conf        import settings
from rest_framework.decorators import api_view
from rest_framework.response   import Response
from rest_framework            import status

# ── Path Setup ───────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# NOTE: ML imports are deferred to function bodies so Django starts
# without requiring TensorFlow/Keras at server startup time.
from backend.chatbot.recommendations import get_recommendations
from .models       import UserSession, Prediction, ChatMessage
from .serializers  import ChatMessageSerializer, PredictionSerializer

# In-memory session store for rolling chat history (use Redis in production)
_SESSION_HISTORY: dict = {}


def _get_or_create_session(user_id: str) -> UserSession:
    session, _ = UserSession.objects.get_or_create(user_id=user_id)
    return session


# ── /api/predict ─────────────────────────────────────────────────────────────

@api_view(["POST"])
def predict_view(request):
    """
    POST /api/predict
    Body (JSON):
      {
        "user_id":         "optional-string",
        "dass_stress":     18, "dass_anxiety": 14, "dass_depression": 10,
        "pss_score":       22, "sleep_hours":   5, "study_hours":      9,
        "social_hours":     2, "exercise_freq":  1, "caffeine_cups":    3,
        "screen_hours":     6
      }
    Returns:
      { stress_level, burnout_score, probabilities }
    """
    data    = request.data
    user_id = data.get("user_id")

    try:
        from models.predict import predict_stress
        result = predict_stress(data)
    except FileNotFoundError as e:
        return Response(
            {"error": "ML models not trained yet. Run `python models/train_classical.py` first.",
             "detail": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Persist prediction
    if user_id:
        session = _get_or_create_session(user_id)
        Prediction.objects.create(
            session       = session,
            stress_level  = result["stress_level"],
            burnout_score = result["burnout_score"],
            probabilities = result["probabilities"],
            raw_features  = {k: v for k, v in data.items() if k != "user_id"},
        )

    return Response(result, status=status.HTTP_200_OK)


# ── /api/chat ─────────────────────────────────────────────────────────────────

@api_view(["POST"])
def chat_view(request):
    """
    POST /api/chat
    Body (JSON):
      {
        "user_id":     "string (required)",
        "message":     "user message text",
        "personality": "calm|coach|listener (optional)",
        "language":    "English|Hindi|Spanish|... (optional)"
      }
    Returns:
      { response, crisis, emotion, stress_level, burnout_score, personality }
    """
    data        = request.data
    user_id     = data.get("user_id", "anonymous")
    message     = data.get("message", "").strip()
    personality = data.get("personality", "calm")
    language    = data.get("language", "English")

    if not message:
        return Response({"error": "message field is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Get or init session + history
    session = _get_or_create_session(user_id)
    session.personality = personality
    session.language_hint = language
    session.save()

    if user_id not in _SESSION_HISTORY:
        # Restore last 20 DB messages into memory on first request
        db_msgs = ChatMessage.objects.filter(session=session).order_by("-created_at")[:20]
        _SESSION_HISTORY[user_id] = [
            {"role": m.role, "content": m.content}
            for m in reversed(list(db_msgs))
        ]

    history = _SESSION_HISTORY[user_id]

    # Run emotion detection
    try:
        from models.predict import predict_emotion
        emotion_result = predict_emotion(message)
    except Exception:
        emotion_result = {"emotion": "neutral", "confidence": 0.5, "all_scores": {}}

    # Run stress prediction using latest DB prediction (if available)
    last_pred = Prediction.objects.filter(session=session).order_by("-created_at").first()
    stress_result = (
        {"stress_level": last_pred.stress_level, "burnout_score": last_pred.burnout_score}
        if last_pred else None
    )

    # Gemini pipeline
    try:
        from backend.chatbot.gemini_pipeline import chat as gemini_chat
        result = gemini_chat(
            user_message   = message,
            history        = history,
            stress_result  = stress_result,
            emotion_result = emotion_result,
            personality    = personality,
            language_hint  = language,
        )
    except EnvironmentError as e:
        return Response(
            {"error": "GEMINI_API_KEY not configured", "detail": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Persist messages
    ChatMessage.objects.create(
        session      = session,
        role         = "user",
        content      = message,
        emotion      = result.get("emotion", ""),
        stress_level = result.get("stress_level", ""),
        burnout_score= result.get("burnout_score"),
        crisis_flag  = False,
    )
    ChatMessage.objects.create(
        session      = session,
        role         = "assistant",
        content      = result["response"],
        emotion      = result.get("emotion", ""),
        stress_level = result.get("stress_level", ""),
        burnout_score= result.get("burnout_score"),
        crisis_flag  = result.get("crisis", False),
    )

    # Persist the dynamically updated stress/burnout as a formal Prediction
    # This ensures that the Dashboard graphs and trend trackers update reliably.
    Prediction.objects.create(
        session       = session,
        stress_level  = result.get("stress_level", "Moderate"),
        burnout_score = result.get("burnout_score", 50.0),
        probabilities = {},
        raw_features  = {"source": "chat_inference"},
    )

    return Response(result, status=status.HTTP_200_OK)


# ── /api/recommend ────────────────────────────────────────────────────────────

@api_view(["GET"])
def recommend_view(request):
    """
    GET /api/recommend?user_id=xxx
    Returns personalized recommendations based on stored prediction history.
    """
    user_id = request.query_params.get("user_id", "")

    # Default context
    stress_level = "Moderate"
    emotion      = "neutral"
    history_emotions = []

    if user_id:
        try:
            session  = UserSession.objects.get(user_id=user_id)
            last_pred = Prediction.objects.filter(session=session).order_by("-created_at").first()
            if last_pred:
                stress_level = last_pred.stress_level

            # Emotion history from last 20 messages
            msgs = ChatMessage.objects.filter(
                session=session, role="user"
            ).order_by("-created_at")[:20]
            history_emotions = [m.emotion for m in msgs if m.emotion]
            if history_emotions:
                emotion = history_emotions[0]

        except UserSession.DoesNotExist:
            pass

    recs = get_recommendations(
        stress_level     = stress_level,
        emotion          = emotion,
        history_emotions = history_emotions,
        max_recs         = 6,
    )

    return Response({
        "stress_level":      stress_level,
        "emotion":           emotion,
        "recommendations":   recs,
    }, status=status.HTTP_200_OK)


# ── /api/history/<user_id> ────────────────────────────────────────────────────

@api_view(["GET"])
def history_view(request, user_id):
    """
    GET /api/history/<user_id>
    Returns last 50 messages + last 10 predictions for the user.
    """
    try:
        session = UserSession.objects.get(user_id=user_id)
    except UserSession.DoesNotExist:
        return Response({"messages": [], "predictions": []}, status=status.HTTP_200_OK)

    messages    = ChatMessage.objects.filter(session=session).order_by("-created_at")[:50]
    predictions = Prediction.objects.filter(session=session).order_by("-created_at")[:10]

    return Response({
        "messages":    ChatMessageSerializer(reversed(list(messages)), many=True).data,
        "predictions": PredictionSerializer(predictions, many=True).data,
    }, status=status.HTTP_200_OK)


# ── /api/health ───────────────────────────────────────────────────────────────

@api_view(["GET"])
def health_view(request):
    return Response({"status": "ok", "service": "MindCare API"})
