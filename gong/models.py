from django.db import models
from django_extensions.db.models import TimeStampedModel


class Record(TimeStampedModel):
    user = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)