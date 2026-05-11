from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Task, Project, TaskComment
from .serializers import TaskSerializer, ProjectSerializer, TaskCommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .forms import TaskCommentForm
from .forms import ProjectForm
from django.db.models import Count, Q
from apps.documents.models import Document
from django.contrib import messages
from apps.core.decorators import handle_exceptions


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


@handle_exceptions
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


@handle_exceptions
@login_required
def task_create(request):
    
    # Тест обработки исключений
    #if request.GET.get('test_error'):
    #    raise ValueError("Это тестовая ошибка для проверки сообщений!")
    
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


@handle_exceptions
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            # Удаляем выбранные файлы
            files_to_delete = form.cleaned_data.get('delete_files')
            if files_to_delete:
                for doc in files_to_delete:
                    doc.delete()

            # Добавляем новые файлы
            files = request.FILES.getlist('files')
            for file in files:
                Document.objects.create(
                    title=file.name,
                    file=file,
                    task=task,
                    uploaded_by=request.user.employee if hasattr(request.user, 'employee') else None
                )

            messages.success(request, 'Задача успешно обновлена!')
            return redirect("task_detail", pk=task.pk)

    else:
        form = TaskForm(instance=task)

    context = {
        "form": form,
        "title": "Редактировать задачу",
        "task": task,
    }
    return render(request, "tasks/task_form.html", context)


@handle_exceptions
@login_required
def task_delete(request, pk):

    task = get_object_or_404(Task.all_objects, pk=pk)

    if request.method == "POST":
        task.soft_delete()
        messages.success(request, f'Задача "{task.title}" перемещена в корзину.')
        return redirect("task_list")
    
    context = {"task": task}
    return render(request, "tasks/task_confirm_delete.html", context)


@handle_exceptions
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    documents = task.document_set.all()
    comment_form = TaskCommentForm()
    
    context = {
        "task": task,
        "documents": documents,
        "comment_form": comment_form,
    }
    return render(request, "tasks/task_detail.html", context)


@handle_exceptions
@login_required
def add_task_comment(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == "POST":
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user.employee
            comment.save()
            messages.success(request, "Комментарий добавлен")
            return redirect('task_detail', pk=task.pk)
    
    return redirect('task_detail', pk=task.pk)


@handle_exceptions
@login_required
def project_list(request):
    projects = Project.objects.annotate(
        tasks_count=Count('task'),
        completed_tasks=Count('task', filter=Q(task__status='done'))
    ).order_by('-created_at')

    context = {'projects': projects}
    return render(request, 'projects/project_list.html', context)


@handle_exceptions
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(project=project).select_related('assigned_to', 'client')

    context = {
        'project': project,
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='done').count(),
    }
    return render(request, 'projects/project_detail.html', context)


@handle_exceptions
@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Проект "{project.name}" успешно создан!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    context = {"form": form, "title": "Создать новый проект"}
    return render(request, "projects/project_form.html", context)


@handle_exceptions
@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект "{project.name}" успешно обновлён!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    context = {
        "form": form,
        "title": "Редактировать проект",
        "project": project
    }
    return render(request, "projects/project_form.html", context)


@handle_exceptions
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project.all_objects, pk=pk)

    if request.method == "POST":
        project.soft_delete()
        messages.success(request, f'Проект "{project.name}" перемещён в корзину.')
        return redirect('project_list')
    
    context = {"project": project}
    return render(request, "projects/project_confirm_delete.html", context)