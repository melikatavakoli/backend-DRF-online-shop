import random
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from persiantools.jdatetime import JalaliDate

from common.models import GenericModel
from course.models import Course
from .choices import OrderStatus
from product.models import Product

User = get_user_model()


class Order(GenericModel):
    order_no = models.CharField(max_length=16, unique=True, editable=False)
    is_successful = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    user = models.ForeignKey(
        User,
        related_name="user_orders",
        verbose_name="user",
        on_delete=models.CASCADE,
        blank=True,
        default="",
    )
    done_by = models.ForeignKey(
        User,
        related_name="order_done",
        verbose_name="done by",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        db_table = "order"

    def __str__(self):
        return (
            f"Order #{self.order_no} by {self.user.get_full_name() or self.user.email}"
        )

    def save(self, *args, **kwargs):
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            self.is_successful = True
        elif self.status in [OrderStatus.PENDING, OrderStatus.CANCELED]:
            self.is_successful = False
        if not self.order_no:
            self.order_no = self._generate_unique_order_no()
        super().save(*args, **kwargs)

    def _generate_unique_order_no(self):
        today = JalaliDate.today()
        prefix = f"{today.year % 100}-{today.month}-{today.day}-"
        while True:
            order_no = f"{prefix}{random.randrange(1000, 9999)}"
            if not Order.objects.filter(order_no=order_no).exists():
                return order_no

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_discount(self):
        return sum(item.total_discount for item in self.items.all())

    @property
    def payable_amount(self):
        return max(self.total_price - self.total_discount, 0)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def product_types(self):
        return list(
            {item.product.type for item in self.items.all() if item.product.type}
        )


class OrderItem(GenericModel):
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="order",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="item_product",
        verbose_name="product",
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="item_course",
        verbose_name="course",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "order_item"
        verbose_name_plural = "order_items"
        db_table = "order_item"

    def __str__(self):
        item_name = (
            self.product.title
            if self.product
            else (self.course.title if self.course else "Unknown Item")
        )
        order_no = self.order.order_no if self.order else "No Order"
        return f"{item_name} x {self.quantity} (Order #{order_no})"

    def clean(self):
        if self.product and self.course:
            raise ValidationError("OrderItem cannot have both product and course")

        if not self.product and not self.course:
            raise ValidationError("OrderItem must have either product or course")

    @property
    def total_price(self):
        try:
            if self.product:
                price = float(self.product.final_price or "0")
                return price * self.quantity
            if self.course:
                price = float(self.course.final_price or "0")
                return price * self.quantity
        except (ValueError, TypeError):
            return 0.0
        return 0.0

    @property
    def discount_amount(self):
        if not self.product:
            return 0.0
        try:
            price = float(self.product.final_price or "0")
        except (ValueError, TypeError):
            price = 0.0
        offer = str(self.product.offer or "").strip()
        if not offer:
            return 0.0
        try:
            if offer.endswith("%"):
                percent = float(offer.rstrip("%"))
                return (percent / 100) * price
            return float(offer)
        except (ValueError, TypeError):
            return 0.0

    @property
    def total_discount(self):
        return self.discount_amount * self.quantity
