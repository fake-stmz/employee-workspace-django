from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    manager = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'email', 'manager', 'external_id']