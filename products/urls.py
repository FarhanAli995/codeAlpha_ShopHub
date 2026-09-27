from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list_view, name='list'),
    path('<slug:slug>/', views.product_detail_view, name='detail'),
]
