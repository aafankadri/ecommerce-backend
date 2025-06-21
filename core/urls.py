from django.urls import path
from .views import RegisterView, ProductListView, CartDetailView, AddToCartView, UpdateCartItemView, RemoveCartItemView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/update/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='cart-remove'),
]