from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from common.serializers import GenericModelSerializer
from users.models import Student
from users.serializers import StudentListSerializer
from .models import (
    Course,
    CourseCategory,
    CourseFeature,
    CourseLearning,
    Field,
    Grade,
    Session,
    SessionProgress,
    Subject,
    TagCourse,
    Teacher,
)


class TeacherSerializer(GenericModelSerializer):
    class Meta:
        model = Teacher
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "full_name",
            "description",
            "avatar",
        )


class SubjectSerializer(GenericModelSerializer):
    class Meta:
        model = Subject
        fields = GenericModelSerializer.Meta.fields + ("title",)


class GradeSerializer(GenericModelSerializer):
    class Meta:
        model = Grade
        fields = GenericModelSerializer.Meta.fields + ("title",)


class FieldSerializer(GenericModelSerializer):
    class Meta:
        model = Field
        fields = GenericModelSerializer.Meta.fields + ("title",)


class SessionWithProgressSerializer(GenericModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "video",
            "length",
            "session_no",
            "is_free",
            "progress_percentage",
            "is_completed",
        )

    @extend_schema_field(serializers.FloatField)
    def get_progress_percentage(self, obj) -> float:
        user = self.context["request"].user
        if not user.is_authenticated:
            return 0
        progress = obj.progress.filter(user=user).first()
        return progress.progress_percentage if progress else 0

    @extend_schema_field(serializers.BooleanField)
    def get_is_completed(self, obj) -> bool:
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        progress = obj.progress.filter(user=user).first()
        return progress.is_completed if progress else False


class SessionProgressUpdateSerializer(GenericModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = SessionProgress
        fields = GenericModelSerializer.Meta.fields + (
            "watched_duration",
            "progress_percentage",
            "is_completed",
        )

    def validate_watched_duration(self, value):
        progress = self.instance
        if progress and value < progress.watched_duration:
            raise serializers.ValidationError("watched_duration cannot decrease")
        return value


class SessionSerializer(GenericModelSerializer):
    progress = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    video_display = serializers.SerializerMethodField()
    has_access = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    video = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Session
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "slug",
            "length",
            "is_free",
            "progress",
            "is_completed",
            "video",
            "video_display",
            "has_access",
            "message",
            "course",
        )

    def get_progress(self, obj) -> float:
        user = self.context["request"].user
        if not user.is_authenticated:
            return 0
        progress = obj.progress.filter(user=user).first()
        return progress.progress_percentage if progress else 0

    def get_is_completed(self, obj) -> bool:
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        progress = obj.progress.filter(user=user).first()
        return progress.is_completed if progress else False

    def _check_access(self, obj):
        request = self.context.get("request")
        user = request.user
        course = obj.course
        if not course:
            return False, "این جلسه دوره‌ای ندارد."
        if user.is_staff or user.is_superuser:
            return True, None
        if obj.is_free:
            if not user.is_authenticated:
                return (
                    False,
                    "برای مشاهده دوره باید وارد حساب کاربری شوید.",
                )
            return True, None
        if course.is_free:
            return True, None
        if not user.is_authenticated:
            return (
                False,
                "برای مشاهده این جلسه باید وارد حساب شوید و دوره را خریداری کنید.",
            )
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return False, "برای مشاهده این جلسه باید دوره را خریداری کنید."
        if course.users.filter(id=student.id).exists():
            return True, None
        return False, "برای مشاهده این جلسه باید دوره را خریداری کنید."

    def get_has_access(self, obj):
        access, _ = self._check_access(obj)
        return access

    def get_message(self, obj):
        access, msg = self._check_access(obj)
        return msg

    def get_video_display(self, obj):
        access, _ = self._check_access(obj)
        if not access:
            return None
        return getattr(obj, "video", None)


class CategorySerializer(GenericModelSerializer):
    session = SessionWithProgressSerializer(many=True, read_only=True)
    total_sessions = serializers.IntegerField(read_only=True)
    total_length = serializers.DurationField(read_only=True)

    class Meta:
        model = CourseCategory
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "session",
            "total_sessions",
            "total_length",
        )


class CourseDetailSerializer(GenericModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    field = FieldSerializer(read_only=True, many=True)
    grade = GradeSerializer(read_only=True, many=True)
    total_sessions = serializers.IntegerField(read_only=True)
    total_length = serializers.DurationField(read_only=True)

    class Meta:
        model = Course
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "description",
            "price",
            "slug",
            "discount_price",
            "is_free",
            "has_discount",
            "status",
            "has_video",
            "video_url",
            "course_length",
            "grade",
            "field",
            "subject",
            "image",
            "category",
            "teacher",
            "total_sessions",
            "total_length",
            "is_private",
        )

    def get_total_sessions(self, obj):
        return obj.sessions.count()


class CourseUpdateSerializer(GenericModelSerializer):
    patch_grade = serializers.CharField(write_only=True, required=False)
    patch_field = serializers.CharField(write_only=True, required=False)
    patch_category = serializers.CharField(write_only=True, required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), required=False)

    class Meta:
        model = Course
        fields = (
            "title",
            "description",
            "price",
            "discount_price",
            "is_free",
            "has_discount",
            "status",
            "has_video",
            "video_url",
            "course_length",
            "patch_grade",
            "patch_field",
            "patch_category",
            "subject",
            "teacher",
            "image",
            "is_private",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        patch_grade = self.initial_data.get("patch_grade")
        patch_field = self.initial_data.get("patch_field")
        patch_category = self.initial_data.get("patch_category")

        def parse_ids(value):
            return [x.strip() for x in value.split(",") if x.strip()]
        if patch_grade:
            ids = parse_ids(patch_grade)
            instance.grade.set(Grade.objects.filter(id__in=ids))
        if patch_field:
            ids = parse_ids(patch_field)
            instance.field.set(Field.objects.filter(id__in=ids))
        if patch_category:
            ids = parse_ids(patch_category)
            instance.category.set(CourseCategory.objects.filter(id__in=ids))
        return instance


class CourseCreateSerializer(GenericModelSerializer):
    grade = serializers.CharField(write_only=True, required=False)
    field = serializers.CharField(write_only=True, required=False)
    category = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Course
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "description",
            "price",
            "discount_price",
            "is_free",
            "has_discount",
            "status",
            "is_private",
            "has_video",
            "video_url",
            "course_length",
            "grade",
            "field",
            "subject",
            "image",
            "category",
            "teacher",
            "final_price",
        )
        read_only_fields = ("final_price",)

    def create(self, validated_data):
        grade_str = validated_data.pop("grade", "")
        field_str = validated_data.pop("field", "")
        category_str = validated_data.pop("category", "")
        with transaction.atomic():
            course = Course.objects.create(**validated_data)
            if grade_str:
                grade_ids = [g.strip() for g in grade_str.split(",") if g.strip()]
                course.grade.set(grade_ids)
            if field_str:
                field_ids = [f.strip() for f in field_str.split(",") if f.strip()]
                course.field.set(field_ids)
            if category_str:
                category_ids = [c.strip() for c in category_str.split(",") if c.strip()]
                course.category.set(category_ids)
        return course


class CourseListSerializer(GenericModelSerializer):
    category = serializers.StringRelatedField(many=True, read_only=True)
    subject = serializers.CharField(source="subject.title", read_only=True)
    teacher = serializers.CharField(source="teacher.full_name", read_only=True)
    field = FieldSerializer(read_only=True, many=True)
    grade = GradeSerializer(read_only=True, many=True)
    total_students = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = GenericModelSerializer.Meta.fields + (
            "slug",
            "title",
            "price",
            "discount_price",
            "is_free",
            "status",
            "image",
            "subject",
            "teacher",
            "is_private",
            "category",
            "description",
            "grade",
            "field",
            "total_students",
            "total_sessions",
        )

    def get_total_students(self, obj):
        return obj.users.count()

    def get_total_sessions(self, obj):
        return obj.sessions.count()


class CourseStudentsSerializer(GenericModelSerializer):
    users = StudentListSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "users",
        )


class CourseFeatureSerializer(serializers.Serializer):
    course = serializers.UUIDField()
    text = serializers.ListField(child=serializers.CharField())


class FeaturesSerializer(GenericModelSerializer):
    class Meta:
        model = CourseFeature
        fields = GenericModelSerializer.Meta.fields + ("id", "course", "text")


class CourseFeatureMultiSerializer(serializers.Serializer):
    course = serializers.UUIDField()
    text = serializers.ListField(child=serializers.CharField(max_length=255))

    def create(self, validated_data):
        course_id = validated_data["course"]
        texts = validated_data["text"]
        course = Course.objects.get(id=course_id)
        features = [CourseFeature(course=course, text=item) for item in texts]
        CourseFeature.objects.bulk_create(features)
        return features


class CourseLearningSerializer(GenericModelSerializer):
    class Meta:
        model = CourseLearning
        fields = GenericModelSerializer.Meta.fields + ("id", "course", "text")


class CourseLearningMultiSerializer(serializers.Serializer):
    course = serializers.UUIDField()
    text = serializers.ListField(child=serializers.CharField(max_length=255))

    def create(self, validated_data):
        course_id = validated_data["course"]
        texts = validated_data["text"]
        course = Course.objects.get(id=course_id)
        learnings = [CourseLearning(course=course, text=item) for item in texts]
        CourseLearning.objects.bulk_create(learnings)
        return learnings


class TagSerializer(GenericModelSerializer):
    class Meta:
        model = CourseLearning
        fields = GenericModelSerializer.Meta.fields + ("id", "course", "text")


class CourseTagsMultiSerializer(serializers.Serializer):
    course = serializers.UUIDField()
    text = serializers.ListField(child=serializers.CharField(max_length=255))

    def create(self, validated_data):
        course_id = validated_data["course"]
        texts = validated_data["text"]
        course = Course.objects.get(id=course_id)
        tags = [CourseLearning(course=course, text=item) for item in texts]
        TagCourse.objects.bulk_create(tags)
        return tags


class TagCourseUpdateSerializer(serializers.ModelSerializer):
    text = serializers.ListField(child=serializers.CharField(),write_only=True,required=True)

    class Meta:
        model = TagCourse
        fields = ("course", "text")

    def update(self, instance, validated_data):
        TagCourse.objects.filter(course=instance.course).delete()
        texts = validated_data.get("text", [])
        new_tags = [TagCourse(course=instance.course, text=t) for t in texts]
        TagCourse.objects.bulk_create(new_tags)
        return instance
