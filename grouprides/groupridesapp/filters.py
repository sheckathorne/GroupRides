from collections import OrderedDict

import django_filters
from django.urls import reverse

from .models import EventOccurence
from django import forms
from .forms import form_row, dropdown, text_input

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Div, HTML
)
from crispy_forms.bootstrap import StrictButton


class RideForm(forms.ModelForm):
    class Meta:
        model = EventOccurence
        fields = ['club', 'group_classification', 'route']

    def __init__(self, *args, **kwargs):
        super(RideForm, self).__init__(*args, **kwargs)
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
                             css_class="col-lg-10"
                         ),
                         Div(StrictButton('Filter', value="Filter", type="submit", css_class="btn-primary w-100 mb-2"),
                             css_class="col-lg-1 col-md-6"),
                         bottom_margin=2,
                         row_id="ride-filter-parent"
                     ),
                     css_class=''),
        )


class RideFilter(django_filters.FilterSet):
    def __init__(self, *args, filter_fields=None, url=None, **kwargs):
        django_filters.FilterSet.__init__(self, *args)
        self.filters = OrderedDict()
        for field in filter_fields:
            self.filters[field[0]] = field[1]
        self.queryset = kwargs['queryset']
        self.url = url

    class Meta:
        url = 'my_available_rides'
        form = RideForm
        model = EventOccurence
        fields = ['club', 'group_classification', 'route__distance']
