from django.shortcuts import render
from rest_framework import viewsets
from .models import Task, Project, TaskComment
from .serializers import TaskSerializer, ProjectSerializer, TaskCommentSerializer
from django_filters.rest_framework import DjangoFilterBackend


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "assigned_to", "project"]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer



def task_list(request):

    if request.user.groups.filter(name='Менеджер').exists():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to__user=request.user)

    status = request.GET.get("status")
    if status:
        tasks = tasks.filter(status=status)

    context = {
        "tasks": tasks
    }

    return render(request, "tasks/task_list.html", context)