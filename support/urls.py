from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('',                       views.support_home,    name='home'),
    path('faq/',                   views.faq_list,        name='faq'),
    path('tickets/new/',           views.create_ticket,   name='create_ticket'),
    path('tickets/',               views.my_tickets,      name='my_tickets'),
    path('tickets/<int:pk>/',      views.ticket_detail,   name='ticket_detail'),
]
