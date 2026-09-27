from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ── Authentication ────────────────────────────────────
    path('register/',  views.register_view,  name='register'),
    path('login/',     views.login_view,     name='login'),
    path('logout/',    views.logout_view,    name='logout'),

    # ── Profile ───────────────────────────────────────────
    path('profile/',   views.profile_view,   name='profile'),

    # ── Address management ────────────────────────────────
    path('addresses/',                    views.address_list_view,        name='address_list'),
    path('addresses/add/',                views.address_add_view,         name='address_add'),
    path('addresses/<int:pk>/edit/',      views.address_edit_view,        name='address_edit'),
    path('addresses/<int:pk>/delete/',    views.address_delete_view,      name='address_delete'),
    path('addresses/<int:pk>/primary/',   views.address_set_primary_view, name='address_primary'),

    # ── Password change (requires login) ──────────────────
    path('password/change/', views.password_change_view, name='password_change'),

    # ── Password reset (email flow — 4 steps) ─────────────
    path('password/reset/',
         views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password/reset/done/',
         views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password/reset/complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]

