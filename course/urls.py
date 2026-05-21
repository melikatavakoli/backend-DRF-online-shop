from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "course"
router = DefaultRouter()

router.register(r"teacher", views.TeacherViewSet, basename="teacher")
router.register(r"grades", views.GradeViewSet, basename="grade")
router.register(r"fields", views.FieldViewSet, basename="field")
router.register(r"subjects", views.SubjectViewSet, basename="subject")
router.register(r"sessions", views.SessionViewSet, basename="session")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"learnings", views.CourseLearningViewSet, basename="learnings")
router.register(r"features", views.CourseFeatureViewSet, basename="feature")
router.register(r"tags", views.TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions-<uuid:course_id>/",
        views.CourseSessionsAPIView.as_view(),
        name="course-sessions",
    ),
    path(
        "students-<uuid:course_id>/",
        views.CourseStudentsAPIView.as_view(),
        name="course-students",
    ),
    path(
        "update-<uuid:pk>/",
        views.CourseUpdateBySlugAPIView.as_view(),
        name="course-update",
    ),
    path(
        "<slug:slug>/",
        views.CourseDetailBySlugAPIView.as_view(),
        name="course-detail",
    ),
    path("my/", views.MyCoursesAPIView.as_view(), name="my-courses"),
    path("create-features/", views.CourseFeatureMultiCreateAPIView.as_view()),
    path("create-learnings/", views.CourseLearningsMultiCreateAPIView.as_view()),
    path("create-tags/", views.CourseTagMultiCreateAPIView.as_view()),
    path(
        "sessions-progress-<uuid:session_id>/",
        views.UpdateSessionProgressView.as_view(),
        name="update_session_progress",
    ),
    path(
        "session/<slug:slug>/",
        views.SessionDetailBySlugAPIView.as_view(),
        name="session-detail",
    ),
]
