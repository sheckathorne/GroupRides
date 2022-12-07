from django import forms
from django.forms import Select, ModelChoiceField

from .models import EventOccurenceMember, EventOccurenceMessage, \
    Club, Event, Route
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div
)
from crispy_forms.bootstrap import StrictButton
from django.utils.html import mark_safe


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


def text_input(field_name, id_name, width=4, margin_bottom=0):
    return Div(Field(field_name, id=f"{id_name}_create_{field_name}"), css_class=f"col-md-{width} mb-{margin_bottom}", )


def dropdown(field_name, id_name, height=38, width=4, margin_bottom=0, onchange=""):
    return Div(
        Field(
            field_name,
            id=f"{id_name}_create_{field_name}",
            css_class="w-100",
            style=f"height: {height}px;",
            onchange=onchange),
        css_class=f"col-md-{width} mb-{margin_bottom}"
    )


def form_row(*args, bottom_margin=3, **kwargs):
    row_id = 'generic-row' if 'row_id' not in kwargs else kwargs['row_id']
    return Div(*args, css_class=f"row mb-{bottom_margin},", id=row_id)


class SelectWithOptionAttribute(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if isinstance(label, dict):
            opt_attrs = label.copy()
            label = opt_attrs.pop('label')
        else:
            opt_attrs = {}

        option_dict = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs)

        for key, val in opt_attrs.items():
            option_dict['attrs'][key] = val

        return option_dict


class RouteChoiceField(ModelChoiceField):
    widget = SelectWithOptionAttribute

    def label_from_instance(self, obj):
        return {
            'label': super().label_from_instance(obj),
            'data-url': obj.url
        }


class CreateEventForm(forms.ModelForm):
    def __init__(self, user_clubs, user_routes, *args, **kwargs):
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['frequency'].label = 'Recurrence'
        self.fields['route'].queryset = user_routes
        self.fields['club'].queryset = user_clubs

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset('Ride Info',
                     form_row(text_input("name", "event"), dropdown("privacy", "event")),
                     form_row(dropdown("route", "event"), dropdown("club", "event")),
                     form_row(text_input("max_riders", "event")),
                     css_class='mt-4'),
            Fieldset('Pace',
                     form_row(
                         dropdown("group_classification", "event")),
                     form_row(
                         text_input("lower_pace_range", "event"),
                         text_input("upper_pace_range", "event")),
                     css_class='mt-4'),
            Fieldset('Date / Time / Recurring',
                     form_row(text_input("start_date", "event"), dropdown("time_zone", "event")),
                     form_row(text_input("end_date", "event"), text_input("ride_time", "event")),
                     form_row(dropdown("frequency", "event")),
                     css_class='mt-4'),
            form_row(
                Div(StrictButton('Create Ride', value="Create Ride", type="submit", css_class="btn-primary w-100"),
                    css_class="col-md-4", ))
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

        field_classes = {
            'route': RouteChoiceField
        }

        help_texts = {
            'route': mark_safe("<a id='route_url_id' href='' target='_blank'>Add</a>")
        }


class CreateRouteForm(forms.ModelForm):
    def __init__(self, user_clubs, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateRouteForm, self).__init__(*args, **kwargs)
        self.fields['start_location_name'].label = 'Start Location Name'
        self.fields['distance'].label = 'Distance (miles)'
        self.fields['elevation'].label = 'Elevation (ft)'
        self.fields['club'].queryset = user_clubs
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset('Route Info',
                     form_row(text_input("name", "route"), text_input("start_location_name", "route")),
                     form_row(text_input("url", "route")),
                     css_class='mt-4'),
            Fieldset('Distance / Elevation',
                     form_row(
                         text_input("distance", "route"),
                         text_input("elevation", "route")),
                     css_class='mt-4'),
            Fieldset('Sharing',
                     form_row(text_input("shared", "route")),
                     form_row(dropdown("club", "route"))),
            form_row(
                Div(StrictButton('Create Route', value="Create Route", type="submit", css_class="btn-primary w-100"),
                    css_class="col-md-4", ))
        )

    def fields_required(self, fields):
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError("This field is required.")
                self.add_error(field, msg)

    def clean(self):
        private = self.cleaned_data.get('shared')
        if private:
            self.fields_required(['club'])

        return self.cleaned_data

    class Meta:
        model = Route
        exclude = ['created_by', 'date_created']
