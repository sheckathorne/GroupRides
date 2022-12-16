from django_unicorn.components import UnicornView
from groupridesapp.utils import generate_pagination


class MemberRequestSearchView(UnicornView):
    membername = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reqs = kwargs.get('reqs', None)
        self.tab_type = kwargs.get('tab_type', None)

    def searched_requests(self):
        if self.membername:
            members = [m for m in self.reqs
                       if self.membername.lower()
                       in (m.user.first_name + ' ' + m.user.last_name).lower()]
        else:
            members = self.reqs

        pagination = generate_pagination(self.request, qs=members, items_per_page=10)
        return {
            "members": pagination["page_obj"].object_list,
            "page_count": pagination["page_obj"].paginator.num_pages,
            "pagination_items": pagination["pagination_items"],
            "tab_type": self.tab_type,
        }
