from django import forms
from .models import WikiPage


class WikiPageForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = ["title", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['id'] = forms.CharField(
                initial=self.instance.pk,
                widget=forms.TextInput(attrs={
                    'readonly': True,
                    'class': 'form-control bg-light'
                }),
                label="ID страницы",
                required=False
            )