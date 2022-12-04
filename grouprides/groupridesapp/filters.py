import django_filters
from .models import EventOccurence, Club, ClubMembership
from django import forms
from django.forms import inlineformset_factory, TextInput
from .forms import form_row, dropdown, text_input

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Div
)
from crispy_forms.bootstrap import StrictButton


class AvailableRideForm(forms.ModelForm):
    class Meta:
        model = EventOccurence
        fields = ['club', 'group_classification']

    def __init__(self, *args, **kwargs):
        super(AvailableRideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset('Filter Rides',
                     form_row(
                         Div(
                             form_row(
                                 dropdown("club", "rides", width=3, margin_bottom=2),
                                 dropdown("group_classification", "rides", width=3, margin_bottom=2),
                                 text_input("distance__lt", "rides", width=3, margin_bottom=2),
                                 text_input("distance__gt", "rides", width=3, margin_bottom=2),
                                 bottom_margin=1
                             ),
                             css_class="col-md-11"
                         ),
                         Div(StrictButton('Filter', value="Filter", type="submit", css_class="btn-primary w-100"),
                             css_class="col-md-1"),
                         bottom_margin=2
                     ),
                     css_class='mt-4'),
        )


def user_clubs(request):
    return Club.objects.filter(
        pk__in=ClubMembership.objects.filter(user=request.user).values('club')
    )


class AvailableRideFilter(django_filters.FilterSet):
    group_classification = django_filters.ChoiceFilter(
        label='',
        lookup_expr='exact',
        field_name='group_classification',
        choices=EventOccurence.GroupClassification.choices,
        empty_label='Select Classification'
    )

    club = django_filters.ModelChoiceFilter(
        label='',
        lookup_expr='exact',
        field_name='club',
        queryset=user_clubs,
        empty_label='Select Club'
    )

    distance__lt = django_filters.NumberFilter(
        field_name='route__distance',
        lookup_expr='lt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Less Than'
        })
    )

    distance__gt = django_filters.NumberFilter(
        field_name='route__distance',
        lookup_expr='gt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Greater Than'
        })
    )

    class Meta:
        form = AvailableRideForm
        model = EventOccurence
        fields = ['club', 'group_classification', 'route__distance']
