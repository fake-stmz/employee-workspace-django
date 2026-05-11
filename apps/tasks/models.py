from django.db import models
from apps.employees.models import Employee
from apps.clients.models import Client
from apps.core.models import SoftDeletableModel, SoftDeletableManager, AllObjectsManager


class Project(SoftDeletableModel):

    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    manager = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Менеджер"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(SoftDeletableModel):

    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    STATUS_CHOICES = [
        ("new", "Новое"),
        ("progress", "В процессе"),
        ("done", "Выполнено")
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус"
    )

    due_date = models.DateTimeField(null=True, blank=True, verbose_name="До")
    created_at = models.DateTimeField(auto_now_add=True)

    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tasks",
        verbose_name="Ответственный"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Проект"
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Клиент"
    )

    def __str__(self):
        return self.title


class TaskComment(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
