from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Dashboard view
    # Transaction URLs will be added later
]