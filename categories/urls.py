from django.urls import path

from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='list'),
    path('create/', views.CategoryCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='delete'),
]
