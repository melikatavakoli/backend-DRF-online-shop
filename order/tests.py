from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from course.models import Course, CourseCategory
from order.models import Order, OrderItem
from order.types import OrderStatus
from product.models import Product
from users.models import User


class OrderModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="pass1234",
            mobile="09123456789",
        )

        self.category = CourseCategory.objects.create(title="test category")

        self.product1 = Product.objects.create(
            title="Product 1",
            final_price=Decimal("100"),
            offer="20%",
            category=self.category,
        )

        self.course1 = Course.objects.create(
            title="Test Course", final_price=Decimal("200")
        )

        self.order = Order.objects.create(user=self.user)

    def test_order_creation(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.user, self.user)
        self.assertTrue(order.order_no)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertFalse(order.is_successful)

    def test_order_item_course_only(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem(order=order, course=self.course1, quantity=2)
        item.full_clean()
        item.save()
        self.assertEqual(item.total_price, Decimal("400"))
        self.assertEqual(item.total_discount, Decimal("0"))

    def test_order_item_product_only(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem(order=order, product=self.product1, quantity=3)
        item.full_clean()
        item.save()
        self.assertEqual(item.total_price, Decimal("300"))
        self.assertEqual(item.discount_amount, Decimal("20"))  # 20% از 100
        self.assertEqual(item.total_discount, Decimal("60"))

    def test_order_item_invalid_both_product_and_course(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem(order=order, product=self.product1, course=self.course1)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_order_item_invalid_neither_product_nor_course(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem(order=order)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_order_totals_with_mixed_items(self):
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, product=self.product1, quantity=2)
        OrderItem.objects.create(order=order, course=self.course1, quantity=1)

        self.assertEqual(order.total_price, Decimal("400"))
        self.assertEqual(order.total_discount, Decimal("40"))
        self.assertEqual(order.payable_amount, Decimal("360"))
        self.assertEqual(order.total_quantity, 3)
        self.assertEqual(order.product_types, [""])  # چون type محصول پیش‌فرض ""
