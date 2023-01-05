from collections import OrderedDict
import django_filters
from crispy_forms.layout import Field, Div, HTML, Layout
from crispy_tailwind.tailwind import CSSContainer
from crispy_forms.bootstrap import StrictButton

from .models import EventOccurence
from django import forms
from .forms import form_row, dropdown, text_input
from crispy_forms.helper import FormHelper


def text_input(field_name, id_name, width=4):
    return Field(
            field_name,
            id=f"{id_name}_create_{field_name}",
            css_class="w-full shadow",
            wrapper_class=f"md:col-span-{width}")


def dropdown(field_name, id_name, width=4, onchange=""):
    return Field(
            field_name,
            id=f"{id_name}_create_{field_name}",
            css_class="w-full",
            wrapper_class=f"md:col-span-{width} shadow-parent cursor-pointer",
            onchange=onchange, )


def form_row(*args, padding_bottom=0, **kwargs):
    row_id = 'generic-row' if 'row_id' not in kwargs else kwargs['row_id']
    return Div(*args, css_class=f"grid gap-2 md:grid-cols-12 pb-{padding_bottom}", id=row_id)


class RideForm(forms.ModelForm):
    class Meta:
        model = EventOccurence
        fields = ['club', 'group_classification', 'route']

    def __init__(self, *args, **kwargs):
        base_input = (
            "bg-white focus:outline-none border border-gray-300 rounded py-2 px-4 block w-full "
            "appearance-none leading-normal text-gray-700"
        )

        default_styles = {
            "text": base_input,
            "number": base_input,
            "radioselect": "",
            "email": base_input,
            "url": base_input,
            "password": base_input,
            "hidden": "",
            "multiplehidden": "",
            "file": "",
            "clearablefile": "",
            "textarea": base_input,
            "date": base_input,
            "datetime": base_input,
            "time": base_input,
            "checkbox": "",
            "select": base_input,
            "nullbooleanselect": "",
            "selectmultiple": base_input,
            "checkboxselectmultiple": "",
            "multi": "",
            "splitdatetime": "text-gray-700 bg-white focus:outline border border-gray-300 leading-normal px-4 "
                             "appearance-none rounded-lg py-2 focus:outline-none mr-2",
            "splithiddendatetime": "",
            "selectdate": "",
            "error_border": "border-red-500",
        }

        css = CSSContainer(default_styles)

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
                             text_input("distance__lt", "rides", width=3,),
                             text_input("distance__gt", "rides", width=3,),),
                             css_class="md:col-span-12 lg:col-span-10",),
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
