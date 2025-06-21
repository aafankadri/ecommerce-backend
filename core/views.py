from rest_framework import generics, filters
from .models import User, Product
from .serializers import RegisterSerializer, ProductSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']  # Enables ?search=keyboard
    ordering_fields = ['price', 'name']      # Enables ?ordering=price