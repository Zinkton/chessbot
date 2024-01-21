from collections import OrderedDict


class LimitedSizeDict(OrderedDict):
    def __init__(self, size_limit):
        super().__init__()
        self.size_limit = size_limit
        self.found = False

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self.ensure_size_limit()

    def ensure_size_limit(self):
        if len(self) > self.size_limit:
            self.popitem(last=False)