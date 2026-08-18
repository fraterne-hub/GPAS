from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('',                                           views.learning_home,     name='home'),
    path('courses/',                                   views.course_list,       name='course_list'),
    path('courses/<slug:slug>/',                       views.course_detail,     name='course_detail'),
    path('courses/<slug:slug>/enroll/',                views.enroll,            name='enroll'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_order>/', views.lesson_view, name='lesson'),
    path('my-courses/',                                views.my_courses,        name='my_courses'),
    path('certificates/',                              views.my_certificates,   name='certificates'),
]
