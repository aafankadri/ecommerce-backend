from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from .models import OrderItem, User, Product, Cart, CartItem, Order
from .serializers import OrderSerializer, RegisterSerializer, ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']  # Enables ?search=keyboard
    ordering_fields = ['price', 'name']      # Enables ?ordering=price

class CartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += int(quantity)
        else:
            item.quantity = int(quantity)
        item.save()
        return Response({'message': 'Product added to cart'})
    
class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.quantity = request.data.get('quantity', item.quantity)
            item.save()
            return Response({'message': 'Cart item updated'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
        
class RemoveCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
        
class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        total_price = sum([item.product.price * item.quantity for item in cart.items.all()])
        order = Order.objects.create(user=user, total_price=total_price, status='CONFIRMED')

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()  # Clear cart

        return Response({'message': 'Order placed successfully', 'order_id': order.id})
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')