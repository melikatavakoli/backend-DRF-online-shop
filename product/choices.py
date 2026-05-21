from django.db import models


class ProductType(models.TextChoices):
    book = "book", "Book"
    booklet = "booklet", "Booklet"
    planner = "planner", "Planner"
