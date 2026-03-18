from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    
    external_id = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.full_name