from django.urls import path
from . import views

urlpatterns = [
    
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),
    path('products/category/<slug>/', views.ProductByCategoryView.as_view(), name='product-list-by-category'),
    path('add_to_favorites/', views.add_to_favorites, name='add-to-favorites'),
    path('remove_from_favorites/', views.remove_from_favorites, name='remove-from-favorites'),
    path('show_favorites/', views.show_favorites, name='show-favorites' ),
]
