from django.shortcuts import render, redirect, get_object_or_404
from apps.tasks.models import Task, Project
from apps.wiki.models import WikiPage
from django.db.models import Count
from django.utils import timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .decorators import handle_exceptions
import requests
import xml.etree.ElementTree as ET
from apps.employees.models import Employee
from apps.clients.models import Client
from .models import SyncSettings


#@handle_exceptions
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

    if sum(values) > 0:
        ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 12}
        )
    else:
        ax.text(
            0.5,
            0.5,
            'Нет данных',
            ha='center',
            va='center',
            fontsize=14
        )
        ax.axis('off')

    ax.set_title('Задачи по статусам', fontsize=14, pad=20)

    # Сохраняем график в base64
    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format='png',
        dpi=120,
        bbox_inches='tight'
    )

    plt.close(fig)
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


@handle_exceptions
@login_required
def deleted_items(request):
    """Корзина удалённых записей (только для менеджеров)"""
    if not request.user.is_superuser:
        return redirect('dashboard')

    deleted_tasks = Task.all_objects.filter(deleted_at__isnull=False)
    deleted_wiki = WikiPage.all_objects.filter(deleted_at__isnull=False)
    deleted_projects = Project.all_objects.filter(deleted_at__isnull=False)

    context = {
        'deleted_tasks': deleted_tasks,
        'deleted_wiki': deleted_wiki,
        'deleted_projects': deleted_projects,
    }
    return render(request, 'deleted_items.html', context)


@handle_exceptions
@login_required
def restore_item(request, model_name, pk):
    """Восстановление записи"""
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    if model_name == 'task':
        item = get_object_or_404(Task.all_objects, pk=pk)
    elif model_name == 'wiki':
        item = get_object_or_404(WikiPage.all_objects, pk=pk)
    elif model_name == 'project':
        item = get_object_or_404(Project.all_objects, pk=pk)
    else:
        return redirect('deleted_items')

    item.restore()
    messages.success(request, f'Запись успешно восстановлена!')
    return redirect('deleted_items')


@handle_exceptions
@login_required
def permanent_delete(request, model_name, pk):
    """Полное удаление записи из корзины (только для администраторов)"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет прав для полного удаления")

    if model_name == 'task':
        item = get_object_or_404(Task.all_objects, pk=pk)
    elif model_name == 'wiki':
        item = get_object_or_404(WikiPage.all_objects, pk=pk)
    elif model_name == 'project':
        item = get_object_or_404(Project.all_objects, pk=pk)
    else:
        return redirect('deleted_items')

    if request.method == "POST":
        item_name = item.name if model_name == 'project' else item.title
        item.delete()
        messages.success(request, f'Запись "{item_name}" была полностью удалена навсегда.')
        return redirect('deleted_items')

    # Если вдруг GET — просто редирект (на всякий случай)
    return redirect('deleted_items')


def parse_and_sync_employees(xml_content):
    root = ET.fromstring(xml_content)
    created = updated = 0

    for item in root.findall('.//Employee') or root.findall('.//Сотрудник'):
        # Безопасное получение текста
        def get_text(tag_names):
            for tag in tag_names:
                elem = item.find(tag)
                if elem is not None and elem.text:
                    return elem.text.strip()
            return None

        external_id = get_text(['ExternalID', 'ИД', 'Id'])
        full_name   = get_text(['FullName', 'ФИО', 'Name'])
        email       = get_text(['Email', 'Почта', 'email'])
        position    = get_text(['Position', 'Должность']) or ''
        department  = get_text(['Department', 'Подразделение']) or ''

        if not full_name or not email:
            continue

        _, created_flag = Employee.objects.update_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'position': position,
                'department': department,
                'external_id': external_id,
            }
        )
        if created_flag:
            created += 1
        else:
            updated += 1

    return created, updated


def parse_and_sync_clients(xml_content):
    root = ET.fromstring(xml_content)
    created = updated = 0

    for item in root.findall('.//Client') or root.findall('.//Клиент'):
        def get_text(tag_names):
            for tag in tag_names:
                elem = item.find(tag)
                if elem is not None and elem.text:
                    return elem.text.strip()
            return None

        external_id = get_text(['ExternalID', 'ИД', 'Id'])
        name        = get_text(['Name', 'Наименование'])
        phone       = get_text(['Phone', 'Телефон']) or ''
        email       = get_text(['Email', 'Почта', 'email']) or ''

        if not name:
            continue

        _, created_flag = Client.objects.update_or_create(
            name=name,
            defaults={
                'external_id': external_id,
                'phone': phone,
                'email': email,
            }
        )
        if created_flag:
            created += 1
        else:
            updated += 1

    return created, updated


def sync_from_1c(request, entity_type):
    settings = SyncSettings.get_settings()
    
    if entity_type == 'employees':
        url = settings.employees_url
        success_msg = "Сотрудники"
    else:
        url = settings.clients_url
        success_msg = "Клиенты"

    if not url:
        messages.warning(request, f"URL для {success_msg.lower()} не настроен!")
        return

    try:
        response = requests.get(url, timeout=20)
        response.encoding = 'utf-8'
        response.raise_for_status()
        xml_content = response.text

        if entity_type == 'employees':
            c, u = parse_and_sync_employees(xml_content)
            settings.last_sync_employees = timezone.now()
        else:
            c, u = parse_and_sync_clients(xml_content)
            settings.last_sync_clients = timezone.now()

        settings.save()

    except Exception as e:
        messages.error(request, f"Ошибка синхронизации: {e}")

@handle_exceptions
@login_required
def settings_view(request):
    
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    settings = SyncSettings.get_settings()

    if request.method == 'POST':
        settings.employees_url = request.POST.get('employees_url', '').strip()
        settings.clients_url = request.POST.get('clients_url', '').strip()
        settings.save()
        messages.success(request, "Настройки успешно сохранены.")
        return redirect('settings')

    context = {
        'settings': settings,
        'page_title': 'Настройки'
    }
    return render(request, 'settings.html', context)