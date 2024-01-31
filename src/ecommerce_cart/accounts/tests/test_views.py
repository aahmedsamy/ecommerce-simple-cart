import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from carts.models import Cart, Product
from ..models import Customer


@pytest.fixture
def customer():
    return Customer.objects.create(name='Test Customer')


@pytest.fixture
def product():
    return Product.objects.create(name='Test Product', in_stock_quantity=10)


@pytest.fixture
def open_cart(customer):
    return Cart.objects.create(customer=customer)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_retrieve_customer(api_client, customer):
    response = api_client.get(reverse('customer-detail', args=[customer.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Test Customer'


@pytest.mark.django_db
def test_create_customer(api_client):
    data = {'user': 1, 'name': 'New Customer'}
    response = api_client.post(reverse('customer-list'), data=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'New Customer'


@pytest.mark.django_db
def test_add_product_to_cart(api_client, customer, open_cart, product):
    data = {'product_id': product.id, 'quantity': 2}
    response = api_client.put(reverse('customer-add-product-to-cart', args=[customer.id]), data=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['detail'] == 'Product added to the carts.'



@pytest.mark.django_db
def test_remove_product_from_cart(api_client, customer, open_cart, product):
    open_cart.products.add(product)
    data = {'product_id': product.id}
    response = api_client.post(reverse('customer-remove-product-from-cart', args=[customer.id]), data=data)
    print(response.data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Product removed from the carts.'
