from django.core.paginator import Paginator


class CustomPaginator(Paginator):
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
