import datetime

import pytz
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Select, ModelChoiceField
from image_uploader_widget.widgets import ImageUploaderWidget
from tinymce.widgets import TinyMCE

from .models import EventOccurenceMember, EventOccurenceMessage, \
    Club, Event, Route, ClubMembership, ClubMembershipRequest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div
)
from crispy_forms.bootstrap import StrictButton, InlineCheckboxes
from django.utils.html import mark_safe
from .utils import css_container, text_input, dropdown, form_row, base_input_style


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
        super().__init__(*args, **kwargs)
        self.fields['message'].label = ''
        self.helper = FormHelper(self)
        self.helper.css_container = css_container()
        self.helper.layout = Layout(
            form_row(
                Field("message", wrapper_class="col-span-12 shadow-lg"),
                padding_bottom="pb-4"),
            Div(
                StrictButton('Add Comment', value="Add", type="submit",
                             css_class=f"w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 "
                                       f"rounded shadow-lg mb-4"),
            ),
        )


class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['membership_expires', 'active', 'membership_type']

        widgets = {
            'membership_expires': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.club_id = kwargs.pop('club_id', None)
        self.membership_request_id = kwargs.pop('membership_request_id', None)
        member = kwargs.get('instance', None)
        member_dropdown_disabled = False

        if member:
            member_dropdown_disabled = (member.membership_type == ClubMembership.MemberType.Creator.value)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.css_container = css_container()
        self.helper.layout = Layout(
            form_row(
                dropdown("membership_type", "member", width="col-span-12"), padding_bottom="pb-4"),
            form_row(Div(Field("membership_expires", id=f"member_create_membership_expires"),
                         css_class=f"md:col-span-12", ), padding_bottom="pb-4"),
            form_row(Div(Field("active", wrapper_class="flex flex-row items-center", css_class="ml-4"),
                         css_class="col-span-12 mb-1"),
                     padding_bottom="pb-4"),
            Div(
                StrictButton('Confirm', value="Confirm", type="submit",
                             css_class=f"w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 "
                                       f"rounded shadow-lg mb-4"),

                css_class="modal-footer"
            ),
        )

        info_icon = f"<button data-popover-target='membership-popover' data-popover-placement='bottom' " \
                    f"data-popover-trigger='click' type='button'><i class='fa-solid fa-circle-info'></i></button>"

        membership_type_label = self.fields['membership_type'].label + " "

        self.fields['membership_type'].label = membership_type_label + info_icon
        self.fields['membership_type'].disabled = member_dropdown_disabled
        self.fields['membership_expires'].disabled = member_dropdown_disabled
        self.fields["active"].disabled = member_dropdown_disabled

        # When approving join rquest, set initial values in form.
        if self.membership_request_id:
            self.fields['membership_type'].initial = ClubMembership.MemberType.PaidMember
            self.fields['membership_expires'].initial = datetime.date.today() + datetime.timedelta(weeks=52)
            self.fields["active"].initial = True

    def clean(self):
        data = super().clean()
        requestor_membership = ClubMembership.objects.get(user=self.user, club=self.club_id)
        requestor_role = requestor_membership.membership_type
        new_role_type = data['membership_type']
        creator_role_type = ClubMembership.MemberType.Creator.value

        # When approving join request, set the approver details when the form is submitted
        if self.membership_request_id:
            tz = pytz.timezone("America/Chicago")
            membership_request = ClubMembershipRequest.objects.get(pk=self.membership_request_id)
            membership_request.status = ClubMembershipRequest.RequestStatus.Approved
            membership_request.responder = self.user
            membership_request.response_date = datetime.datetime.now(tz)
            membership_request.save()

        if new_role_type == creator_role_type and requestor_role > creator_role_type:
            raise ValidationError(
                "Only creators can promote others to the \'creator\' role."
            )


class CreateClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ["name", "description", "web_url", "logo", "zip_code", "private"]

        widgets = {
            'logo': ImageUploaderWidget(),
        }

    def __init__(self, *args, **kwargs):
        width = "xl:col-span-4 lg:col-span-6 md:col-span-8 col-span-12"
        row_padding = "pb-2"

        super(CreateClubForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.css_container = css_container()
        self.helper.layout = Layout(
            form_row(text_input("name", "club", label='Club Name', width=width), padding_bottom=row_padding),
            form_row(Field("description", wrapper_class=width + " shadow-lg"), padding_bottom=row_padding),
            form_row(text_input("web_url", "club", width=width), padding_bottom=row_padding),
            form_row(Field("logo", wrapper_class=width + " shadow-lg"), padding_bottom=row_padding),
            form_row(text_input("zip_code", "club", width=width), padding_bottom=row_padding),
            form_row(Field('private', wrapper_class='mb-3'), padding_bottom=row_padding),
            form_row(
                Div(StrictButton('Create Club', value="Create Club", type="submit",
                                 css_class="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 "
                                           "rounded shadow-lg mb-4"),
                    css_class=width,))
        )

        self.fields['name'].label = 'Club Name'
        self.fields['private'].label = 'Private (membership managed by Admin)'


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
    widget = SelectWithOptionAttribute(attrs={"class": base_input_style()})

    def label_from_instance(self, obj):
        return {
            'label': super().label_from_instance(obj),
            'data-url': obj.url
        }


class CreateEventForm(forms.ModelForm):
    def __init__(self, user_clubs, user_routes, *args, **kwargs):
        width = "xl:col-span-4 md:col-span-6 col-span-12"
        row_padding = "pb-2"

        super().__init__(*args, **kwargs)
        self.fields['frequency'].label = 'Recurrence'
        self.fields['route'].queryset = user_routes
        self.fields['club'].queryset = user_clubs
        self.helper = FormHelper(self)
        self.helper.css_container = css_container()
        self.helper.layout = Layout(
            Fieldset('Ride Info',
                     form_row(text_input("name", "event", width=width), padding_bottom=row_padding),
                     form_row(dropdown("privacy", "event", width=width), dropdown("club", "event", width=width),
                              padding_bottom=row_padding),
                     form_row(dropdown("route", "event", width=width), padding_bottom=row_padding),
                     form_row(text_input("max_riders", "event", width=width), padding_bottom=row_padding),
                     css_class='my-4'),
            Fieldset('Pace',
                     form_row(
                         dropdown("group_classification", "event", width=width), padding_bottom=row_padding),
                     form_row(
                         text_input("lower_pace_range", "event", width=width),
                         text_input("upper_pace_range", "event", width=width), padding_bottom=row_padding),
                     css_class='my-4'),
            Fieldset('Date / Time / Recurring',
                     form_row(text_input("start_date", "event", width=width), text_input("end_date", "event", width=width),
                              padding_bottom=row_padding),
                     form_row(dropdown("time_zone", "event", width=width), text_input("ride_time", "event", width=width), padding_bottom=row_padding),
                     form_row(dropdown("frequency", "event", width=width), padding_bottom=row_padding),
                     InlineCheckboxes("weekdays", label="", wrapper_class="mb-3")),
            form_row(
                Div(StrictButton('Create Ride', value="Create Ride", type="submit",
                                 css_class="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 "
                                           "rounded shadow-lg mb-4"),
                    css_class=width + " mt-4", ))
        )

        self.fields["weekdays"].label = ''

    def fields_required(self, fields):
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError("This field is required.")
                self.add_error(field, msg)

    def clean(self):
        required_fields = []

        private = self.cleaned_data.get('privacy')
        frequency = self.cleaned_data.get('frequency')

        if private == Event.EventMemberType.Members:
            required_fields.append('club')

        if frequency is Event.RecurrenceFrequency.Weekly:
            required_fields.append('weekdays')

        if len(required_fields) > 0:
            self.fields_required(required_fields)

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
            'route': mark_safe("<a id='route_url_id' class='underline text-blue-700' href='' target='_blank'>Add</a>")
        }


class CreateRouteForm(forms.ModelForm):
    def __init__(self, user_clubs, *args, **kwargs):
        width = "xl:col-span-4 md:col-span-6 col-span-12"
        row_padding = "pb-2"
        self.user = kwargs.pop('user', None)
        super(CreateRouteForm, self).__init__(*args, **kwargs)
        self.fields['start_location_name'].label = 'Start Location Name'
        self.fields['distance'].label = 'Distance (miles)'
        self.fields['elevation'].label = 'Elevation (ft)'
        self.fields['club'].queryset = user_clubs
        self.helper = FormHelper(self)
        self.helper.css_container = css_container()
        self.helper.layout = Layout(
            Fieldset('Route Info',
                     form_row(text_input("name", "route", width=width), text_input("start_location_name", "route",
                                                                                   width=width),
                              padding_bottom=row_padding),
                     form_row(text_input("url", "route", width=width), padding_bottom=row_padding),
                     css_class='mt-4'),
            Fieldset('Distance / Elevation',
                     form_row(
                         text_input("distance", "route", width=width),
                         text_input("elevation", "route", width=width), padding_bottom=row_padding),
                     css_class='mt-4'),
            Fieldset('Sharing',
                     form_row(Div(Field("shared", id="route_create_shared", wrapper_class="flex flex-row items-center",
                                        css_class="ml-4"),
                                  css_class="col-span-12 mb-1"), padding_bottom=row_padding),
                     form_row(dropdown("club", "route", width=width), padding_bottom=row_padding)),
            form_row(
                Div(StrictButton('Create Route', value="Create Route", type="submit",
                                 css_class="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 "
                                           "rounded shadow-lg mb-4"),
                    css_class=width, ))
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
