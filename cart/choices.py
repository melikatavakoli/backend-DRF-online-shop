from django.db import models


class CartStatus(models.TextChoices):
    pending = "P", "PENDING"
    converted = "C", "CONVERTED"
    cancelled = "CA", "CANCELLED"
