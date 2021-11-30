from django.core.paginator import Paginator, InvalidPage, EmptyPage


class Page(object):
    """
    page
    """

    def __init__(self, objects, page_size):
        """

        :param objects: query set
        :param page_size: page size
        """
        self.objects = objects
        try:
            page_size = int(page_size)
            if page_size > 100:
                self.page_size = 100
            elif page_size <= 0:
                self.page_size = 10
            else:
                self.page_size = page_size
        except Exception as e:
            self.page_size = 10
        self.page_index = 1
        self.paginator = Paginator(self.objects, self.page_size)

    def page(self, page_index):
        objs = []
        total_page = 1
        total_count = 0

        try:
            page_index = int(page_index)
            if page_index <= 0:
                self.page_index = 1
            else:
                self.page_index = page_index
        except Exception as e:
            self.page_index = 1

        try:
            page_obj = self.paginator.page(self.page_index)

            objs = page_obj.object_list
            total_page = page_obj.paginator.num_pages
            total_count = page_obj.paginator.count
        except Exception as e:
            objs = []

        return {
            'objects': objs,
            'page_index': self.page_index,
            'total_page': total_page,
            'total_count': total_count
        }
