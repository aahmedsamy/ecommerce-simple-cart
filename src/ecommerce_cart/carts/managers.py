from django.db import models


class CartManager(models.Manager):
    def get_open_cart(self):
        cart, _ = self.get_or_create(ordered=False)
        return cart