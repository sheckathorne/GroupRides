from collections import OrderedDict
import django_filters
from crispy_forms.layout import Div, HTML, Layout
from crispy_forms.bootstrap import StrictButton

from .models import EventOccurence
from django import forms
from .forms import form_row, dropdown, text_input
from crispy_forms.helper import FormHelper

from .utils import css_container, form_row, dropdown, text_input


class RideForm(forms.ModelForm):
    class Meta:
        model = EventOccurence
        fields = ['club', 'group_classification', 'route']

    def __init__(self, *args, **kwargs):
        css = css_container()
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.disable_csrf = True
        self.helper.css_container = css
        self.helper.attrs["field_class"] = "mb-0"
        self.helper.layout = Layout(
            Div(
                form_row(
                    Div(form_row(
                        dropdown(
                            "club",
                            "rides",
                            width=3,
                            onchange="form.submit()"),
                        dropdown(
                            "group_classification",
                            "rides",
                            width=3,
                            onchange="form.submit()"),
                        text_input("distance__lt", "rides", width=3, ),
                        text_input("distance__gt", "rides", width=3, ), ),
                        css_class="md:col-span-12 lg:col-span-10", ),
                    Div(form_row(
                        Div(
                            StrictButton(
                                'Filter',
                                value="Filter",
                                type="submit",
                                css_class="w-full bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 "
                                          "px-4 border border-gray-400 rounded shadow"),
                            css_class="md:col-span-6"),
                        Div(
                            HTML(
                                f"<a href=''>"
                                f"<button class='w-full bg-white hover:bg-gray-100 text-gray-800 "
                                f"font-semibold py-2 px-4 border border-gray-400 rounded shadow'>Clear</button>"
                                f"</a>"),
                            css_class="md:col-span-6"),
                        row_id="ride-filter-parent"
                    ),
                        css_class="md:col-span-12 lg:col-span-2"),
                    padding_bottom=2,
                    css_class="pb-2"
                )
            )
        )


class RideFilter(django_filters.FilterSet):
    def __init__(self, *args, queryset=None, filter_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters = OrderedDict()
        for field in filter_fields:
            self.filters[field[0]] = field[1]

        self.queryset = queryset

    class Meta:
        form = RideForm
        model = EventOccurence
        fields = ['club', 'group_classification', 'route__distance']
