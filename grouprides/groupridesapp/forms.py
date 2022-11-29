from django import forms
from .models import EventOccurenceMember, EventOccurenceMessage, Club, ClubMembership, Event, Route
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div
)

from django.forms.widgets import SelectDateWidget

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


def text_input(field_name, width=4):
    return Div(Field(field_name, id=f"event_create_{field_name}"), css_class=f"col-md-{width}", )


def dropdown(field_name, height=38, width=4):
    return Div(Field(
        field_name,
        id=f"event_create_{field_name}",
        css_class="w-100",
        style=f"height: {height}px;"),
        css_class=f"col-md-{width}"
    )


def form_row(*args, margin=3):
    return Div(*args, css_class=f"row mb-{margin}")


class CreateEventForm(forms.ModelForm):
    def __init__(self, user, user_clubs, user_routes, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['frequency'].label = 'Recurrence'
        self.fields['route'].queryset = user_routes
        self.fields['club'].queryset = user_clubs

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset('Ride Info',
                     form_row(text_input("name"), dropdown("privacy")),
                     form_row(dropdown("route"), dropdown("club")),
                     form_row(text_input("max_riders")),
                     css_class='mt-4'),
            Fieldset('Pace',
                     form_row(
                         dropdown("group_classification")),
                     form_row(
                         text_input("lower_pace_range"),
                         text_input("upper_pace_range")),
                     css_class='mt-4'),
            Fieldset('Date / Time / Recurring',
                     form_row(text_input("start_date"), dropdown("time_zone")),
                     form_row(text_input("end_date"), text_input("ride_time")),
                     form_row(dropdown("frequency")),
                     css_class='mt-4'),
            StrictButton(
                'Create Ride',
                value='Create Ride',
                type='submit',
                css_class='btn-outline-primary mb-4 col-md-4 w-100')
        )

    def fields_required(self, fields):
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError("This field is required.")
                self.add_error(field, msg)

    def clean(self):
        private = self.cleaned_data.get('privacy')

        if private == Event.EventMemberType.Members:
            self.fields_required(['club'])

        return self.cleaned_data

    class Meta:
        model = Event
        exclude = ['created_by']

        widgets = {
            'start_date': forms.DateInput(
                format='%-m/%-d/%Y',
                attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'end_date': forms.DateInput(
                format='%-m/%-d/%Y',
                attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'ride_time': forms.TimeInput(
                format='%-I:%M %p',
                attrs={'class': 'form-control', 'placeholder': 'Select a time', 'type': 'time'}
            )
        }
