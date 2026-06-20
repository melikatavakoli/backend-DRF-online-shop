from django.db import models


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    FAILED = "failed", "Failed"
    SUCCESS = "success", "Success"
