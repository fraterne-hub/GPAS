from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('',                    views.research_home,   name='home'),
    path('papers/',             views.paper_list,      name='paper_list'),
    path('papers/<slug:slug>/', views.paper_detail,    name='paper_detail'),
    path('papers/<int:pk>/download/', views.paper_download, name='paper_download'),
    path('papers/submit/',      views.submit_paper,    name='submit_paper'),
    path('projects/',           views.project_list,    name='project_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
]
