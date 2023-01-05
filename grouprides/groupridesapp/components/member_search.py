from django_unicorn.components import UnicornView
from groupridesapp.forms import ClubMembershipForm
from groupridesapp.paginators import CustomPaginator


class MemberSearchView(UnicornView):
    membername = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.members = kwargs.get('members', None)
        self.tab_type = kwargs.get('tab_type', None)

    def searched_members(self):
        if self.membername:
            members = [{'member': m, 'form': ClubMembershipForm(instance=m)} for m in self.members
                       if self.membername.lower() in (m.user.first_name + ' ' + m.user.last_name).lower()]
        else:
            members = [{'member': m, 'form': ClubMembershipForm(instance=m)} for m in self.members]

        pagination = CustomPaginator(
            self.request,
            members,
            10,
            on_each_side=2,
            on_ends=1
        )

        return {
            "members": pagination.item_list,
            "page_count": pagination.num_pages,
            "pagination_items": pagination.html_list,
            "tab_type": self.tab_type,
        }
