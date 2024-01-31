from django.db import models, transaction
from django.db.models import F

from accounts.models import Customer
from .managers import CartManager


class Product(models.Model):
    name = models.CharField(max_length=255)
    in_stock_quantity = models.IntegerField(default=0)


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='carts')
    products = models.ManyToManyField(Product, through='CartItem')
    ordered = models.BooleanField(default=False)

    objects = CartManager()

    def is_open_cart(self) -> bool:
        return not self.ordered

    def add_product_to_cart(self, product: Product, quantity: int = 1) -> CartItem:
        if not self.is_open_cart():
            raise ValueError('Cart is already ordered.')
        if product.in_stock_quantity < quantity:
            raise ValueError(f'Insufficient stock for product {product.id}.')

        cart_item, created = CartItem.objects.get_or_create(
            cart=self, product=product,
        )
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item

    def update_product_quantity_in_cart(self, product: Product, new_quantity: int) -> CartItem:
        if not self.is_open_cart():
            raise ValueError('Cart is already ordered.')
        if new_quantity <= 0:
            raise ValueError('New quantity should be greater than 0.')

        try:
            if product.in_stock_quantity < new_quantity:
                raise ValueError(f'Insufficient stock for product {product.id}.')
            cart_item = self.cart_items.get(product=product)
            cart_item.quantity = new_quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            raise ValueError('Product is not in the carts.')

    def remove_product_from_cart(self, product: Product) -> bool:
        if not self.is_open_cart():
            raise ValueError('Cart is already ordered.')
        try:
            cart_item = self.cart_items.get(product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            raise ValueError('Product is not in the carts.')

    def checkout(self) -> 'Cart':
        if not self.is_open_cart():
            raise ValueError('Cart is already ordered.')

        with transaction.atomic():
            # Lock the Cart and associated Product rows for update to handle race conditions
            cart_items = self.cart_items.select_for_update().select_related('product').all()

            # Validate product quantities and deduct from in_stock_quantity
            for cart_item in cart_items:
                product = cart_item.product
                if product.in_stock_quantity < cart_item.quantity:
                    raise ValueError(f'Insufficient stock for product {product.id}.')

                # Deduct the in_stock_quantity
                product.in_stock_quantity -= cart_item.quantity
                product.save()

            # Mark the carts as ordered
            self.ordered = True
            self.save()

            return self
