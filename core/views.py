import razorpay
from django.conf import settings
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from .models import OrderItem, User, Product, Cart, CartItem, Order
from .serializers import AdminOrderUpdateSerializer, OrderSerializer, RegisterSerializer, ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from razorpay.errors import SignatureVerificationError
from .tasks import send_order_confirmation_email
from .permissions import IsAdminUser

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
    
class RazorpayOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        total_price = sum([item.product.price * item.quantity for item in cart.items.all()])
        total_amount_paise = int(total_price * 100)  # Razorpay expects amount in paise

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            "amount": total_amount_paise,
            "currency": "INR",
            "payment_capture": "1"
        })

        return Response({
            "razorpay_order_id": payment['id'],
            "amount": total_amount_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID
        })
    
class RazorpayVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        order_id = data.get("order_id")
        payment_id = data.get("payment_id")
        signature = data.get("signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
        except SignatureVerificationError:
            return Response({'error': 'Payment verification failed'}, status=400)

        # Proceed with placing the order
        cart = Cart.objects.get(user=user)
        total_price = sum([item.product.price * item.quantity for item in cart.items.all()])
        order = Order.objects.create(user=user, total_price=total_price, status='CONFIRMED', payment_id=payment_id)
        send_order_confirmation_email.delay(order.id)

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()

        return Response({'message': 'Payment successful and order placed', 'order_id': order.id})
    

class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        queryset = Order.objects.all().order_by('-created_at')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset
    
class AdminOrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'pk'