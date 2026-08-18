from django.urls import path
from . import views

app_name = 'ai_support'

urlpatterns = [
    path('',                              views.ai_chat_page,     name='chat'),
    path('send/',                         views.ai_chat_send,     name='send'),
    path('history/',                      views.ai_chat_history,  name='history'),
    path('clear/',                        views.ai_chat_clear,    name='clear'),
    path('feedback/<int:message_id>/',    views.ai_chat_feedback, name='feedback'),
]
