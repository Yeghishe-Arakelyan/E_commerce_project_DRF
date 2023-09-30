from django.urls import path
from . import views

urlpatterns = [
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),

    path('create_order/', views.create_order, name='create_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('user_orders/', views.user_orders, name='user_orders'),

    path('order_list/', views.OrderListView.as_view(), name='order_list'),
    path('order_detail/<int:pk>/', views.OrderRetrieveUpdateDestroyView.as_view(), name='order_detail'),
    path('orders/<int:pk>/mark_as_paid/', views.mark_order_as_paid, name='mark_order_as_paid'),
    path('orders/<int:pk>/mark_as_delivered/', views.mark_order_as_delivered, name='mark_order_as_delivered'),
]
