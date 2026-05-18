from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from common.paginations import CustomLimitOffsetPagination
from course.filters import CourseFilter
from .models import (
    Course, CourseCategory,
    CourseFeature, CourseLearning,
    Field, Grade, Session,
    SessionProgress, Subject,
    TagCourse, Teacher,
)
from .serializers import (
    CategorySerializer, CourseCreateSerializer, CourseDetailSerializer,
    CourseFeatureSerializer, CourseLearningSerializer, CourseListSerializer, CourseStudentsSerializer,
    CourseUpdateSerializer, FieldSerializer, GradeSerializer, TagSerializer,
    UpdateSessionProgresseSerializer, SessionSerializer, SubjectSerializer, TeacherSerializer,
)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = [
        "course_id",
    ]
    ordering_fields = ["_created_at", "_updated_at"]
    ordering = ["-_created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = CustomLimitOffsetPagination
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = CourseFilter
    ordering_fields = ("_created_at", "_updated_at", "total_students")
    search_fields = (
        "status",
        "subject__title",
        "teacher__full_name",
    )
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Course.objects.select_related(
                "subject",
                "teacher",
            )
            .prefetch_related(
                "grade",
                "field",
                "category",
                "category__session",
                "category__session__progress",
            )
            .annotate(total_students=Count("users"))
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class UpdateSessionProgressView(generics.UpdateAPIView):
    serializer_class = UpdateSessionProgresseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        session_id = self.kwargs["session_id"]
        obj, _created, _restored = SessionProgress.get_or_restore(
            user=self.request.user, session_id=session_id
        )
        return obj


class CourseDetailBySlugAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.prefetch_related(
        "category__session", "grade", "field"
    ).select_related("subject", "teacher")
    lookup_field = "slug"
    serializer_class = CourseDetailSerializer


class CourseUpdateBySlugAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseUpdateSerializer
    lookup_field = "pk"
    parser_classes = (MultiPartParser, FormParser)

    queryset = Course.objects.prefetch_related(
        "category__session", "grade", "field"
    ).select_related("subject", "teacher")


class SessionDetailBySlugAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    lookup_field = "slug"


class CourseSessionsAPIView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        categories = course.category.all()
        sessions = Session.objects.filter(
            session_category__in=categories
        ).order_by("session_no")
        serializer = SessionSerializer(
            sessions, many=True, context={"request": request}
        )
        return Response(serializer.data)


class CourseStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseStudentsSerializer

    def get(self, request, course_id):
        course = get_object_or_404(
            Course.objects.prefetch_related("users"), id=course_id
        )
        serializer = CourseStudentsSerializer(course)
        return Response(serializer.data)


class MyCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseListSerializer

    def get(self, request):
        courses = (
            Course.objects.select_related(
                "subject",
                "teacher",
            )
            .prefetch_related(
                "grade",
                "field",
                "category",
            )
            .filter(users__user=request.user)
            .distinct()
        )
        serializer = CourseListSerializer(
            courses, many=True, context={"request": request}
        )
        return Response(serializer.data)


class CourseFeatureViewSet(viewsets.ModelViewSet):
    # serializer_class = FeaturesSerializer
    queryset = TagCourse.objects.all()
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = [
        "course_id",
    ]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def list(self, request):
        queryset = CourseFeature.objects.all()
        grouped_data = {}
        for obj in queryset:
            course_id = str(obj.course.id)
            if course_id not in grouped_data:
                grouped_data[course_id] = {"course": course_id, "text": []}
            grouped_data[course_id]["text"].append(obj.text)
        result = list(grouped_data.values())
        serializer = CourseFeatureSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="update-text")
    def update_text(self, request):
        course_id = request.data.get("course")
        texts = request.data.get("text", [])
        if not course_id:
            return Response({"detail": "course is required"}, status=400)
        CourseFeature.objects.filter(course_id=course_id).delete()
        new_features = [
            CourseFeature(course_id=course_id, text=t) for t in texts
        ]
        CourseFeature.objects.bulk_create(new_features)
        return Response(
            {"detail": "Course features updated successfully"}, status=200
        )


class CourseFeatureMultiCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CourseFeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Features created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseLearningViewSet(viewsets.ModelViewSet):
    queryset = CourseLearning.objects.all()
    serializer_class = CourseLearningSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = [
        "course_id",
    ]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def list(self, request):
        queryset = CourseLearning.objects.all()
        grouped_data = {}
        for obj in queryset:
            course_id = str(obj.course.id)
            if course_id not in grouped_data:
                grouped_data[course_id] = {"course": course_id, "text": []}
            grouped_data[course_id]["text"].append(obj.text)
        result = list(grouped_data.values())
        serializer = CourseFeatureSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="update-text")
    def update_text(self, request):
        course_id = request.data.get("course")
        texts = request.data.get("text", [])
        if not course_id:
            return Response({"detail": "course is required"}, status=400)
        CourseLearning.objects.filter(course_id=course_id).delete()
        new_learnings = [
            CourseLearning(course_id=course_id, text=t) for t in texts
        ]
        CourseLearning.objects.bulk_create(new_learnings)
        return Response(
            {"detail": "Course learning texts updated successfully"},
            status=200,
        )


class CourseLearningsMultiCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CourseLearningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Learnings created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    queryset = TagCourse.objects.all()
    serializer_class = CourseLearningSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["course_id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def list(self, request):
        queryset = TagCourse.objects.all()
        grouped_data = {}
        for obj in queryset:
            course_id = str(obj.course.id)
            if course_id not in grouped_data:
                grouped_data[course_id] = {"course": course_id, "text": []}
            grouped_data[course_id]["text"].append(obj.text)
        result = list(grouped_data.values())
        serializer = CourseFeatureSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="update-text")
    def update_text(self, request):
        course_id = request.data.get("course_id")
        texts = request.data.get("text", [])
        if not course_id:
            return Response({"detail": "course_id is required"}, status=400)
        TagCourse.objects.filter(course_id=course_id).delete()
        new_tags = [TagCourse(course_id=course_id, text=t) for t in texts]
        TagCourse.objects.bulk_create(new_tags)
        return Response({"detail": "Tags updated successfully"}, status=200)


class CourseTagMultiCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Tags created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
