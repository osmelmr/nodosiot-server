from django.db import models
from django.utils import timezone


class StatusModel(models.Model):
    """
    Provides logical activation/deactivation.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is active"
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Provides logical deletion instead of physical deletion.
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Is deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deletion date"
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Override delete to perform soft delete.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class BaseModel(
    StatusModel,
    SoftDeleteModel
):
    """
    Base abstract model combining all shared behaviors.
    """
    class Meta:
        abstract = True
