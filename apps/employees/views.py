from django.shortcuts import render
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from django.contrib.auth.decorators import login_required
from apps.tasks.models import Task
from django.db.models import Count
from django.utils import timezone
import matplotlib.pyplot as plt
import io
import base64
from django.db import models


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) | 
                models.Q(email__icontains=search)
            )
        return queryset


@login_required
def dashboard(request):
    now = timezone.now()
    
    # Основная статистика
    total_tasks = Task.objects.count()
    my_tasks = Task.objects.filter(assigned_to__user=request.user).count()
    completed_tasks = Task.objects.filter(status='done').count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['new', 'progress']
    ).count()

    recent_tasks = Task.objects.select_related('assigned_to', 'project').order_by('-created_at')[:6]

    # Генерация графика Matplotlib
    status_data = Task.objects.values('status').annotate(count=Count('id'))
    
    status_dict = {'new': 0, 'progress': 0, 'done': 0}
    for item in status_data:
        status_dict[item['status']] = item['count']

    labels = ['Новое', 'В процессе', 'Выполнено']
    values = [status_dict['new'], status_dict['progress'], status_dict['done']]
    colors = ['#0d6efd', '#ffc107', '#198754']

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    ax.set_title('Задачи по статусам', fontsize=14, pad=20)

    # Сохраняем график в base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    chart_base64 = base64.b64encode(image_png).decode('utf-8')
    chart_url = f"data:image/png;base64,{chart_base64}"

    context = {
        'total_tasks': total_tasks,
        'my_tasks': my_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'chart_url': chart_url,
        'now': now,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def employee_list(request):
    employees = Employee.objects.all()

    context = {
        "employees": employees
    }

    return render(request, "employees/employee_list.html", context)