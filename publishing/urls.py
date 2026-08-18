from django.urls import path
from . import views

app_name = 'publishing'

urlpatterns = [
    path('',                          views.publishing_home,      name='home'),
    path('publications/',             views.publication_list,     name='publication_list'),
    path('publications/<slug:slug>/', views.publication_detail,   name='publication_detail'),
    path('submit/',                   views.submit_publication,   name='submit'),
    path('my-submissions/',           views.my_submissions,       name='my_submissions'),

    path('editor/',                   views.editor_dashboard,     name='editor_dashboard'),
    path('editor/approve/<int:pk>/',  views.approve_publication,  name='approve'),
    path('editor/reject/<int:pk>/',   views.reject_publication,   name='reject'),

    path('reviewer/',                 views.reviewer_dashboard,   name='reviewer_dashboard'),
    path('reviewer/review/<int:pk>/', views.submit_review,        name='submit_review'),

    path('books/',                    views.book_list,            name='book_list'),
    path('books/<slug:slug>/',        views.book_detail,          name='book_detail'),
    path('books/<int:pk>/download/',  views.book_download,        name='book_download'),

    path('journals/',                 views.journal_list,         name='journal_list'),
    path('journals/<slug:slug>/',     views.journal_detail,       name='journal_detail'),

    # ── Catch-all slug redirect ──────────────────────────────────────────────
    # Handles old bad notification links like /publishing/some-slug/
    # that were generated before the URL fix. Tries to find a matching
    # publication or book and redirects to the correct URL.
    path('<slug:slug>/',              views.slug_redirect,        name='slug_redirect'),
]
