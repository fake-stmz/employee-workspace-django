from django.db import models


class Employee(models.Model):
    
    external_id = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name