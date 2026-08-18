from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                          views.home,                  name='home'),
    path('user/',                     views.user_dashboard,        name='user_dashboard'),
    path('researcher/',               views.researcher_dashboard,  name='researcher_dashboard'),
    path('author/',                   views.author_dashboard,      name='author_dashboard'),
    path('instructor/',               views.instructor_dashboard,  name='instructor_dashboard'),
    path('reviewer/',                 views.reviewer_dashboard,    name='reviewer_dashboard'),
    path('editor/',                   views.editor_dashboard,      name='editor_dashboard'),
    path('institution/',              views.institution_dashboard, name='institution_dashboard'),
    path('library/',                  views.library_dashboard,     name='library_dashboard'),
    path('admin/',                    views.admin_dashboard,       name='admin_dashboard'),
    path('admin/users/',              views.manage_users,          name='manage_users'),
    path('admin/users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user_active'),
    path('admin/users/<int:pk>/role/',   views.change_user_role,   name='change_user_role'),
]
