import datetime

from crispy_forms.layout import Field, Div
from crispy_tailwind.tailwind import CSSContainer
from django.core import paginator
from django.utils import timezone
import django_filters
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import TextInput
from django.utils.safestring import mark_safe

from .models import EventOccurence, EventOccurenceMember, ClubMembership, Club, EventOccurenceMessage
from .paginators import CustomPaginator


def days_from_today(n):
    return datetime.date.today() + datetime.timedelta(days=n)


def club_total_from(qs, club_name):
    return qs.get(club__name=club_name)['total']


def club_ride_count(qs, club_name):
    return 0 if not qs.exists() else club_total_from(qs, club_name)


def gather_available_rides(user):
    days_in_the_future = days_from_today(11)

    return EventOccurence.objects.exclude(
        pk__in=EventOccurenceMember.objects.filter(
            user=user
        ).values('event_occurence')
    ).filter(
        privacy__lte=EventOccurence.EventMemberType.Open,
        club__in=ClubMembership.objects.filter(
            user=user).values('club')
    ).filter(
        ride_date__lte=days_in_the_future,
        ride_date__gte=datetime.date.today()
    )


def distinct_errors(errors_list):
    new_list = []
    for error in errors_list:
        if error not in new_list:
            new_list.append(error)

    return new_list


def remove_page_from_url(full_path):
    if 'page' not in full_path:
        return full_path
    else:
        return full_path[:full_path.find('page') - 1]


def get_filter_fields(qs, table_prefix):
    def filter_club(queryset, _club, value):
        return queryset.filter(**{F"{table_prefix}club": value.id})

    clubs_queryset = Club.objects.filter(pk__in=qs.values(f"{table_prefix}club")).distinct()
    classification_choices = EventOccurence.GroupClassification.choices
    available_choices = qs.values_list(f"{table_prefix}group_classification", flat=True)
    group_classification_choices = [choice for choice in classification_choices if choice[0] in list(available_choices)]

    club = django_filters.ModelChoiceFilter(
        label='',
        lookup_expr='exact',
        field_name=f"{table_prefix}club",
        to_field_name='slug',
        queryset=clubs_queryset,
        empty_label='Select Club',
        method=filter_club,
    )

    group_classification = django_filters.ChoiceFilter(
        label='',
        lookup_expr='exact',
        field_name=f"{table_prefix}group_classification",
        choices=group_classification_choices,
        empty_label='Select Classification',
    )

    distance__lt = django_filters.NumberFilter(
        field_name=f"{table_prefix}route__distance",
        lookup_expr='lt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Less Than'
        }),
    )

    distance__gt = django_filters.NumberFilter(
        field_name=f"{table_prefix}route__distance",
        lookup_expr='gt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Greater Than'
        }),
    )

    return [('club', club),
            ('group_classification', group_classification),
            ('distance__lt', distance__lt),
            ('distance__gt', distance__gt)]


def create_pagination(f, table_prefix, page_number):
    page = CustomPaginator(f.qs.order_by(f"{table_prefix}ride_date", f"{table_prefix}ride_time"), 4)
    page_obj = page.get_page(page_number)
    return page_obj


def get_event_comments(occurence_id, order_by):
    return EventOccurenceMessage.objects.filter(event_occurence__id=occurence_id).order_by(order_by)


def get_members_by_type(tab_type, qs):
    now = timezone.now().date()
    if tab_type == "inactive":
        members = qs.filter(Q(active=False) | Q(membership_expires__lt=now))
    elif tab_type == "active":
        members = qs.filter(active=True, membership_expires__gte=now)
    else:
        members = qs.filter(active=True, membership_expires__gte=now)

    return members


def base_input_style():
    return f"bg-white shadow focus:outline-none border border-gray-300 rounded py-2 px-4 " \
           f"block w-full appearance-none leading-normal text-gray-700"


def css_container():
    base_input = base_input_style()

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
    css -= {'text': 'rounded-lg'}
    css += {'text': 'rounded'}

    return css


def text_input(field_name, id_name, width="md:col-span-4"):
    return Field(
        field_name,
        id=f"{id_name}_create_{field_name}",
        css_class="w-full shadow",
        wrapper_class=width)


def dropdown(field_name, id_name, width="md:col-span-4", onchange=""):
    return Field(
        field_name,
        id=f"{id_name}_create_{field_name}",
        wrapper_class=f"{width} cursor-pointer",
        onchange=onchange, )


def form_row(*args, padding_bottom="pb-0", **kwargs):
    row_id = 'generic-row' if 'row_id' not in kwargs else kwargs['row_id']
    return Div(*args, css_class=f"grid gap-2 md:grid-cols-12 {padding_bottom}", id=row_id)
