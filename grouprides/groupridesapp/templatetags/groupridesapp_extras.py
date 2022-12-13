from django import template

register = template.Library()


@register.simple_tag
def can_register_to_ride(user, event_occurence):
    return event_occurence.can_be_joined_by(user)


@register.simple_tag
def active_tab_is_selected(tab_type):
    return tab_type == "active"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
