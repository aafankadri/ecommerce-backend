from django.urls import path
from .views import RegisterView, ProductListView, CartDetailView, AddToCartView, UpdateCartItemView, RemoveCartItemView, OrderCreateView, OrderListView, RazorpayOrderCreateView, RazorpayVerifyView, AdminOrderListView, AdminOrderStatusUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/update/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='cart-remove'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('razorpay/create-order/', RazorpayOrderCreateView.as_view(), name='razorpay-create'),
    path('razorpay/verify-payment/', RazorpayVerifyView.as_view(), name='razorpay-verify'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/update/', AdminOrderStatusUpdateView.as_view(), name='admin-order-update'),
]