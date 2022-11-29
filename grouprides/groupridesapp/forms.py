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
    return Div(Field(field_name), css_class=f"col-md-{width}", )


def dropdown(field_name, height=38, width=4):
    return Div(Field(field_name, css_class="w-100", style=f"height: {height}px;"), css_class=f"col-md-{width}", )


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            'start_date': forms.DateInput(
                format='%m/%d/%Y',
                attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'end_date': forms.DateInput(
                format='%m/%d/%Y',
                attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'ride_time': forms.TimeInput(
                format='%-I:%M %p',
                attrs={'class': 'form-control', 'placeholder': 'Select a time', 'type': 'time'}
            )
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['frequency'].label = 'Recurrence'
        self.fields['route'].queryset = Route.objects.filter(created_by=self.user)
        self.fields['club'].queryset = (
            Club.objects.filter(
                pk__in=ClubMembership.objects.filter(
                    user=self.user, membership_type__lte=ClubMembership.MemberType.RideLeader.value)
                .values('club')))

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset('Ride Info',
                     Div(text_input("name"), dropdown("club"), css_class='row mb-3'),
                     Div(dropdown("route"), dropdown("privacy"), css_class='row mb-3', ),
                     Div(text_input("max_riders"), css_class='row mb-3', ),
                     css_class='mt-4'),
            Fieldset('Pace', Div(
                dropdown("group_classification"),
                text_input("lower_pace_range"),
                text_input("upper_pace_range"),
                css_class='row mb-3', ),
                     css_class='mt-4'),
            Fieldset('Date / Time / Recurring', Div(
                text_input("start_date"),
                dropdown("time_zone"),
                css_class='row mb-3', ), Div(
                text_input("end_date"),
                text_input("ride_time"),
                css_class='row mb-3', ), Div(
                dropdown("frequency"),
                css_class='row mb-3', ),
                     css_class='mt-4'),
        )
