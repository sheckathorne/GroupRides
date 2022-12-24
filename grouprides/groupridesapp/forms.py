import datetime

import pytz
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Select, ModelChoiceField
from django.utils import timezone

from .models import EventOccurenceMember, EventOccurenceMessage, \
    Club, Event, Route, ClubMembership, ClubMembershipRequest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div
)
from crispy_forms.bootstrap import StrictButton
from django.utils.html import mark_safe


def text_input(field_name, id_name, width=4, margin_bottom=0):
    return Div(Field(field_name, id=f"{id_name}_create_{field_name}"), css_class=f"col-md-{width} mb-{margin_bottom}", )


def dropdown(field_name, id_name, height=38, width=4, margin_bottom=0, onchange=""):
    return Div(
        Field(
            field_name,
            id=f"{id_name}_create_{field_name}",
            css_class="w-100",
            style=f"height: {height}px;",
            onchange=onchange,),
        css_class=f"col-md-{width} mb-{margin_bottom}"
    )


def form_row(*args, bottom_margin=3, **kwargs):
    row_id = 'generic-row' if 'row_id' not in kwargs else kwargs['row_id']
    return Div(*args, css_class=f"row mb-{bottom_margin},", id=row_id)


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

        super(ClubMembershipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            form_row(
                dropdown("membership_type", "member", width=12, margin_bottom=2),),
            form_row(Div(Field("membership_expires", id=f"member_create_membership_expires"), css_class=f"col-md-12 mb-2", )),
            form_row(Div(Field("active"), css_class="mb-1")),
            Div(
                StrictButton('Close', value="Close", type="button", css_class="btn-secondary", data_bs_dismiss="modal"),
                StrictButton('Confirm', value="Confirm", type="submit", css_class="btn-primary"),
                css_class="modal-footer"
            ),
        )

        info_icon = '<i class="fa-solid fa-circle-info"></i>'
        popover_content = (f"<i>Each role includes the abilities of the roles below them, "
                           f"even if not explicitly specified.</i><br><br>"
                           f"<b>Creator</b> - The founder of the club. Has complete management control over the club, "
                           f"including the ability to disband it altogether. Once made a creator, the member cannot be "
                           f"removed or demoted to a lesser role.<br><br>"
                           f"<b>Admin</b> - Can modify members&#39; roles, respond to membership "
                           f"requests, and remove members.<br><br>"
                           f"<b>Ride Leader</b> - Can create events and rides that "
                           f"are associated with the club.<br><br>"
                           f"<b>Route Contributor</b> - Can create routes to be used in rides that are "
                           f"associated with the club. Any route created by a <i>Route Contributor</i> are available "
                           f"to all <i>Ride Leader</i>s for use in their rides.<br><br>"
                           f"<b>Paid Member</b> - Can join members-only rides that "
                           f"are associated with the club.<br><br>"
                           f"<b>Unpaid Member</b> - Can view club rides but cannot join them unles they are set "
                           f"to &#39Open&#39.<br><br>"
                           f"<b>Non-Member</b> - Has no club priveleges.")

        popover = (
            f"<a "
            f"tabindex='0' "
            f"role='button' "
            f"data-bs-html=true "
            f"data-bs-toggle='popover' "
            f"data-bs-trigger='focus' "
            f"data-bs-title='<h5>Member Types</h5>' "
            f"data-bs-content='{popover_content}'>"
            f"{info_icon}</a>")
        membership_type_label = self.fields['membership_type'].label + " "

        self.fields['membership_type'].label = membership_type_label + popover
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
                     form_row(text_input("name", "event")),
                     form_row(dropdown("privacy", "event"), dropdown("club", "event")),
                     form_row(dropdown("route", "event")),
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
                     form_row(dropdown("frequency", "event", margin_bottom=2)),
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
