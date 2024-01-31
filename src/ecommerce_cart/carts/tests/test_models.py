import pytest
from django.db import transaction
from model_bakery import baker

from ..models import Cart


@pytest.fixture
def sample_customer():
    return baker.make('accounts.Customer')


@pytest.fixture
def sample_product():
    return baker.make('carts.Product', in_stock_quantity=10)


@pytest.fixture
def open_cart(sample_customer):
    return Cart.objects.create(customer=sample_customer)


@pytest.mark.django_db
def test_add_product_to_cart(open_cart, sample_product):
    assert open_cart.is_open_cart()
    cart_item = open_cart.add_product_to_cart(sample_product, quantity=3)
    assert cart_item.product == sample_product
    assert cart_item.quantity == 3


@pytest.mark.django_db
def test_add_product_to_cart_insufficient_stock(open_cart, sample_product):
    sample_product.in_stock_quantity = 2
    sample_product.save()

    with pytest.raises(ValueError, match=r'Insufficient stock for product .*'):
        open_cart.add_product_to_cart(sample_product, quantity=3)


@pytest.mark.django_db
def test_update_product_quantity_in_cart(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    cart_item = open_cart.update_product_quantity_in_cart(sample_product, new_quantity=5)
    assert cart_item.quantity == 5


@pytest.mark.django_db
def test_update_product_quantity_in_cart_invalid_quantity(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)

    with pytest.raises(ValueError, match=r'New quantity should be greater than 0.'):
        open_cart.update_product_quantity_in_cart(sample_product, new_quantity=0)


@pytest.mark.django_db
def test_update_product_quantity_in_cart_insufficient_stock(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    sample_product.in_stock_quantity = 2
    sample_product.save()

    with pytest.raises(ValueError, match=r'Insufficient stock for product .*'):
        open_cart.update_product_quantity_in_cart(sample_product, new_quantity=5)


@pytest.mark.django_db
def test_remove_product_from_cart(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    assert open_cart.cart_items.count() == 1
    assert open_cart.remove_product_from_cart(sample_product)
    assert open_cart.cart_items.count() == 0


@pytest.mark.django_db
def test_remove_product_from_cart_not_in_cart(open_cart, sample_product):
    with pytest.raises(ValueError, match=r'Product is not in the carts.'):
        open_cart.remove_product_from_cart(sample_product)


@pytest.mark.django_db
def test_checkout(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    sample_product.in_stock_quantity = 3
    sample_product.save()
    assert open_cart.is_open_cart()

    with transaction.atomic():
        updated_cart = open_cart.checkout()
        assert not updated_cart.is_open_cart()
        assert updated_cart.ordered

    # Verify that product stock has been deducted
    sample_product.refresh_from_db()
    assert sample_product.in_stock_quantity == 0


@pytest.mark.django_db
def test_checkout_already_ordered(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    open_cart.checkout()

    with pytest.raises(ValueError, match=r'Cart is already ordered.'):
        open_cart.checkout()


@pytest.mark.django_db
def test_checkout_insufficient_stock(open_cart, sample_product):
    open_cart.add_product_to_cart(sample_product, quantity=3)
    sample_product.in_stock_quantity = 2
    sample_product.save()

    with pytest.raises(ValueError) as exc_info:
        open_cart.checkout()
    # Check if the expected substring is in the error message
    assert 'Insufficient stock for product' in str(exc_info.value)
