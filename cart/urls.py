from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='view'),
    path('add/<slug:slug>/', views.cart_add_view, name='add'),
    path('update/<int:item_id>/', views.cart_update_view, name='update'),
    path('remove/<int:item_id>/', views.cart_remove_view, name='remove'),
]
