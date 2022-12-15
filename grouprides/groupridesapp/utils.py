import datetime
from django.utils import timezone
import django_filters
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import TextInput

from .forms import EditClubMemberForm
from .models import EventOccurence, EventOccurenceMember, ClubMembership, Club, EventOccurenceMessage


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


def generate_pagination(request, qs=None, items_per_page=10):
    paginator = Paginator(qs, items_per_page)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    page_count = page_obj.paginator.num_pages
    pagination_items = []

    if page_count > 1:
        pagination_items = generate_pagination_items(
            page_count=page_obj.paginator.num_pages,
            active_page=page_number,
            delta=2
        )

    return {"page_obj": page_obj, "pagination_items": pagination_items}


def generate_pagination_items(page_count=1, active_page=1, delta=2, current_url=""):
    pagination_items = list()
    active_page = int(active_page)

    right_items = 3 - (active_page - delta)
    left_items = (active_page + 2 + delta) - page_count

    extra_items_to_right = right_items if right_items > 0 else 0
    extra_items_to_left = left_items if left_items > 0 else 0

    middle_ellipses = bool(extra_items_to_right) or bool(extra_items_to_left)
    left_ellipses = not bool(extra_items_to_right) and not bool(extra_items_to_left)
    right_ellipses = not bool(extra_items_to_right) and not bool(extra_items_to_left)

    prev_page = 1 if active_page == 1 else active_page - 1
    prev_disabled = " disabled" if active_page == 1 else ""
    next_page = page_count if active_page == page_count else active_page + 1
    next_disabled = " disabled" if active_page == page_count else ""

    qm_index = current_url.find("?")
    query = "?"

    if qm_index > 0:
        query = query + current_url[qm_index + 1:] + "&"

    for i in range(0, page_count + 2):
        active = " active" if i == active_page else ""

        prev_button = f"<li class=\"page-item{ prev_disabled }\">" \
                      f"<a class=\"page-link\" href=\"{query}page={prev_page}\">&laquo;</a></li>"

        next_button = f"<li class=\"page-item{ next_disabled }\">" \
                      f"<a class=\"page-link\" href=\"{query}page={next_page}\">&raquo;</a></li>"

        ellipses = f"<li class=\"page-item\"><a class=\"page-link\" href=\"#\">...</a></li>"

        num_button = f"<li class=\"page-item{ active }\"><a class=\"page-link\" href=\"{query}page={i}\">{i}</a></li>"

        if i == 0:
            pagination_items.append(prev_button)
        elif i == page_count + 1:
            pagination_items.append(next_button)
        elif ((1 < i < page_count
               and active_page - delta - extra_items_to_left <= i <= active_page + delta + extra_items_to_right)
              or i == 1
              or i == page_count):
            pagination_items.append(num_button)
        elif middle_ellipses:
            pagination_items.append(ellipses)
            middle_ellipses = not middle_ellipses
        elif (left_ellipses and active_page > i) or (right_ellipses and active_page < i):
            if active_page > i:
                left_ellipses = not left_ellipses
                if active_page - 1 == delta + 2:
                    pagination_items.append(num_button)
                else:
                    pagination_items.append(ellipses)
            else:
                right_ellipses = not right_ellipses
                if page_count - active_page == delta + 2:
                    pagination_items.append(num_button)
                else:
                    pagination_items.append(ellipses)

    return pagination_items


def remove_page_from_url(full_path):
    if 'page' not in full_path:
        return full_path
    else:
        return full_path[:full_path.find('page') - 1]


def filter_club(queryset, _club, value):
    return queryset.filter(club=value.id)


def get_filter_fields(qs, table_prefix):
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
        empty_label='Select Classification'
    )

    distance__lt = django_filters.NumberFilter(
        field_name=f"{table_prefix}route__distance",
        lookup_expr='lt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Less Than'
        })
    )

    distance__gt = django_filters.NumberFilter(
        field_name=f"{table_prefix}route__distance",
        lookup_expr='gt',
        label='',
        widget=TextInput(attrs={
            'placeholder': 'Distance Greater Than'
        })
    )

    return [('club', club),
            ('group_classification', group_classification),
            ('distance__lt', distance__lt),
            ('distance__gt', distance__gt)]


def create_pagination(f, table_prefix, page_number):
    paginator = Paginator(f.qs.order_by(f"{table_prefix}ride_date", f"{table_prefix}ride_time"), 4)
    page_obj = paginator.get_page(page_number)

    return page_obj


def create_pagination_html(request, page_obj, page_number):
    url = remove_page_from_url(request.get_full_path())
    page_count = page_obj.paginator.num_pages
    pagination_items = []

    if page_count > 1:
        pagination_items = generate_pagination_items(
            page_count=page_count,
            active_page=page_number,
            delta=2,
            current_url=url
        )

    return pagination_items


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

"""
def get_members_by_type(tab_type, qs):
    if tab_type == "inactive":
        members = [
            {'member': mem, 'form': EditClubMemberForm(instance=mem)}
            for mem in qs if
            mem.is_expired() or mem.is_inactive()
        ]
    elif tab_type == "active":
        members = [
            {'member': mem, 'form': EditClubMemberForm(instance=mem)}
            for mem in qs if
            not mem.is_expired() and not mem.is_inactive()
        ]
    else:
        members = [
            {'member': mem, 'form': EditClubMemberForm(instance=mem)}
            for mem in qs if
            not mem.is_expired() and not mem.is_inactive()
        ]

    return members
"""
