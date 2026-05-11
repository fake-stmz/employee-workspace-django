import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe
from apps.core.decorators import handle_exceptions
from .models import DocumentTemplate


PLACEHOLDER_RE = re.compile(r'\{\{(\w+)\}\}')


def _extract_placeholders(body: str) -> list[str]:
    """Return unique ordered list of placeholder names found in body."""
    seen = set()
    result = []
    for name in PLACEHOLDER_RE.findall(body):
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _fill_body(body: str, values: dict) -> str:
    """Replace {{name}} with supplied values; unknown keys left as-is."""
    def replacer(m):
        return values.get(m.group(1), m.group(0))
    return PLACEHOLDER_RE.sub(replacer, body)


def _human_label(name: str) -> str:
    """turn_snake_case → Turn Snake Case"""
    return name.replace('_', ' ').capitalize()


@handle_exceptions
@login_required
def template_list(request):
    category = request.GET.get('category', '')
    qs = DocumentTemplate.objects.all()
    if category:
        qs = qs.filter(category=category)

    context = {
        'templates':  qs,
        'categories': DocumentTemplate.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'documents/template_list.html', context)


@handle_exceptions
@login_required
def template_create(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category    = request.POST.get('category', 'other')
        body        = request.POST.get('body', '').strip()

        if not title or not body:
            messages.error(request, 'Название и тело документа обязательны.')
            return render(request, 'documents/template_form.html', {
                'title':       'Новый шаблон',
                'post':        request.POST,
                'categories':  DocumentTemplate.CATEGORY_CHOICES,
            })

        employee = getattr(request.user, 'employee', None)
        tpl = DocumentTemplate.objects.create(
            title=title,
            description=description,
            category=category,
            body=body,
            created_by=employee,
        )
        messages.success(request, f'Шаблон «{tpl.title}» создан.')
        return redirect('template_detail', pk=tpl.pk)

    return render(request, 'documents/template_form.html', {
        'title':      'Новый шаблон',
        'categories': DocumentTemplate.CATEGORY_CHOICES,
    })


@handle_exceptions
@login_required
def template_update(request, pk):
    tpl = get_object_or_404(DocumentTemplate, pk=pk)

    if request.method == 'POST':
        tpl.title       = request.POST.get('title', tpl.title).strip()
        tpl.description = request.POST.get('description', '').strip()
        tpl.category    = request.POST.get('category', tpl.category)
        tpl.body        = request.POST.get('body', tpl.body).strip()

        if not tpl.title or not tpl.body:
            messages.error(request, 'Название и тело документа обязательны.')
        else:
            tpl.save()
            messages.success(request, f'Шаблон «{tpl.title}» обновлён.')
            return redirect('template_detail', pk=tpl.pk)

    return render(request, 'documents/template_form.html', {
        'title':      f'Редактировать: {tpl.title}',
        'tpl':        tpl,
        'categories': DocumentTemplate.CATEGORY_CHOICES,
    })


@handle_exceptions
@login_required
def template_detail(request, pk):
    tpl = get_object_or_404(DocumentTemplate, pk=pk)
    placeholders = [
        {'name': n, 'label': _human_label(n)}
        for n in _extract_placeholders(tpl.body)
    ]
    context = {
        'tpl':          tpl,
        'placeholders': placeholders,
    }
    return render(request, 'documents/template_detail.html', context)


@handle_exceptions
@login_required
def template_delete(request, pk):
    tpl = get_object_or_404(DocumentTemplate, pk=pk)
    if request.method == 'POST':
        name = tpl.title
        tpl.delete()
        messages.success(request, f'Шаблон «{name}» удалён.')
        return redirect('template_list')
    return render(request, 'documents/template_confirm_delete.html', {'tpl': tpl})


@handle_exceptions
@login_required
def template_fill(request, pk):
    tpl = get_object_or_404(DocumentTemplate, pk=pk)
    placeholders = [
        {'name': n, 'label': _human_label(n)}
        for n in _extract_placeholders(tpl.body)
    ]

    if request.method == 'POST':
        values = {p['name']: request.POST.get(p['name'], '') for p in placeholders}
        filled_body = mark_safe(_fill_body(tpl.body, values))
        return render(request, 'documents/template_print.html', {
            'tpl':         tpl,
            'filled_body': filled_body,
            'values':      values,
        })

    context = {
        'tpl':          tpl,
        'placeholders': placeholders,
    }
    return render(request, 'documents/template_fill.html', context)
