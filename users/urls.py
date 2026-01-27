from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Change email and password URLs
    path('change_email/', views.change_email, name='change_email'),
    path('change_password/', views.CustomPasswordChangeView.as_view(), name='change_password'),

    # Landing page
    path('', views.landing_page, name='landing_page'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
