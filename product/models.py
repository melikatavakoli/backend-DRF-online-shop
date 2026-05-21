from django.db import models
from django.utils.text import slugify

from common.format import upload_to_by_date
from common.models import GenericModel
from course.models import CourseCategory, Field, Grade
from .choices import ProductType


class Product(GenericModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    final_price = models.CharField(max_length=255, blank=True, null=True)
    offer = models.CharField(max_length=255, blank=True, null=True)
    base_price = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(
        CourseCategory,
        related_name="product_category",
        verbose_name="category",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    grade = models.ManyToManyField(
        Grade, related_name="grade_product", verbose_name="grade", blank=True
    )
    field = models.ManyToManyField(
        Field, related_name="field_product", verbose_name="field", blank=True
    )
    education_level = models.CharField(max_length=255, blank=True, null=True)
    available_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=upload_to_by_date, blank=True, null=True)
    type = models.CharField(choices=ProductType, blank=True, null=True)
    slug = models.SlugField(
        max_length=255, unique=True, allow_unicode=True, blank=True, null=True
    )
    has_offer = models.BooleanField(default=False)

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
        db_table = "product"

    def __str__(self):
        return self.title or "none"

    def calculate_price_after_offer(self) -> str:
        try:
            base_price = float(self.base_price or "0")
        except (ValueError, TypeError):
            base_price = 0.0
        discount = 0.0
        offer_str = (self.offer or "").strip()
        if offer_str:
            try:
                if offer_str.endswith("%"):
                    percent = float(offer_str.rstrip("%"))
                    if percent < 0 or percent > 100:
                        percent = 0.0
                    discount = (percent / 100) * base_price
                else:
                    discount = float(offer_str)
            except (ValueError, TypeError):
                discount = 0.0
        final = max(base_price - discount, 0.0)
        return str(int(final))

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title, allow_unicode=True)
        self.has_offer = bool(self.offer and str(self.offer).strip())
        self.final_price = self.calculate_price_after_offer()
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.available_quantity > 0
