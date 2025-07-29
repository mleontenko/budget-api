from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/types/', views.category_types, name='category-types'),
] 