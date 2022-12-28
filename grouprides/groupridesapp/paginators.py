from django.core.paginator import Paginator


class CustomPaginator(Paginator):
    def get_elided_page_range(self, number=1, on_each_side=3, on_ends=2):
        number = self.validate_number(number)
        node_count = 3 + ((on_each_side + on_ends) * 2)
        total_end_nodes = (on_ends * 2)

        if self.num_pages <= node_count:
            yield from self.page_range
            return

        print('node count:', node_count)
        left_nodes_to_add = max(node_count - number - on_each_side - total_end_nodes, 0)
        print('LNTA:', left_nodes_to_add)
        right_nodes_to_add = max(node_count - total_end_nodes - 1 - on_each_side - self.num_pages + number, 0)

        if number > (1 + on_each_side + on_ends) + 1:
            print('A', range(1, on_ends))
            yield from range(1, on_ends + 1)
            yield self.ELLIPSIS
            print('B', range(number - on_each_side - right_nodes_to_add, number))
            yield from range(number - on_each_side - right_nodes_to_add, number + 1)
        else:
            print('C', range(1, number + left_nodes_to_add))
            yield from range(1, number + left_nodes_to_add + 1)

        if number < (self.num_pages - on_each_side - on_ends) - 1:
            print('D', range(number + left_nodes_to_add + 1, number + on_each_side + left_nodes_to_add))
            yield from range(number + left_nodes_to_add + 1, number + on_each_side + left_nodes_to_add + 1)
            yield self.ELLIPSIS
            print('E', range(self.num_pages - on_ends + 1, self.num_pages))
            yield from range(self.num_pages - on_ends + 1, self.num_pages + 1)
        else:
            print('F', range(number + 1, self.num_pages))
            yield from range(number + 1, self.num_pages + 1)
