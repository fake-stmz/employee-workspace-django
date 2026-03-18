from django.contrib import admin
from .models import EmailAccount, EmailMessage


@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "employee")


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "sender_email", "receiver_email", "sent_at")
