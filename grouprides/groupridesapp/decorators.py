from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from .models import EventOccurenceMember


def user_is_ride_member(function=None, redirect_url='/'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            event_occurence_id = kwargs["event_occurence_id"]

            member = EventOccurenceMember.objects.filter(user=request.user, event_occurence__id=event_occurence_id)

            if not member.exists():
                messages.error(
                    request,
                    "You cannot participate in this discussion until you're registered for the ride")
                return redirect(reverse('my_rides'))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator
