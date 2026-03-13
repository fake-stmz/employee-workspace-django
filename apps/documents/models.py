from django.db import models
from apps.employees.models import Employee
from apps.tasks.models import Task


class Document(models.Model):

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
