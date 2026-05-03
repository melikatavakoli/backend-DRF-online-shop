import uuid
from functools import cached_property

from django.conf import settings
from django.db import models
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from common.format import common_datetime_str
from common.middleware import get_current_user

from .managers import SoftDeleteManager


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_%(app_label)s_%(class)s_set",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_%(app_label)s_%(class)s_set",
    )

    objects = SoftDeleteManager(alive_only=True)
    all_objects = SoftDeleteManager(alive_only=None)
    deleted_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["id"], name="%(class)s_id_idx")]

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.created_by:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)

    @classmethod
    def get_or_restore(cls, defaults=None, **kwargs):
        instance = cls.all_objects.filter(**kwargs).first()
        if instance:
            restored = False
            if instance.is_deleted:
                instance.restore()
                restored = True
            if defaults:
                for key, value in defaults.items():
                    setattr(instance, key, value)
                instance.save(update_fields=list(defaults.keys()))
            return instance, False, restored
        
        instance, created = cls.objects.get_or_create(defaults=defaults, **kwargs)
        return instance, created, False

    @classmethod
    def update_or_restore(cls, defaults=None, **kwargs):
        instance = cls.all_objects.filter(**kwargs).first()
        if instance:
            restored = False
            if instance.is_deleted:
                instance.restore()
                restored = True
            if defaults:
                for key, value in defaults.items():
                    setattr(instance, key, value)
                instance.save(update_fields=list(defaults.keys()))
            return instance, False, restored
        
        instance, created = cls.objects.update_or_create(defaults=defaults, **kwargs)
        return instance, created, False

    def delete(self, using=None, keep_parents=False):
        if self.is_deleted:
            return
        self._soft_delete_related(using=using)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        if not self.is_deleted:
            return
        
        # Restore related objects
        for rel in self._meta.related_objects:
            if getattr(rel, "on_delete", None) is not models.CASCADE:
                continue
            
            try:
                related = getattr(self, rel.get_accessor_name())
            except Exception:
                continue
            
            if rel.one_to_one:
                try:
                    related.restore()
                except rel.related_model.DoesNotExist:
                    pass
            else:
                for obj in related.all():
                    obj.restore()
        
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def _soft_delete_related(self, using=None):
        for rel in self._meta.related_objects:
            on_delete = getattr(rel, "on_delete", None)
            if on_delete not in (models.CASCADE, models.SET_NULL, models.PROTECT):
                continue
            
            try:
                related = getattr(self, rel.get_accessor_name())
            except Exception:
                continue
            
            if on_delete is models.PROTECT:
                if rel.one_to_one:
                    if related:
                        raise ProtectedError("Cannot delete due to protected objects.", [related])
                elif related.all().exists():
                    raise ProtectedError("Cannot delete due to protected objects.", list(related.all()))
                continue
            
            if on_delete is models.SET_NULL:
                field_name = rel.field.name
                if rel.one_to_one:
                    if related:
                        setattr(related, field_name, None)
                        related.save(using=using, update_fields=[field_name])
                else:
                    related.all().update(**{field_name: None})
                continue
            
            # CASCADE
            if rel.one_to_one:
                try:
                    related.delete(using=using)
                except rel.related_model.DoesNotExist:
                    pass
            else:
                for obj in related.all():
                    obj.delete(using=using)

    @cached_property
    def can_delete(self):
        for rel in self._meta.related_objects:
            try:
                if getattr(self, rel.related_name).all().exists():
                    return False
            except Exception:
                pass
        return True

    @property
    def created_at_display(self):
        return common_datetime_str(self.created_at)

    @property
    def updated_at_display(self):
        return common_datetime_str(self.updated_at)
