from rest_framework import serializers
from .models import WikiPage


class WikiPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiPage
        fields = "__all__"
