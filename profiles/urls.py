from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_detail, name='detail'),  # View profile
    path('edit/', views.ProfileUpdateView.as_view(), name='edit'),  # Edit profile
]
