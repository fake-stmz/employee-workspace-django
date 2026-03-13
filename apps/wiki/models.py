from django.db import models
from apps.employees.models import Employee


class WikiPage(models.Model):

    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
