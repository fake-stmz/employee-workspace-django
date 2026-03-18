from django.shortcuts import render
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from django.contrib.auth.decorators import login_required
from apps.tasks.models import Task


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


@login_required
def dashboard(request):

    if request.user.groups.filter(name='Менеджер').exists():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to__email=request.user.email)

    return render(request, 'dashboard.html', {'tasks': tasks})
