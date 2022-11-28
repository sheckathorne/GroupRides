from django import forms
from .models import EventOccurenceMember, EventOccurenceMessage, Club, ClubMembership, Event, Route
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div
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


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['route'].queryset = Route.objects.filter(created_by=self.user)
        self.fields['club'].queryset = (
            Club.objects.filter(
                pk__in=ClubMembership.objects.filter(
                    user=self.user, membership_type__lte=ClubMembership.MemberType.RideLeader.value)
                .values('club')))
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset('Ride Info',
                     Div(
                         Div(Field('name'), css_class='col-md-4', ),
                         css_class='row',
                     ),
                     Div(
                         Div(Field('route', css_class="w-100", style="height: 38px;"), css_class='col-md-4', ),
                         css_class='row',
                     ),
                     Div(
                         Div(Field('privacy', css_class="w-100", style="height: 38px;"), css_class='col-md-4', ),
                         css_class='row',
                     ),
                     Div(
                         Div(Field('club', css_class="w-100", style="height: 38px;", type="date"), css_class='col-md-4', ),
                         css_class='row',
                     )),
            Fieldset('Pace',
                     Div(
                         Div(
                             Field('group_classification', css_class="w-100", style="height: 38px;"), css_class='col-md-4', ),
                         Div('lower_pace_range', css_class='col-md-4', ),
                         Div('upper_pace_range', css_class='col-md-4', ),
                         css_class='row',
                     ),
                     ))
