from django.urls import path
from . import views

urlpatterns = [
    path("predict",              views.predict_view,              name="predict"),
    path("chat",                 views.chat_view,                 name="chat"),
    path("recommend",            views.recommend_view,            name="recommend"),
    path("history/<str:user_id>",views.history_view,              name="history"),
    path("health",               views.health_view,               name="health"),
]
