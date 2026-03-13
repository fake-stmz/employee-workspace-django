from django.db import models
from apps.employees.models import Employee


class Client(models.Model):

    external_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True)

    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="clients"
    )

    def __str__(self):
        return self.name
