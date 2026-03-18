from django import forms
from .models import WikiPage


class WikiPageForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = ["title", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10})
        }
