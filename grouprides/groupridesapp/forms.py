from django import forms
from .models import EventOccurenceMember


class DeleteRideRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventOccurenceMember
        fields = []


class CreateRideRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventOccurenceMember
        fields = []