from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # ── Buyer flow ──────────────────────────────────────────────────────────
    path('checkout/<str:content_type>/<int:object_id>/',
         views.checkout, name='checkout'),
    path('pay/<str:content_type>/<int:object_id>/',
         views.process_payment, name='process_payment'),
    path('receipt/<str:transaction_id>/',
         views.receipt, name='receipt'),
    path('download/<str:content_type>/<int:object_id>/<str:transaction_id>/',
         views.download_content, name='download'),
    path('my-purchases/',
         views.my_purchases, name='my_purchases'),

    # ── Publisher ───────────────────────────────────────────────────────────
    path('publisher/dashboard/',
         views.publisher_dashboard, name='publisher_dashboard'),
    path('publisher/payout/request/',
         views.request_payout, name='request_payout'),

    # ── Admin / Platform owner ──────────────────────────────────────────────
    path('admin/revenue/',
         views.admin_revenue_dashboard, name='admin_revenue'),
    path('admin/payout/<int:pk>/approve/',
         views.approve_payout, name='approve_payout'),
    path('admin/payout/<int:pk>/reject/',
         views.reject_payout, name='reject_payout'),
    path('admin/set-price/<str:content_type>/<int:object_id>/',
         views.set_content_price, name='set_price'),
]
