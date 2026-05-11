from django.shortcuts import render
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from django.contrib.auth.decorators import login_required
from django.db import models
from apps.core.decorators import handle_exceptions
from apps.core.views import sync_from_1c


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

@handle_exceptions
@login_required
def employee_list(request):
    sync_from_1c(request, 'clients')
    
    employees = Employee.objects.all()

    context = {
        "employees": employees
    }

    return render(request, "employees/employee_list.html", context)