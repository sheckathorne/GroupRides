import datetime
from .models import EventOccurence, EventOccurenceMember, ClubMembership


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


def generate_pagination_items(page_count=1, active_page=1, delta=2):
    pagination_items = list()
    active_page = int(active_page)

    right_items = 3 - (active_page - delta)
    left_items = (active_page + 2 + delta) - page_count

    extra_items_to_right = right_items if right_items > 0 else 0
    extra_items_to_left = left_items if left_items > 0 else 0

    middle_ellipses = bool(extra_items_to_right) or bool(extra_items_to_left)
    left_ellipses = not bool(extra_items_to_right) and not bool(extra_items_to_left)
    right_ellipses = not bool(extra_items_to_right) and not bool(extra_items_to_left)

    print('left', left_ellipses)
    print('middle', middle_ellipses)
    print('right', right_ellipses)

    prev_page = 1 if active_page == 1 else active_page - 1
    prev_disabled = " disabled" if active_page == 1 else ""
    next_page = page_count if active_page == page_count else active_page + 1
    next_disabled = " disabled" if active_page == page_count else ""

    for i in range(0, page_count + 2):
        active = " active" if i == active_page else ""

        prev_button = f"<li class=\"page-item{ prev_disabled }\">" \
                      f"<a class=\"page-link\" href=\"?page={prev_page}\">&laquo;</a></li>"

        next_button = f"<li class=\"page-item{ next_disabled }\">" \
                      f"<a class=\"page-link\" href=\"?page={next_page}\">&raquo;</a></li>"

        ellipses = f"<li class=\"page-item\"><a class=\"page-link\" href=\"#\">...</a></li>"

        num_button = f"<li class=\"page-item{ active }\"><a class=\"page-link\" href=\"?page={i}\">{i}</a></li>"

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
