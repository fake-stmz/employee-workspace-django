from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer
from django.contrib.auth.decorators import login_required
from django.db import models


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(email__icontains=search)
            )
        return queryset


@login_required
def client_list(request):
    clients = Client.objects.select_related("manager")

    context = {
        "clients": clients
    }

    return render(request, "clients/client_list.html", context)
