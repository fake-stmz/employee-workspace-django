from rest_framework import serializers
from .models import Task, Project, TaskComment
from apps.employees.serializers import EmployeeSerializer


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer(read_only=True)
    get_status_display = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'status', 
            'get_status_display',
            'due_date', 
            'created_at', 
            'assigned_to', 
            'project', 
            'client'
        ]


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = "__all__"
