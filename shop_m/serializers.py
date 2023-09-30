from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' 

class ProductSerializer(serializers.ModelSerializer):
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_related_products(self, obj):
        
        related_products = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
        serializer = ProductSerializer(related_products, many=True)
        return serializer.data

class AddToFavoritesSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class RemoveFromFavoritesSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    