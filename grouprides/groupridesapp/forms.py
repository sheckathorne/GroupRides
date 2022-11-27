from django import forms
from .models import EventOccurenceMember, EventOccurenceMessage


class DeleteRideRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventOccurenceMember
        fields = []


class CreateRideRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventOccurenceMember
        fields = []


class CreateEventOccurenceMessageForm(forms.ModelForm):
    class Meta:
        model = EventOccurenceMessage
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super(CreateEventOccurenceMessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = ''
