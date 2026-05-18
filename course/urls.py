from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

app_name = "course"
router = DefaultRouter()

router.register(r"teacher", TeacherViewSet, basename="teacher")
router.register(r"grade", GradeViewSet, basename="grade")
router.register(r"field", FieldViewSet, basename="field")
router.register(r"subject", SubjectViewSet, basename="subject")
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"learnings", CourseLearningViewSet, basename="learnings")
router.register(r"features", CourseFeatureViewSet, basename="feature")
router.register(r"tag", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "course-sessions/<uuid:course_id>/",
        CourseSessionsAPIView.as_view(),
        name="course-sessions",
    ),
    path(
        "courses-students/<uuid:course_id>/",
        CourseStudentsAPIView.as_view(),
        name="course-students",
    ),
    path(
        "courses/update/<uuid:pk>/",
        CourseUpdateBySlugAPIView.as_view(),
        name="course-update",
    ),
    path(
        "courses/<slug:slug>/",
        CourseDetailBySlugAPIView.as_view(),
        name="course-detail",
    ),
    path("my/", MyCoursesAPIView.as_view(), name="my-courses"),
    path("create-features/", CourseFeatureMultiCreateAPIView.as_view()),
    path("create-learnings/", CourseLearningsMultiCreateAPIView.as_view()),
    path("create-tags/", CourseTagMultiCreateAPIView.as_view()),
    path(
        "sessions-progress/<uuid:session_id>/",
        UpdateSessionProgressView.as_view(),
        name="update_session_progress",
    ),
    path(
        "session/<slug:slug>/",
        SessionDetailBySlugAPIView.as_view(),
        name="session-detail",
    ),
]
