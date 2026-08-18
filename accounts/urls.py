from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',                    views.register,                          name='register'),
    path('login/',                       views.user_login,                        name='login'),
    path('logout/',                      views.user_logout,                       name='logout'),
    path('profile/',                     views.profile,                           name='profile'),
    path('profile/edit/',                views.edit_profile,                      name='edit_profile'),
    path('profile/<str:username>/',      views.public_profile,                    name='public_profile'),
    path('preferences/',                 views.preferences,                       name='preferences'),
    path('theme/toggle/',                views.toggle_theme,                      name='toggle_theme'),

    # Password change
    path('password/change/',             views.GARLPasswordChangeView.as_view(),  name='password_change'),
    path('password/change/done/',        views.GARLPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Password reset
    path('password/reset/',              views.GARLPasswordResetView.as_view(),   name='password_reset'),
    path('password/reset/done/',         views.GARLPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.GARLPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/',     views.GARLPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
