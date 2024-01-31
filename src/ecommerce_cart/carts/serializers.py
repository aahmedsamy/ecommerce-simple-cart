from rest_framework import serializers
from .models import Product, Cart, CartItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'in_stock_quantity']


class AddProductToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    product_id = serializers.IntegerField()


class ProductIdSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'ordered', 'product']
        read_only_fields = ['ordered']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class RetrieveCartSerializer(serializers.ModelSerializer):
    products = CartItemSerializer(many=True, source='cart_items')

    class Meta:
        model = Cart
        fields = ['ordered', 'products']
