from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Task, Project, TaskComment
from .serializers import TaskSerializer, ProjectSerializer, TaskCommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee
from apps.documents.models import Document
from django.contrib import messages


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "assigned_to", "project"]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer



@login_required
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
            task = form.save()

            files = request.FILES.getlist('files')
            for file in files:
                Document.objects.create(
                    title=file.name,
                    file=file,
                    task=task,
                    uploaded_by=request.user.employee if hasattr(request.user, 'employee') else None
                )

            messages.success(request, 'Задача успешно создана!')
            return redirect("task_list")
    else:
        form = TaskForm()

    context = {"form": form, "title": "Создать задачу"}
    return render(request, "tasks/task_form.html", context)


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            files = request.FILES.getlist('files')
            for file in files:
                Document.objects.create(
                    title=file.name,
                    file=file,
                    task=task,
                    uploaded_by=request.user.employee if hasattr(request.user, 'employee') else None
                )

            messages.success(request, 'Задача успешно обновлена!')
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    context = {
        "form": form,
        "title": "Редактировать задачу",
        "task": task,
    }
    return render(request, "tasks/task_form.html", context)


@login_required
def task_delete(request, pk):

    task = get_object_or_404(Task.all_objects, pk=pk)

    if request.method == "POST":
        task.soft_delete()
        messages.success(request, f'Задача "{task.title}" перемещена в корзину.')
        return redirect("task_list")
    
    context = {"task": task}
    return render(request, "tasks/task_confirm_delete.html", context)