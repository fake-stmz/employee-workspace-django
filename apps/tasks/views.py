from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Task, Project, TaskComment
from .serializers import TaskSerializer, ProjectSerializer, TaskCommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee


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


@login_required
def task_create(request):

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm()
        
        if not request.user.groups.filter(name='Manager').exists():
            form.fields['assigned_to'].queryset = Employee.objects.filter(user=request.user)
        
    context = {
        "form": form,
        "title": "Создать задачу"
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_update(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)
        
        if not request.user.groups.filter(name='Manager').exists():
            form.fields['assigned_to'].queryset = Employee.objects.filter(user=request.user)

    context = {
        "form": form,
        "title": "Редактировать задачу"
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_delete(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    
    context = {
        "task": task
    }

    return render(request, "tasks/task_confirm_delete.html", context)