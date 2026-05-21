from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views

app_name = "profiles"

router = DefaultRouter()
router.register(r"student", views.StudentViewSet, basename="student")
router.register(r"consultant", views.ConsultantViewSet, basename="consultant")
router.register(r"students/top", views.TopStudentViewSet, basename="top-students")
router.register(r"specialities", views.SpecialityViewSet, basename="speciality")
router.register(
    r"student-update",
    views.StudentPatchProfileViewSet,
    basename="student_update",
)

urlpatterns = [
    path("", include(router.urls)),
    path("my/", views.ProfileView.as_view(), name="user_profile"),
]
