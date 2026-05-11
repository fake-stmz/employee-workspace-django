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


class DocumentTemplate(models.Model):
    """
    Шаблон документа с плейсхолдерами вида {{имя_переменной}}.
    Тело (body) хранится как HTML — поддерживает форматирование.
    """

    CATEGORY_CHOICES = [
        ('contract', 'Договор'),
        ('act',      'Акт'),
        ('invoice',  'Счёт'),
        ('letter',   'Письмо'),
        ('report',   'Отчёт'),
        ('other',    'Прочее'),
    ]

    title       = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True,     verbose_name='Описание')
    category    = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Категория',
    )
    body = models.TextField(verbose_name='Тело документа (HTML)')

    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Шаблон документа'
        verbose_name_plural = 'Шаблоны документов'
        ordering            = ['-created_at']

    def __str__(self):
        return self.title
