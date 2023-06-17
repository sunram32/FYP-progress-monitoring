from django.forms import DateInput, ModelForm, TextInput, Textarea, TimeInput, FileInput, URLInput
from django import forms
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class NewMeetingRecordForm(ModelForm):
    class Meta:
        model = MeetingRecord
        fields = ['date', 'time', 'updates_from_previous_meeting', 'items_discussed_this_meeting', 'work_for_coming_meeting']
        widgets = {
            'date': DateInput(attrs={
                'class': "form-control mb-3"
            }),
            'time': TimeInput(attrs={
                'class': "form-control mb-3"
            }),
            'updates_from_previous_meeting': Textarea(attrs={
                'class': "form-control mb-3",
                'rows': 5
            }),
            'items_discussed_this_meeting': Textarea(attrs={
                'class': "form-control mb-3",
                'rows': 5
            }),
            'work_for_coming_meeting': Textarea(attrs={
                'class': "form-control mb-3",
                'rows': 5
            }),
        }

class NewTaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'category', 'start_date', 'due_date', 'description']
        widgets = {
            'title': TextInput(attrs={
                'class': "form-control mb-3"
            }),
            'category': TextInput(attrs={
                'class': "form-control mb-3"
            }),
            'start_date': DateInput(attrs={
                'class': "form-control mb-3"
            }),
            'due_date': DateInput(attrs={
                'class': "form-control mb-3"
            }),
            'description': TextInput(attrs={
                'class': "form-control mb-3"
            }),
        }

class NewResourceForm(ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'category', 'description', 'file_name', 'file_URL']
        widgets = {
            'title': TextInput(attrs={
                'class': "form-control mb-3"
            }),
            'category': TextInput(attrs={
                'class': "form-control mb-3"
            }),
            'description': TextInput(attrs={
                'class': "form-control mb-3"
            }),
            'file_name': FileInput(attrs={
                'class': "form-control mb-3"
            }),
            'file_URL': URLInput(attrs={
                'class': "form-control mb-3"
            }),
        }