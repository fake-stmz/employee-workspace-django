from django.db import models
from apps.employees.models import Employee
from apps.core.models import SoftDeletableModel, SoftDeletableManager, AllObjectsManager


class WikiPage(SoftDeletableModel):

    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Содержание")

    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
