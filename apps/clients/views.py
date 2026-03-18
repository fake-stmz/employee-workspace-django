from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer
from django.contrib.auth.decorators import login_required


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


@login_required
def client_list(request):
    clients = Client.objects.select_related("manager")

    context = {
        "clients": clients
    }

    return render(request, "clients/client_list.html", context)
