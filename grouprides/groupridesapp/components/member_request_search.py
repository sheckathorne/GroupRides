from django_unicorn.components import UnicornView

from groupridesapp.models import ClubMembershipRequest
from groupridesapp.utils import generate_pagination


def filter_membername(name, reqs):
    return [
        m for m in reqs
        if name.lower()
        in (m.user.first_name + ' ' + m.user.last_name).lower()
    ]


def filter_status(status, reqs):
    return [m for m in reqs if m.status == int(status)]


def filter_requests(name, status, reqs):
    if name and not status:
        return filter_membername(name, reqs)
    elif name and status:
        members = filter_membername(name, reqs)
        return filter_status(status, members)
    elif status and not name:
        return filter_status(status, reqs)
    else:
        return reqs


class MemberRequestSearchView(UnicornView):
    membername = ""
    selected_status = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reqs = kwargs.get('reqs', None)
        self.tab_type = kwargs.get('tab_type', None)

    def searched_requests(self):
        status_choices = []

        for req in self.reqs.values_list('status', flat=True).distinct().order_by('status'):
            status_choices.append({'label': ClubMembershipRequest.RequestStatus(req).label, 'value': req})

        members = filter_requests(self.membername, self.selected_status, self.reqs)
        pagination = generate_pagination(self.request, qs=members, items_per_page=10)

        return {
            "members": pagination["page_obj"].object_list,
            "status_choices": status_choices,
            "page_count": pagination["page_obj"].paginator.num_pages,
            "pagination_items": pagination["pagination_items"],
            "tab_type": self.tab_type,
        }
