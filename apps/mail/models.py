from django.db import models
from apps.employees.models import Employee
from apps.clients.models import Client


class EmailAccount(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    email = models.EmailField()
    imap_server = models.CharField(max_length=255)
    smtp_server = models.CharField(max_length=255)

    def __str__(self):
        return self.email


class EmailMessage(models.Model):

    subject = models.CharField(max_length=255)
    body = models.TextField()

    sender_email = models.EmailField()
    receiver_email = models.EmailField()

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    sent_at = models.DateTimeField()
