from django import forms
from django.contrib.auth.models import User

from .models import Task


class AddJobsForm(forms.Form):
    users = forms.ModelMultipleChoiceField(User.objects)
    tasks = forms.ModelMultipleChoiceField(Task.objects.order_by('number'))
