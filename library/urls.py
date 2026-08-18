from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('',                          views.library_home,       name='home'),
    path('resources/',                views.resource_list,      name='resource_list'),
    path('resources/<int:pk>/',       views.resource_detail,    name='resource_detail'),
    path('resources/<int:pk>/download/', views.resource_download, name='download'),
]
