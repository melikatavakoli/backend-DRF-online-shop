from django.contrib.auth.models import AbstractUser
from django.db import models

from address.models import City, Country, State
from common.format import calculate_age, common_datetime_str
from common.models import BaseModel
from common.managers import UserManager
from core.types import RoleType, StatusType


class BaseUser(AbstractUser, BaseModel):
    username = None
    mobile = models.CharField(max_length=11, unique=True)
    email = models.EmailField(blank=True, default="")
    role = models.CharField(max_length=1, choices=RoleType.choices, default=RoleType.CUSTOMER)
    description = models.TextField(blank=True, default="")
    birth_date = models.DateField(blank=True, null=True)
    password_updated_at = models.DateTimeField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    objects = UserManager(alive_only=True)

    @property
    def full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else "Anonymous"

    @property
    def age(self):
        return calculate_age(self.birth_date)

    @property
    def created_at_display(self):
        return common_datetime_str(self.created_at)

    @property
    def is_customer(self):
        return self.role == RoleType.CUSTOMER
    
    @property
    def is_vendor(self):
        return self.role == RoleType.VENDOR
    
    @property
    def is_staff_user(self):
        return self.role in [RoleType.STAFF, RoleType.ADMIN]

    def __str__(self):
        return self.full_name or self.mobile

    class Meta:
        verbose_name = "base_user"
        verbose_name_plural = "base_users"
        db_table = "base_user"
        ordering = ("-updated_at", "-created_at")
        indexes = (
            models.Index(fields=["id"], name="user_id_idx"),
            models.Index(fields=["mobile"], name="user_mobile_idx"),
        )
