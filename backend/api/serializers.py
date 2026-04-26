"""
api/serializers.py
"""

from rest_framework import serializers
from .models import UserSession, Prediction, ChatMessage


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Prediction
        fields = ["id", "stress_level", "burnout_score", "probabilities", "created_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ["id", "role", "content", "emotion", "stress_level",
                  "burnout_score", "crisis_flag", "created_at"]


class UserSessionSerializer(serializers.ModelSerializer):
    predictions = PredictionSerializer(many=True, read_only=True)
    messages    = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model  = UserSession
        fields = ["user_id", "language_hint", "personality", "created_at",
                  "updated_at", "predictions", "messages"]
