from django.db import models


class InvoiceStatus(models.TextChoices):
    UNPAID = "UN", "Unpaid"
    PAID = "P", "Paid"
    CANCELED = "C", "Canceled"
    REFUNDED = "R", "Refunded"
