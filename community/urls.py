from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('',                              views.directory_home,      name='home'),
    path('institutions/',                 views.institution_list,    name='institution_list'),
    path('institutions/<slug:slug>/',     views.institution_detail,  name='institution_detail'),
    path('researchers/',                  views.researcher_list,     name='researcher_list'),
]
