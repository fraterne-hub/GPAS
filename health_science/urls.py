from django.urls import path
from . import views

app_name = 'health_science'

urlpatterns = [
    path('',                              views.health_home,        name='home'),
    path('resources/',                    views.resource_list,      name='resource_list'),
    path('resources/<slug:slug>/',        views.resource_detail,    name='resource_detail'),
    path('resources/<int:pk>/download/',  views.resource_download,  name='download'),
    path('<str:discipline>/',             views.discipline_view,    name='discipline'),
]
