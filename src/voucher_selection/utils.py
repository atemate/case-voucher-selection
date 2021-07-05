from itertools import zip_longest


def iter_paged(iterable, page_size: int, fillvalue=None):
    # TODO: test
    # source: https://stackoverflow.com/a/434411/4977823
    args = [iter(iterable)] * page_size
    return zip_longest(*args, fillvalue=fillvalue)
