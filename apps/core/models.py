from django.db import models
from django.utils import timezone
import uuid


class TimeStampedModel(models.Model):
    """
    Provides creation and update timestamps.
    Used for auditability and traceability.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Creation date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last update"
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)


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


class UUIDModel(models.Model):
    """
    Provides a UUID field for public-safe identification.
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        abstract = True


class BaseModel(
    UUIDModel,
    TimeStampedModel,
    StatusModel,
    SoftDeleteModel
):
    """
    Base abstract model combining all shared behaviors.
    """
    class Meta:
        abstract = True
