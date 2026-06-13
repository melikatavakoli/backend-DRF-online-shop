from django.db import models


class GradeChoices(models.IntegerChoices):
    G09 = 9, "9th Grade"
    G10 = 10, "10th Grade"
    G11 = 11, "11th Grade"
    G12 = 12, "12th Grade"
    G13 = 13, "Graduate"


class FieldChoices(models.TextChoices):
    MATH = "M", "Mathematics"
    SCIENCE = "S", "Experimental Sciences"
    HUMANITY = "H", "Humanities"
    NONE = "-", "Middle School"


class EducationChoices(models.IntegerChoices):
    DIPLOMA = 0, "Diploma"
    ASSOCIATE = 1, "Associate Degree"
    BACHELOR = 2, "Bachelor's Degree"
    MASTER = 3, "Master's Degree"
    PHD = 4, "PhD"
