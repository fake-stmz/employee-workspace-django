from django import forms
from .models import Task

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if isinstance(data, list):
            return data
        return [data] if data else []


class TaskForm(forms.ModelForm):
    files = MultipleFileField(
        required=False,
        label="Прикрепить файлы"
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "assigned_to",
            "project",
            "client",
            "due_date"
        ]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.due_date:
            self.initial['due_date'] = self.instance.due_date.strftime('%Y-%m-%dT%H:%M')

        if self.instance and self.instance.pk:
            self.fields['id'] = forms.CharField(
                initial=self.instance.pk,
                widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control bg-light'}),
                label="ID записи в базе",
                required=False
            )