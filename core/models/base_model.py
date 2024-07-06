from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_by = models.CharField(null=True)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    updated_by = models.CharField(null=True)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.CharField(null=True)

    class Meta:
        abstract = True
