from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('', views.order_list_view, name='list'),
    path('<str:order_number>/', views.order_detail_view, name='detail'),
]
