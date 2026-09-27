from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<slug:slug>/', views.wishlist_add_view, name='wishlist_add'),
    path('wishlist/remove/<slug:slug>/', views.wishlist_remove_view, name='wishlist_remove'),
]

