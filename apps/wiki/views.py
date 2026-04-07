from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WikiPage
from .forms import WikiPageForm
from django.db import models
from rest_framework import viewsets
from .serializers import WikiPageSerializer
from django.contrib import messages


class WikiViewSet(viewsets.ModelViewSet):
    queryset = WikiPage.objects.all()
    serializer_class = WikiPageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(content__icontains=search)
            )
        return queryset.order_by('-created_at')


@login_required
def wiki_list(request):
    pages = WikiPage.objects.all().order_by("-created_at")

    context = {
        "pages": pages
    }

    return render(request, "wiki/wiki_list.html", context)


@login_required
def wiki_page_view(request, pk):

    page = get_object_or_404(WikiPage, pk=pk)

    context = {
        "page": page
    }

    return render(request, "wiki/wiki_page.html", context)


@login_required
def wiki_create(request):

    if request.method == "POST":
        form = WikiPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user.employee
            page.save()
            messages.success(request, 'Вики страница успешно создана!')
            return redirect("wiki_list")
    else:
        form = WikiPageForm()

    context = {
        "form": form,
        "title": "Создать страницу"
    }

    return render(request, "wiki/wiki_form.html", context)


@login_required
def wiki_update(request, pk):

    page = get_object_or_404(WikiPage, pk=pk)

    if request.method == "POST":
        form = WikiPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вики страница успешно обновлена!')
            return redirect("wiki_list")
    else:
        form = WikiPageForm(instance=page)

    context = {
        "form": form,
        "title": "Редактировать страницу"
    }

    return render(request, "wiki/wiki_form.html", context)


@login_required
def wiki_delete(request, pk):

    page = get_object_or_404(WikiPage.all_objects, pk=pk)

    if request.method == "POST":
        page.soft_delete()
        messages.success(request, f'Страница "{page.title}" перемещена в корзину.')
        return redirect("wiki_list")
    
    context = {"page": page}
    return render(request, "wiki/wiki_confirm_delete.html", context)