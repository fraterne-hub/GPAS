from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',                    views.home,                  name='home'),
    path('bookmark/toggle/',    views.toggle_bookmark,       name='toggle_bookmark'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
