from django import forms
from .models import EventOccurenceMember, EventOccurenceMessage, Club
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Submit
)

from crispy_forms.bootstrap import StrictButton


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


class CreateClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'web_url', 'logo_url', 'zip_code', 'private']

    def __init__(self, *args, **kwargs):
        super(CreateClubForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('name', wrapper_class='mb-3', label='Club Name'),
            Field('web_url', wrapper_class='mb-3'),
            Field('logo_url', wrapper_class='mb-3'),
            Field('zip_code', wrapper_class='mb-3'),
            Field('private', wrapper_class='mb-3'),
            StrictButton('Create Club', value='Create Club', type='submit', css_class='btn-outline-primary')
        )

        self.fields['name'].label = 'Club Name'
        self.fields['private'].label = 'Private (membership managed by Admin)'
