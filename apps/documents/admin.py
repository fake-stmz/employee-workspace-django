from django.contrib import admin
from .models import Document, DocumentTemplate


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_by", "created_at")


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display  = ("id", "title", "category", "created_by", "created_at", "updated_at")
    list_filter   = ("category",)
    search_fields = ("title", "description")
