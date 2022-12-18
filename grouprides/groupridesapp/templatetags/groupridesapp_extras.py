from django import template

from groupridesapp.models import ClubMembershipRequest

register = template.Library()


@register.simple_tag
def can_register_to_ride(user, event_occurence):
    return event_occurence.can_be_joined_by(user)


@register.simple_tag
def say_deactivate(tab_type, active):
    return tab_type == active or active


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def contains_pending_requests(members):
    for member in members:
        if member["request"].status == ClubMembershipRequest.RequestStatus.Pending:
            return True

    return False
