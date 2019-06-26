from i18n.models import Internationalizable
from django.db import models

class TestModel(Internationalizable):
    """
    Minimal implementation of a Django model that supports internationalization
    """
    title = models.CharField(max_length=255)
    description = models.TextField()

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
