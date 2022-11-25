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