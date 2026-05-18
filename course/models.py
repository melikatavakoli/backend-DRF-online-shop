from datetime import timedelta
from django.conf import settings
from django.db import models
from common.format import generate_slug
from common.models import GenericModel
from course.type import CourseStatus, SessionVideoUploadStatus
from users.models import Student


class Teacher(GenericModel):
    title = models.CharField(max_length=310, blank=True, default="")
    full_name = models.CharField(max_length=310, blank=True, default="")
    description = models.CharField(max_length=1000, blank=True, default="")
    avatar = models.ImageField(upload_to="upload_to_by_date", blank=True, null=True)

    class Meta:
        verbose_name = "teacher"
        verbose_name_plural = "teachers"
        db_table = "teacher"

    def __str__(self) -> str:
        return self.title or "None"


class Subject(GenericModel):
    title = models.CharField(max_length=310, blank=True, default="")

    class Meta:
        verbose_name = "subject"
        verbose_name_plural = "subjects"
        db_table = "subject"

    def __str__(self) -> str:
        return self.title or "None"


class Grade(GenericModel):
    title = models.CharField(max_length=310, blank=True, default="")

    class Meta:
        verbose_name = "grade"
        verbose_name_plural = "grades"
        db_table = "grade"

    def __str__(self) -> str:
        return self.title or "None"


class Field(GenericModel):
    title = models.CharField(max_length=310, blank=True, default="")

    class Meta:
        verbose_name = "field"
        verbose_name_plural = "fields"
        db_table = "field"

    def __str__(self) -> str:
        return self.title or "None"


class Session(GenericModel):
    course = models.ForeignKey(related_name="sessions", on_delete=models.CASCADE, null=True, blank=True,)
    title = models.CharField(max_length=310, blank=True, default="")
    session_no = models.PositiveSmallIntegerField(null=True, blank=True)
    video = models.URLField(blank=True, default="")
    is_free = models.BooleanField(default=False)
    length = models.DurationField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True,)

    class Meta:
        verbose_name = "session"
        verbose_name_plural = "sessions"
        db_table = "session"

    def __str__(self) -> str:
        return self.title or "None"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.title, Session, self.pk)
        super().save(*args, **kwargs)


class SessionProgress(GenericModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="session_progress", verbose_name="progress_user", null=True, blank=True,
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="progress",
        verbose_name="session",
        null=True,
        blank=True,
    )
    watched_duration = models.DurationField(default=timedelta(0))

    class Meta:
        unique_together = ("user", "session")
        verbose_name = "session_progress"
        verbose_name_plural = "session_progress"
        db_table = "session_progress"

    @property
    def progress_percentage(self):
        if self.session and not self.session.length:
            return 0
        watched_duration = self.watched_duration.total_seconds()
        session_length = self.session.length.total_seconds()
        if session_length == 0:
            return 0
        return min(watched_duration / session_length * 100, 100)

    @property
    def is_completed(self):
        return self.progress_percentage >= 95


class CourseCategory(GenericModel):
    title = models.CharField(max_length=310, blank=True, default="")
    session = models.ManyToManyField(Session, related_name="session_category")

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        db_table = "category"

    def __str__(self) -> str:
        return self.title or "None"

    @property
    def total_sessions(self):
        return self.session.count()

    @property
    def total_length(self):
        total_seconds = sum(
            s.length.total_seconds() for s in self.session.all() if s.length
        )
        return timedelta(seconds=total_seconds)


class Course(GenericModel):
    title = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    price = models.CharField(max_length=20, blank=True, default="")
    discount_price = models.CharField(max_length=20, blank=True, default="")
    final_price = models.CharField(max_length=20, blank=True, default="")
    is_free = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    has_discount = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CourseStatus.choices, default=CourseStatus.DRAFT)
    has_video = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, default="")
    course_length = models.DurationField(blank=True, null=True)
    grade = models.ManyToManyField(Grade, related_name="grade_course", verbose_name="grade")
    field = models.ManyToManyField(Field, related_name="field_course", verbose_name="field")
    subject = models.ForeignKey(Subject, related_name="subject_course", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to="media", blank=True, null=True)
    category = models.ManyToManyField(CourseCategory, related_name="category_course", verbose_name="category")
    teacher = models.ForeignKey(Teacher, related_name="teacher_course", verbose_name="teacher", on_delete=models.CASCADE, null=True, blank=True,)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)
    users = models.ManyToManyField(Student, related_name="courses", verbose_name="students", blank=True)

    class Meta:
        verbose_name = "course"
        verbose_name_plural = "courses"
        db_table = "course"

    def __str__(self):
        return self.title or "none"

    def save(self, *args, **kwargs):
        price_str = self.price or "0.00"
        discount_str = (self.discount_price or "").strip()
        try:
            price_val = float(price_str)
        except (ValueError, TypeError):
            price_val = 0.0
        discount_val = 0.0
        if self.has_discount and discount_str:
            try:
                if discount_str.endswith("%"):
                    percent = float(discount_str.rstrip("%"))
                    if percent < 0 or percent > 100:
                        raise ValueError("Discount percent must be between 0 and 100")
                    discount_val = price_val * (percent / 100)
                else:
                    discount_val = float(discount_str)
            except (ValueError, TypeError):
                discount_val = 0.0
        if self.is_free:
            self.final_price = "0.00"
        else:
            final_val = price_val - discount_val
            if final_val < 0:
                final_val = 0.0
            self.final_price = f"{final_val:.2f}"
        if not self.slug:
            self.slug = generate_slug(self.title, Course, self.pk)
        super().save(*args, **kwargs)

    @property
    def total_sessions(self):
        return sum(cat.total_sessions for cat in self.category.all())

    @property
    def total_length(self):
        total_seconds = sum(
            cat.total_length.total_seconds() for cat in self.category.all()
        )
        return timedelta(seconds=total_seconds)


class CourseFeature(GenericModel):
    course = models.ForeignKey(Course, related_name="features_course", on_delete=models.CASCADE, blank=True)
    text = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "feature"
        verbose_name_plural = "features"
        db_table = "feature"

    def __str__(self):
        return self.text or "none"


class CourseLearning(GenericModel):
    course = models.ForeignKey(Course, related_name="learnings_course", on_delete=models.CASCADE, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "learning"
        verbose_name_plural = "learnings"
        db_table = "learning"
        
    def __str__(self):
        return self.text or "none"


class TagCourse(GenericModel):
    course = models.ForeignKey(Course, related_name="tag_course", on_delete=models.CASCADE, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "tag_course"
        verbose_name_plural = "tag_course"
        db_table = "tag_course"

    def __str__(self) -> str:
        return self.text or "none"
