from decimal import Decimal
from django.db.models import Q, UniqueConstraint
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

from common.models import GenericModel
from course.models import Course
from order.models import Order
from product.models import Product

User = get_user_model()


class Cart(GenericModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    # order = models.OneToOneField(Order, on_delete=models.SET_NULL, related_name="carts", null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20, choices=CartStatus, default="pending")    

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        db_table="cart"

    def __str__(self):
        return str(self.status)

    def __iter__(self):
        return iter(self.cart_items.all)
    
    def clear(self):
        self.cart_item.all().delete()
        
    @property
    def total_quantity(self):
        return self.cart_items.aggerate(total=("quantity"))["total"] or 0
    
    @property
    def total_base_pricw(self):
        total=0.0
        for item in self.cart_items.all():
            try:
                total+=float(item.base_price or "0") * (item.quantity or 0)
            except(ValueError, TypeError):
                continue
            
        return f"{total:2f}"
    
    @property
    def total_discount(self):
        total = 0.0
        for item in self.cart_items.all():
            try:
                total += item.discount_amount * (item.quantity or 0)
            except (ValueError, TypeError):
                continue
        return f"{total:.2f}"

    @property
    def total_price(self):
        total = 0.0
        for item in self.cart_items.all():
            try:
                total += float(item.final_price or "0") * (item.quantity or 0)
            except (ValueError, TypeError):
                continue
        return f"{total:.2f}"
    
    def cart_serializable(self):
        representation = {}

        cart_items = self.cart_items.select_related("product", "course").all()

        for item in cart_items:
            quantity = item.quantity or 0
            base_price = float(item.base_price or 0)
            final_price = float(item.final_price or 0)
            total_price = float(item.total_price or 0)

            discount_per_item = float(getattr(item, "discount_amount", 0) or 0)
            total_discount = discount_per_item * quantity

            representation[str(item.id)] = {
                "quantity": quantity,
                "base_price": base_price,
                "final_price": final_price,
                "total_price": total_price,
                "discount_amount": total_discount,
                "product": item.product.title if item.product else None,
                "course": item.course.title if item.course else None,
            }

        return representation
    
    
class CartItem(GenericModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    class Meta:
        db_table = "cart_item"
        constraints = [
            UniqueConstraint(
                fields=["cart", "product"],
                condition=Q(product__isnull=False),
                name="unique_product_per_cart",
            ),
            UniqueConstraint(
                fields=["cart", "course"],
                condition=Q(course__isnull=False),
                name="unique_course_per_cart",
            ),
        ]

    def __str__(self):
        if self.product:
            return f"{self.product.title} x {self.quantity}"
        elif self.course:
            return f"{self.course.title} x {self.quantity}"
        return f"Item #{self.id} x {self.quantity}"

    def save(self, *args, **kwargs):
        if self.product:
            self.base_price = self.product.base_price
            self.final_price = self.product.final_price
        elif self.course:
            self.base_price = self.course.price
            self.final_price = self.course.final_price

        super().save(*args, **kwargs)

    @property
    def discount_amount(self):
        if not self.product:
            return 0.0
        try:
            base_price = float(self.product.base_price or "0")
        except (ValueError, TypeError):
            base_price = 0.0

        offer_str = str(getattr(self.product, "offer", "")).strip()
        if not offer_str:
            return 0.0

        try:
            if offer_str.endswith("%"):
                percent = float(offer_str.rstrip("%"))
                return (percent / 100) * base_price
            return float(offer_str)
        except (ValueError, TypeError):
            return 0.0

    @property
    def total_price(self):
        try:
            price = float(self.final_price or self.base_price or "0")
            return price * (self.quantity or 0)
        except (ValueError, TypeError):
            return 0.0

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.product and not self.course:
            raise ValidationError("CartItem must have either a product or a course.")
        if self.product and self.course:
            raise ValidationError("CartItem cannot have both product and course.")
