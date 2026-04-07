from django.shortcuts import render, redirect, get_object_or_404
from apps.tasks.models import Task
from apps.wiki.models import WikiPage
from django.db.models import Count
from django.utils import timezone
import matplotlib.pyplot as plt
import io
import base64
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

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
def deleted_items(request):
    """Корзина удалённых записей (только для менеджеров)"""
    if not request.user.is_superuser:
        return redirect('dashboard')

    deleted_tasks = Task.all_objects.filter(deleted_at__isnull=False)
    deleted_wiki = WikiPage.all_objects.filter(deleted_at__isnull=False)

    context = {
        'deleted_tasks': deleted_tasks,
        'deleted_wiki': deleted_wiki,
    }
    return render(request, 'deleted_items.html', context)


@login_required
def restore_item(request, model_name, pk):
    """Восстановление записи"""
    if not request.user.is_superuser:
        return redirect('dashboard')

    if model_name == 'task':
        item = get_object_or_404(Task.all_objects, pk=pk)
    elif model_name == 'wiki':
        item = get_object_or_404(WikiPage.all_objects, pk=pk)
    else:
        return redirect('deleted_items')

    item.restore()
    messages.success(request, f'Запись успешно восстановлена!')
    return redirect('deleted_items')


@login_required
def permanent_delete(request, model_name, pk):
    """Полное удаление записи из корзины (только для администраторов)"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет прав для полного удаления")

    if model_name == 'task':
        item = get_object_or_404(Task.all_objects, pk=pk)
        item_name = item.title
    elif model_name == 'wiki':
        item = get_object_or_404(WikiPage.all_objects, pk=pk)
        item_name = item.title
    else:
        return redirect('deleted_items')

    if request.method == "POST":
        item.delete()  # Полное удаление из базы
        messages.success(request, f'Запись "{item_name}" полностью удалена.')
        return redirect('deleted_items')

    context = {
        'item': item,
        'model_name': model_name,
        'item_name': item_name,
    }
    return render(request, 'permanent_delete_confirm.html', context)