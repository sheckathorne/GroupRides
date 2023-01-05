from django.core.paginator import Paginator
from django.utils.safestring import mark_safe


class CustomPaginator(Paginator):
    def __init__(self, request, object_list, per_page, orphans=0,
                 allow_empty_first_page=True, on_each_side=2, on_ends=1):
        self.request = request
        self.on_each_side = on_each_side
        self.on_ends = on_ends
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)

    @property
    def item_list(self):
        page_num = self.request.GET.get('page', 1)
        return self.get_page(page_num)

    @property
    def html_list(self):
        pagination_html = []
        page_num = self.request.GET.get('page', 1)
        if self.get_page(page_num).paginator.num_pages > 0:
            page_list = self.get_elided_page_range(
                page_num,
                on_each_side=self.on_each_side,
                on_ends=self.on_ends
            )

            pagination_html = tailwind_pagination(
                page_list,
                page_num,
                self.num_pages,
                current_url=remove_page_from_url(self.request.get_full_path()))

        return pagination_html

    def get_elided_page_range(self, number=1, on_each_side=2, on_ends=1):
        number = self.validate_number(number)
        node_count = 3 + ((on_each_side + on_ends) * 2)

        if self.num_pages <= node_count:
            yield from self.page_range
            return

        left_nodes_to_add = max(node_count - number - on_each_side - on_ends - 1, 0)
        right_nodes_to_add = max(node_count - on_ends - 2 - on_each_side - self.num_pages + number, 0)

        if number > (1 + on_each_side + on_ends) + 1:
            yield from range(1, on_ends + 1)
            yield self.ELLIPSIS
            yield from range(number - on_each_side - right_nodes_to_add, number + 1)
        else:
            yield from range(1, number + left_nodes_to_add + 1)

        if number < (self.num_pages - on_each_side - on_ends) - 1:
            yield from range(number + left_nodes_to_add + 1, number + on_each_side + left_nodes_to_add + 1)
            yield self.ELLIPSIS
            yield from range(self.num_pages - on_ends + 1, self.num_pages + 1)
        else:
            yield from range(number + 1, self.num_pages + 1)


def remove_page_from_url(full_path):
    if 'page' not in full_path:
        return full_path
    else:
        return full_path[:full_path.find('page') - 1]


def tailwind_pagination(pagination_list, page, page_count, current_url=""):
    pagination_items = list()
    active_page = int(page)

    hover_color = f"hover:bg-blue-100 hover:shadow"
    base_class = f"rounded py-2 px-4"
    enabled_class = f"{base_class} text-gray-800 {hover_color} hover:text-gray-900"
    disabled_class = f"{base_class} bg-transparent text-gray-500 cursor-default focus:shadow-none"
    active_class = f"{base_class} text-white bg-blue-600 shadow-xl"

    prev_page = 1 if active_page == 1 else active_page - 1
    next_page = page_count if active_page == page_count else active_page + 1

    prev_disabled = {'li_class': ' disabled', 'a_class': disabled_class, 'aria': ''} \
        if active_page == 1 else {'li_class': '', 'a_class': enabled_class, 'aria': ''}

    next_disabled = {'li_class': ' disabled', 'a_class': disabled_class, 'aria': ''} \
        if active_page == page_count else {'li_class': '', 'a_class': enabled_class, 'aria': ''}

    qm_index = current_url.find("?")
    query = "?"

    if qm_index > 0:
        query = query + current_url[qm_index + 1:] + "&"

    ellipses = f"<a class=\"{enabled_class}\"" \
               f"href=\"#\">...</a>"

    href = "#" if active_page == 1 else f"\"{query}page={prev_page}\""

    prev_button = f"<a class=\"{prev_disabled['a_class']}\" " \
                  f"href={href} tabindex=\"-1\" " \
                  f">&laquo;</a>"

    pagination_items.append(mark_safe(prev_button))

    for item in pagination_list:
        if item == Paginator.ELLIPSIS:
            pagination_items.append(mark_safe(ellipses))
        elif item == active_page:
            num_button = f"<a class=\"{active_class}\" href=\"{query}page={item}\">{item}</a>"

            pagination_items.append(mark_safe(num_button))
        else:
            num_button = f"<a class=\"{enabled_class}\" href=\"{query}page={item}\">{item}</a>"

            pagination_items.append(mark_safe(num_button))

    href = "#" if active_page == page_count else f"\"{query}page={next_page}\""
    next_button = f"<a class=\"{next_disabled['a_class']}\" " \
                  f"href={href} tabindex=\"-1\" " \
                  f">&raquo;</a>"

    pagination_items.append(mark_safe(next_button))

    return pagination_items
