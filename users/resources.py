from import_export import fields, resources
from users.models import Consultant, Student, TopStudent


class ConsultantResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name="id")
    user = fields.Field(attribute="user", column_name="user")
    education = fields.Field(attribute="education", column_name="education")
    major = fields.Field(attribute="major", column_name="major")
    is_present = fields.Field(attribute="is_present", column_name="is_present")

    class Meta:
        model = Consultant
        fields = ("id", "user", "education", "major", "is_present")
        import_id_fields = ("user",)


class StudentResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name="id")
    user = fields.Field(attribute="user", column_name="user")
    grade = fields.Field(attribute="grade", column_name="grade")
    field = fields.Field(attribute="field", column_name="field")

    class Meta:
        model = Student
        fields = ("id", "user", "grade", "field")
        import_id_fields = ("user",)


class TopStudentResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name="id")
    student = fields.Field(attribute="student", column_name="student")
    field = fields.Field(attribute="field", column_name="field")
    rank = fields.Field(attribute="rank", column_name="rank")
    branch = fields.Field(attribute="branch", column_name="branch")

    class Meta:
        model = TopStudent
        fields = ("id", "student", "field", "rank", "branch")
        import_id_fields = ("student",)
