from django.contrib.auth import get_user_model
from django.db import models
from address.models import Branch
from common.models import GenericModel
from users.types import (
    EducationChoices,
    FieldChoices,
    GradeChoices,
)
from .services import years

User = get_user_model()


class Speciality(GenericModel):
    title = models.CharField(max_length=63, null=True, blank=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "speciality"
        verbose_name_plural = "specialities"
        db_table = "speciality"
        ordering = ("-_updated_at", "-_created_at")

    def __str__(self) -> str:
        return self.title or "none"


class Consultant(GenericModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    specialities = models.ManyToManyField(Speciality, related_name="consultants", blank=True)
    major = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    education = models.IntegerField(choices=EducationChoices.choices, null=True, blank=True)
    is_present = models.BooleanField(default=True)

    class Meta:
        verbose_name = "consultant"
        verbose_name_plural = "consultant"
        db_table = "consultant"
        ordering = ("-_updated_at",)

    def __str__(self) -> str:
        return self.user.full_name or "none"


class Student(GenericModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    grade = models.IntegerField(choices=GradeChoices.choices, null=True, blank=True)
    field = models.CharField(max_length=100, choices=FieldChoices.choices, blank=True, default="")
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "student"
        verbose_name_plural = "students"
        db_table = "student"
        ordering = ("-_updated_at",)

    def __str__(self) -> str:
        return self.user.full_name or "none"


class TopStudent(GenericModel):
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, related_name="top_students", on_delete=models.SET_NULL, null=True,blank=True,)
    uni_accepted_major = models.CharField(max_length=300, default="")
    university = models.CharField(max_length=300, default="")
    first_name = models.CharField(max_length=127, null=True,blank=True)
    last_name = models.CharField(max_length=127, null=True,blank=True)
    field = models.CharField(max_length=100, choices=FieldChoices.choices, null=True,blank=True)
    description = models.TextField(blank=True, default="")
    rank = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to="profile/top-students/", blank=True, null=True)
    year = models.PositiveSmallIntegerField(choices=years, null=True,blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "top_student"
        verbose_name_plural = "top_students"
        db_table = "top_students"
        ordering = ("-_updated_at",)

    def __str__(self) -> str:
        return self.full_name or "none"

    def save(self, *args, **kwargs):
        if self.student and not (self.first_name or self.last_name):
            self.first_name = self.student.user.first_name
            self.last_name = self.student.user.last_name
            self.field = self.student.field
        super().save(*args, **kwargs)
