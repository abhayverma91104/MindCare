"""
api/models.py — Django ORM models for MindCare
"""

import uuid
from django.db import models


class UserSession(models.Model):
    """Represents a user session identified by a UUID."""
    user_id       = models.CharField(max_length=64, unique=True, db_index=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    language_hint = models.CharField(max_length=32, default="English")
    personality   = models.CharField(max_length=16, default="calm")  # coach|calm|listener

    def __str__(self):
        return f"Session[{self.user_id}]"

    class Meta:
        ordering = ["-updated_at"]


class Prediction(models.Model):
    """Stores a stress + burnout prediction result."""
    STRESS_CHOICES = [("Low", "Low"), ("Moderate", "Moderate"), ("High", "High")]

    session      = models.ForeignKey(UserSession, on_delete=models.CASCADE,
                                     related_name="predictions", null=True, blank=True)
    stress_level = models.CharField(max_length=10, choices=STRESS_CHOICES)
    burnout_score = models.FloatField()
    raw_features  = models.JSONField(default=dict)
    probabilities = models.JSONField(default=dict)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ChatMessage(models.Model):
    """Stores a single chat message with snapshot of the detected context."""
    ROLE_CHOICES = [("user", "user"), ("assistant", "assistant")]

    session      = models.ForeignKey(UserSession, on_delete=models.CASCADE,
                                     related_name="messages")
    role         = models.CharField(max_length=12, choices=ROLE_CHOICES)
    content      = models.TextField()
    emotion      = models.CharField(max_length=16, blank=True, default="")
    stress_level = models.CharField(max_length=10, blank=True, default="")
    burnout_score = models.FloatField(null=True, blank=True)
    crisis_flag  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
