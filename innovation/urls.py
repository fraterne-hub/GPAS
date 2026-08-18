from django.urls import path
from . import views

app_name = 'innovation'

urlpatterns = [
    path('',                        views.innovation_home,   name='home'),
    path('projects/',               views.project_list,      name='project_list'),
    path('projects/<slug:slug>/',   views.project_detail,    name='project_detail'),
    path('submit/',                 views.submit_project,    name='submit'),
    path('projects/<int:pk>/like/', views.toggle_like,       name='like'),
    path('moderate/',               views.moderate_projects, name='moderate'),
    path('moderate/<int:pk>/approve/', views.approve_project, name='approve'),
]
