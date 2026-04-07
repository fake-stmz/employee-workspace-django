from rest_framework import serializers
from .models import WikiPage
from apps.employees.serializers import EmployeeSerializer


class WikiPageSerializer(serializers.ModelSerializer):
    author = EmployeeSerializer(read_only=True)
    class Meta:
        model = WikiPage
        fields = ['id', 'title', 'content', 'author', 'created_at']
