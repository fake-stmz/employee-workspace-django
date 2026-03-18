from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from django.contrib.auth.decorators import login_required


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


@login_required
def dashboard(request):
    # W.I.P.
    # Пока что просто редирект на список задач
    
    return redirect('task_list')


@login_required
def employee_list(request):
    employees = Employee.objects.all()

    context = {
        "employees": employees
    }

    return render(request, "employees/employee_list.html", context)