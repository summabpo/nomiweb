from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_api, name="mar_ia_chat_api"),
]