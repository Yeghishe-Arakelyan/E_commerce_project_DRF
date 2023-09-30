from rest_framework import generics, filters, status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, AddToFavoritesSerializer,RemoveFromFavoritesSerializer
from .permissions import IsManagerOrReadOnly, IsOwner
from rest_framework.permissions import IsAuthenticated
from .filter import ProductFilter, CategoryFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]
    filterset_class = CategoryFilter 

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = '__all__'
    search_fields = ['title','sku']

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManagerOrReadOnly]

class ProductByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = Category.objects.filter(slug=slug).first()
        queryset = Product.objects.filter(category=category)
        
        if not category.is_sub:
            sub_categories = category.sub_categories.all()
            queryset |= Product.objects.filter(category__in=sub_categories)
        
        return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request):
    serializer = AddToFavoritesSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        try:
            product = Product.objects.get(id=product_id)
            request.user.likes.add(product)
            return Response({'message': 'Product added to favorites'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsOwner])
def remove_from_favorites(request):
    serializer = RemoveFromFavoritesSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        try:
            product = Product.objects.get(id=product_id)
            request.user.likes.remove(product)
            return Response({'message': 'Product removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsOwner])
def show_favorites(request):
    
    favorite_products = request.user.liked_products.all()  
    serializer = ProductSerializer(favorite_products, many=True)  
    
    return Response(serializer.data)