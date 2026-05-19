from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from rest_framework import generics,viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from common.paginations import CustomLimitOffsetPagination
from users.exports import export_students_to_excel
from users.filters import ConsultantFilterSet
from users.models import (
    Consultant,
    Speciality,
    Student,
    TopStudent,
)
from users.serializers import (
    ConsultantDetailSerializer,
    ConsultantListSerializer,
    ConsultantWriteSerializer,
    SpecialitySerializer,
    StudentDetailSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
    StudentWriteSerializer,
    TopStudentSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)
from core.types import RoleType


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.role == RoleType.STUDENT:
            student = Student.objects.filter(user=user).first()
            if student:
                return Response(StudentDetailSerializer(student).data)
        if user.role == RoleType.CONSULTANT:
            consultant = Consultant.objects.filter(user=user).first()
            if consultant:
                return Response(ConsultantDetailSerializer(consultant).data)
        return Response({"user": UserProfileSerializer(user).data})

    @extend_schema(
        request=PolymorphicProxySerializer(
            component_name="ProfileMyPatchRequest",
            serializers=[
                UserProfileUpdateSerializer,
                StudentWriteSerializer,
                ConsultantWriteSerializer,
            ],
            resource_type_field_name=None,
        ),
        responses=PolymorphicProxySerializer(
            component_name="ProfileMyPatchResponse",
            serializers=[
                UserProfileSerializer,
                StudentDetailSerializer,
                ConsultantDetailSerializer,
            ],
            resource_type_field_name=None,
        ),
    )
    
    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        user_fields = {
            "first_name",
            "last_name",
            "birth_date",
            "state",
            "city",
            "country",
        }
        user_data = {}
        for field in user_fields:
            if field in data:
                user_data[field] = data.get(field)
                data.pop(field, None)

        if user_data:
            user_serializer = UserProfileUpdateSerializer(
                instance=user,
                data=user_data,
                partial=True,
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        if user.role == RoleType.STUDENT:
            student, _, _ = Student.get_or_restore(user=user)
            student_serializer = StudentWriteSerializer(
                instance=student,
                data=data,
                partial=True,
            )
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()
            return Response(StudentDetailSerializer(student_serializer.instance).data)
        if user.role == RoleType.CONSULTANT:
            consultant, _, _ = Consultant.get_or_restore(user=user)
            consultant_serializer = ConsultantWriteSerializer(
                instance=consultant,
                data=data,
                partial=True,
            )
            consultant_serializer.is_valid(raise_exception=True)
            consultant_serializer.save()
            return Response(
                ConsultantDetailSerializer(consultant_serializer.instance).data
            )
        if data:
            serializer = UserProfileUpdateSerializer(
                instance=user,
                data=data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return self.retrieve(request, *args, **kwargs)


class ConsultantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Consultant.objects.all()
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConsultantFilterSet
    search_fields = ("user__first_name","user__last_name","user__mobile","user__email","description",)
    ordering_fields = ("_created_at", "_updated_at")
    ordering = ("-_updated_at",)

    def get_serializer_class(self):
        if self.action == "list":
            return ConsultantListSerializer
        if self.action == "retrieve":
            return ConsultantDetailSerializer
        return ConsultantWriteSerializer


class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("grade", "field", "user__city", "user__state", "_created_by")
    search_fields = ("user__first_name", "user__last_name", "user__mobile")
    ordering_fields = ("_created_at","_updated_at","user__first_name","user__last_name",)
    ordering = ("-_updated_at",)
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentWriteSerializer


class TopStudentViewSet(viewsets.ModelViewSet):
    queryset = TopStudent.objects.all()
    serializer_class = TopStudentSerializer
    pagination_class = CustomLimitOffsetPagination
    filterset_fields = ("field", "branch")
    search_fields = ("student__user__first_name","student__user__last_name","first_name","last_name",)
    ordering = ("-_created_at",)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]


class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]


class StudentPatchProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class StudentExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Student.objects.select_related("user").all()
        excel_file = export_students_to_excel(queryset)
        response = HttpResponse(
            excel_file,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="students-report.xlsx"'
        return response
