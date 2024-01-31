from django.urls import path

from carts.views import ProductListAPIView

urlpatterns = [
    path('products/', ProductListAPIView.as_view())
]