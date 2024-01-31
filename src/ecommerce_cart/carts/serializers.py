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

    def create(self, validated_data):
        products_data = validated_data.pop('product', [])
        cart_instance = self.instance

        for product_data in products_data:
            # Create or get the product based on the provided data
            product, _ = Product.objects.get(id=product_data.get('id'))

            # Add the product to the existing carts
            cart_instance.add_product_to_cart(product, product_data.get('quantity'))

        return cart_instance


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class RetrieveCartSerializer(serializers.ModelSerializer):
    products = CartItemSerializer(many=True, source='cart_items')

    class Meta:
        model = Cart
        fields = ['ordered', 'products']
