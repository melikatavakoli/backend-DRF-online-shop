import uuid
from import_export import resources, fields
from django.utils.timezone import now

class BaseModelResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        if 'id' not in row or not row['id']:
            row['id'] = str(uuid.uuid4())
        row.setdefault('active', True)
        row.setdefault('created_by', None)
        row.setdefault('_updated_by', None)
        row.setdefault('created_at', now())
        row.setdefault('updated_at', now())
        super().before_import_row(row, **kwargs)
