from django import template

register = template.Library()


@register.simple_tag
def can_register_to_ride(user, event_occurence):
    return event_occurence.can_be_joined_by(user)
