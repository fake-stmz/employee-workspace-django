from django.db import models
from django.utils import timezone


class SoftDeletableModel(models.Model):
    """Абстрактная модель для мягкого удаления"""
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления")

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class SoftDeletableManager(models.Manager):
    """Менеджер, который по умолчанию скрывает удалённые записи"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Менеджер для доступа ко всем записям (включая удалённые)"""
    def get_queryset(self):
        return super().get_queryset()


from django.db import models
from django.utils import timezone


class SyncSettings(models.Model):
    """Настройки синхронизации с 1С"""
    
    employees_url = models.URLField(
        verbose_name="URL сотрудников (XML)", 
        max_length=500, 
        blank=True,
        help_text="Например: https://1c.example.com/hs/exchange/employees/"
    )
    
    clients_url = models.URLField(
        verbose_name="URL клиентов (XML)", 
        max_length=500, 
        blank=True,
        help_text="Например: https://1c.example.com/hs/exchange/clients/"
    )
    
    last_sync_employees = models.DateTimeField(null=True, blank=True, verbose_name="Последняя синхронизация сотрудников")
    last_sync_clients = models.DateTimeField(null=True, blank=True, verbose_name="Последняя синхронизация клиентов")

    class Meta:
        verbose_name = "Настройки синхронизации"
        verbose_name_plural = "Настройки синхронизации"

    def __str__(self):
        return "Настройки синхронизации с 1С"

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings
    