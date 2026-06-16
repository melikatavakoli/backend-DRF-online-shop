import logging
from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.serializers import GenericModelSerializer
from core.choices import RoleType
from address.models import City, State
from users.models import (
    Consultant,
    Speciality,
    Student,
    TopStudent,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserProfileSerializer(GenericModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    city_lable = serializers.CharField(source="city.title", read_only=True)
    country_lable = serializers.CharField(source="country.title", read_only=True)
    state_lable = serializers.CharField(source="state.title", read_only=True)

    class Meta(GenericModelSerializer.Meta):
        model = User
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "mobile",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "birth_date",
            "age",
            "description",
            "state",
            "state_lable",
            "city",
            "city_lable",
            "country",
            "country_lable",
        )


class UserProfileUpdateSerializer(GenericModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "birth_date",
            "description",
            "state",
            "city",
            "country",
        )


class UserSerializer(GenericModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(read_only=True)
    mobile = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    city = serializers.UUIDField(required=False, allow_null=True)
    state = serializers.UUIDField(required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    state_label = serializers.CharField(source="state.title", read_only=True)
    city_label = serializers.CharField(source="city.title", read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "mobile",
            "email",
            "is_active",
            "is_verified",
            "state_label",
            "city_label",
            "password",
            "state",
            "birth_date",
            "city",
        )

    def validate(self, attrs):
        state_id = attrs.get("state")
        city_id = attrs.get("city")
        if state_id and not State.objects.filter(id=state_id).exists():
            raise serializers.ValidationError({"state": "Invalid state id."})
        if city_id and not City.objects.filter(id=city_id).exists():
            raise serializers.ValidationError({"city": "Invalid city id."})
        return attrs

    def create(self, validated_data):
        validated_data["role"] = RoleType.CONSULTANT
        password = validated_data.pop("password")
        city_id = validated_data.pop("city", None)
        state_id = validated_data.pop("state", None)
        if city_id is not None:
            validated_data["city"] = City.objects.filter(id=city_id).first()
        if state_id is not None:
            validated_data["state"] = State.objects.filter(id=state_id).first()
        user = User.objects.create_user(password=password, **validated_data)
        user.is_verified = True
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop("password", None)
        city_id = validated_data.pop("city", None)
        state_id = validated_data.pop("state", None)
        if city_id is not None:
            instance.city = City.objects.filter(id=city_id).first()
        if state_id is not None:
            instance.state = State.objects.filter(id=state_id).first()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserStudentSerializer(GenericModelSerializer):
    state_label = serializers.CharField(source="state.title", read_only=True)
    city_label = serializers.CharField(source="city.title", read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "mobile",
            "email",
            "is_active",
            "is_verified",
            "state_label",
            "city_label",
            "password",
        )

    def create(self, validated_data):
        validated_data["role"] = RoleType.STUDENT
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        user.is_verified = True
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop("password", None)
        return super().update(instance, validated_data)


class ConsultantWriteSerializer(GenericModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Consultant
        fields = (
            "id",
            "user",
            "specialities",
            "is_present",
            "education",
            "major",
            "description",
        )

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        mobile = user_data.get("mobile")
        user = User.objects.filter(mobile=mobile).first() if mobile else None
        if user:
            if Consultant.objects.filter(user=user).exists():
                raise serializers.ValidationError(
                    "کاربر و مشاور با این شماره موبایل قبلاً ثبت شده‌اند."
                )
            update_data = user_data.copy()
            update_data.pop("mobile", None)
            update_data.pop("password", None)
            user_serializer = UserSerializer(
                instance=user,
                data=update_data,
                partial=True,
            )
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
        else:
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
        specialities = validated_data.pop("specialities", [])
        consultant = Consultant.objects.create(user=user, **validated_data)
        if specialities:
            consultant.specialities.set(specialities)
        return consultant

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            serializer = UserSerializer(
                instance=instance.user, data=user_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        specialities = validated_data.pop("specialities", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if specialities is not None:
            instance.specialities.set(specialities)
        return instance


class SpecialityMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ("id", "title")


class ConsultantDetailSerializer(GenericModelSerializer):
    user = UserProfileSerializer(read_only=True)
    specialities = SpecialityMiniSerializer(many=True, read_only=True)

    class Meta(GenericModelSerializer.Meta):
        model = Consultant
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "user",
            "specialities",
            "is_present",
            "education",
            "major",
            "description",
        )


class ConsultantListSerializer(GenericModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    mobile = serializers.CharField(source="user.mobile")
    specialities = SpecialityMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Consultant
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "full_name",
            "mobile",
            "specialities",
            "is_present",
            "education",
            "major",
        )


class StudentWriteSerializer(GenericModelSerializer):
    user = UserSerializer(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = (
            "id",
            "user",
            "grade",
            "field",
            "description",
        )

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data is None:
            request = self.context.get("request")
            user = getattr(request, "user", None)
            if not user or not user.is_authenticated:
                raise serializers.ValidationError(
                    {"user": "Authenticated user is required."}
                )
        else:
            mobile = user_data.get("mobile")
            user = User.objects.filter(mobile=mobile).first() if mobile else None
            if user:
                if Student.objects.filter(user=user).exists():
                    raise serializers.ValidationError(
                        "کاربر و دانش‌آموز با این شماره موبایل قبلاً ثبت شده‌اند."
                    )
                update_data = user_data.copy()
                update_data.pop("mobile", None)
                update_data.pop("password", None)
                user_serializer = UserSerializer(
                    instance=user,
                    data=update_data,
                    partial=True,
                )
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
            else:
                user_serializer = UserSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
        return Student.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            serializer = UserSerializer(
                instance=instance.user, data=user_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StudentDetailSerializer(GenericModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta(GenericModelSerializer.Meta):
        model = Student
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "user",
            "grade",
            "field",
            "description",
        )


class StudentListSerializer(GenericModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    mobile = serializers.CharField(source="user.mobile")

    class Meta:
        model = Student
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "grade",
            "field",
            "description",
            "full_name",
            "mobile",
        )


class TopStudentSerializer(GenericModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta(GenericModelSerializer.Meta):
        model = TopStudent
        fields = GenericModelSerializer.Meta.fields + (
            "id",
            "student",
            "branch",
            "first_name",
            "last_name",
            "full_name",
            "field",
            "rank",
            "image",
            "description",
            "year",
            "university",
            "uni_accepted_major",
        )


class SpecialitySerializer(GenericModelSerializer):
    class Meta(GenericModelSerializer.Meta):
        model = Speciality
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "description",
        )


class StudentUpdateSerializer(GenericModelSerializer):
    user = UserProfileUpdateSerializer()

    class Meta:
        model = Student
        fields = (
            "grade",
            "field",
            "description",
            "user",
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        files = self.context["request"].FILES
        if "user.profile_picture" in files:
            user_data["profile_picture"] = files["user.profile_picture"]
        user_serializer = UserProfileUpdateSerializer(
            instance=instance.user,
            data=user_data,
            partial=True,
            context=self.context,
        )
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return super().update(instance, validated_data)
