from django.db import models


class CourseStatus(models.TextChoices):
    PUBLISHED = "P", "Published"
    DRAFT = "D", "Draft"
    COMMING_SOON = "CS", "Coming_Soon"

class SessionVideoUploadStatus(models.TextChoices):
    INITIATED = "INI", "Initiated"
    UPLOADED = "UP", "Uploaded"
    INGESTING = "ING", "Ingesting"
    PROCESSING = "PR", "Processing"
    READY = "R", "Ready"
    FAILED = "F", "Failed"