from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Product
from carts.serializers import CartSerializer, RetrieveCartSerializer, AddProductToCartSerializer, ProductIdSerializer
from .models import Customer
from .serializers import CustomerSerializer

@extend_schema_view(
    create=extend_schema(description='Used to create users.')
)
class CustomerViewSet(mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    def get_queryset(self):
        return Customer.objects.all()

    def get_serializer_class(self):

        if self.action in ['retrieve', 'create']:
            return CustomerSerializer
        elif self.action == 'my_open_cart':
            return RetrieveCartSerializer
        elif self.action in ['add_product_to_cart', 'update_product_quantity_in_cart']:
            return AddProductToCartSerializer
        elif self.action == 'remove_product_from_cart':
            return ProductIdSerializer
        return CartSerializer

    def _get_open_cart(self, customer):
        return customer.carts.get_open_cart()

    def _handle_exception_response(self, exception):
        return Response({'error': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_path='open-carts')
    def my_open_cart(self, request, *args, **kwargs):
        """
        End point to get current user's open cart
        """
        customer = self.get_object()
        open_cart = customer.carts.get_open_cart()
        serializer = self.get_serializer(open_cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "example": {'detail': 'Product added to the carts.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Product does not exist.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Insufficient stock for product `{product_id}`.'}
            },
        }
    )
    @action(detail=True, methods=['PUT'], url_path='add-to-carts')
    def add_product_to_cart(self, request, *args, **kwargs):
        """
        Endpoint to add product to current user's open cart
        """
        customer = self.get_object()
        open_cart = self._get_open_cart(customer)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.data.get('product_id')
        quantity = serializer.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
            open_cart.add_product_to_cart(product, quantity)
            return Response({'detail': 'Product added to the carts.'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist as e:
            return self._handle_exception_response(e)
        except ValueError as e:
            return self._handle_exception_response(e)

    @action(detail=True, methods=['POST'], url_path='remove-product')
    def remove_product_from_cart(self, request, *args, **kwargs):
        """
        Endpoint to remove product to current user's open cart
        """
        customer = self.get_object()
        open_cart = customer.carts.get_open_cart()
        product_id = request.data.get('product_id')

        try:
            open_cart.remove_product_from_cart(product_id)
            return Response({'detail': 'Product removed from the carts.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "example": {'detail': 'Product quantity updated in the carts.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Product does not exist.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Insufficient stock for product `{product_id}`.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Product is not in the carts.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'New quantity should be greater than 0.'}
            },
        }
    )
    @action(detail=True, methods=['POST'], url_path='update-product-quantity')
    def update_product_quantity_in_cart(self, request, *args, **kwargs):
        customer = self.get_object()
        open_cart = customer.carts.get_open_cart()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.data.get('product_id')
        quantity = serializer.data.get('quantity', 1)
        try:
            product = Product.objects.get(id=product_id)
            open_cart.update_product_quantity_in_cart(product, quantity)
            return Response({'detail': 'Product quantity updated in the carts.'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist as e:
            return self._handle_exception_response(e)
        except ValueError as e:
            return self._handle_exception_response(e)

    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "example": {'detail': 'Checkout done successfully.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Cart is already ordered.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Insufficient stock for product `{product_id}`.'}
            },
            status.HTTP_400_BAD_REQUEST: {
                "example": {'error': 'Product is not in the carts.'}
            },
        }
    )
    @action(detail=True, methods=['GET'], url_path='checkout')
    def checkout(self, request, *args, **kwargs):
        customer = self.get_object()
        open_cart = customer.carts.get_open_cart()
        try:
            open_cart.checkout()
        except ValueError as e:
            return self._handle_exception_response(e)
        return Response({'detail': 'Checkout done successfully.'}, status=status.HTTP_200_OK)
