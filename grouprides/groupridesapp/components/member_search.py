from django.utils.functional import cached_property
from django_unicorn.components import UnicornView
from groupridesapp.forms import EditClubMemberForm
from groupridesapp.models import ClubMembership
from groupridesapp.utils import generate_pagination


class MemberSearchView(UnicornView):
    membername = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.members = kwargs.get('members', None)
        self.tab_type = kwargs.get('tab_type', None)

    def searched_members(self):
        if(type(self.members[0])) is dict:
            pks = [m['pk'] for m in self.members]
            mems = ClubMembership.objects.filter(pk__in=pks)
            members = [{'member': m, 'form': EditClubMemberForm(instance=m)} for m in mems
                       if self.membername.lower() in (m.user.first_name + ' ' + m.user.last_name).lower()]
        else:
            members = [{'member': m, 'form': EditClubMemberForm(instance=m)} for m in self.members]

        pagination = generate_pagination(self.request, qs=members, items_per_page=10)
        return {
            "members": pagination["page_obj"].object_list,
            "page_count": pagination["page_obj"].paginator.num_pages,
            "pagination_items": pagination["pagination_items"],
            "tab_type": self.tab_type,
        }
