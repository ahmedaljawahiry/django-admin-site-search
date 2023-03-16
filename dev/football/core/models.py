from django.db import models


class BaseModel(models.Model):
    """Adds base fields for all models"""

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["created_at"]
        abstract = True
