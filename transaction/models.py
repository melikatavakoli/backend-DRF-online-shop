from decimal import ROUND_HALF_UP, Decimal
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction as db_transaction
from transaction.utils import generate_random_transaction_no

from cart.models import Cart
from common.models import GenericModel
from invoice.models import Invoice
from invoice.choices import InvoiceStatus
from order.models import Order
from product.models import Product
from transaction.choices import TransactionStatus

User = get_user_model()


class PaymentReceipt(GenericModel):
    user = models.ForeignKey(
        User,
        related_name="receipts_user",
        verbose_name="user",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="media", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "payment_receipt"
        verbose_name = "payment_receipt"
        db_table = "payment_receipt"

    def __str__(self):
        return f"Receipt {self.user} - {self.uploaded_at}"


class Transaction(GenericModel):
    user = models.ForeignKey(
        User,
        related_name="user_transactions",
        verbose_name="user",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        Order,
        related_name="order_transactions",
        verbose_name="order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    invoice = models.ForeignKey(
        Invoice,
        related_name="invoice_transactions",
        verbose_name="invoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cart = models.ForeignKey(
        Cart,
        related_name="cart_transactions",
        verbose_name="cart",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    payment_receipt = models.ForeignKey(
        PaymentReceipt,
        on_delete=models.SET_NULL,
        related_name="reciept_transactions",
        verbose_name="payment_receipt",
        null=True,
        blank=True,
    )
    transaction_no = models.CharField(
        max_length=50, unique=True, blank=True, null=True, editable=False
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, default="0", blank=True
    )
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    card_number = models.CharField(max_length=50, blank=True, null=True)
    ref_number = models.CharField(max_length=50, blank=True, null=True)
    track_id = models.CharField(max_length=300, blank=True, null=True)
    gateway = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(
        max_length=300,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    stock_reduced = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
        db_table = "transaction"

    def __str__(self):
        return f"{self.transaction_no} | {self.user} | {self.status}"

    def reduce_product_stock(self):
        """
        Reduce order product stock after successful transaction.
        Only performed once.
        """
        if not self.is_successful or not self.order or self.stock_reduced:
            return
        with db_transaction.atomic():
            for item in self.order.items.select_related("product").select_for_update():
                product: Product = item.product
                if product.available_quantity >= item.quantity:
                    product.available_quantity -= item.quantity
                    product.save(update_fields=["available_quantity"])
                else:
                    raise ValueError(
                        f"Insufficient stock for product {product.name}: "
                        f"available {product.available_quantity} - requested {item.quantity}"
                    )

            self.stock_reduced = True
            self.save(update_fields=["stock_reduced"])

    @property
    def calculated_amount(self):
        """Actual transaction amount: if invoice is related, get from invoice"""
        if self.invoice:
            return Decimal(self.invoice.final_amount or 0)
        return self.amount or Decimal("0.00")

    @property
    def fee(self):
        """Transaction fee: 1% of transaction amount"""
        return (self.calculated_amount * Decimal("0.01")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def total_amount_with_fee(self):
        """Total transaction amount + fee"""
        return (self.calculated_amount + self.fee).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def is_successful(self):
        return self.status == TransactionStatus.success

    def save(self, *args, **kwargs):
        """
        Auto-generate transaction number and save model
        and reduce order product stock if transaction is successful
        """
        if not self.transaction_no:
            self.transaction_no = generate_random_transaction_no()
        super().save(*args, **kwargs)
        if self.invoice and self.is_successful:
            self.invoice.status = InvoiceStatus.paid
            self.invoice.save(update_fields=["status"])
        if self.is_successful and self.order and not self.stock_reduced:
            self.reduce_product_stock()
