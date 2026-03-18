from django.contrib import admin
from .models import WikiPage


@admin.register(WikiPage)
class WikiPageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
