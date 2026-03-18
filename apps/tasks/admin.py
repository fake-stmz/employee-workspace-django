from django.contrib import admin
from .models import Task, Project, TaskComment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manager", "created_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "assigned_to", "due_date")
    list_filter = ("status",)
    search_fields = ("title",)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
