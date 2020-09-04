import json

class Dimensions:

    class Size:

        def __init__(self, width=0, height=0):
            self.width = int(width)
            self.height = int(height)

        def __iter__(self):
            yield self.width
            yield self.height

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__,
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)

    class Position:

        def __init__(self, x=0, y=0):
            self.x = int(x)
            self.y = int(y)

        def __iter__(self):
            yield self.x
            yield self.y

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__,
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)

    def __init__(self, pos_x=0, pos_y=0, width=0, height=0):
        self.position = Dimensions.Position(pos_x, pos_y)
        self.size = Dimensions.Size(width, height)

    def set_size(self, width, height):
        self.set_dimension(width=width, height=height)

    def get_size(self):
        return self.size

    def set_position(self, x, y):
        self.set_dimension(x=x, y=y)

    def get_position(self):
        return self.position

    def get_bbox(self):
        return (int(self.position.x - self.size.width/2),
                int(self.position.y - self.size.height/2),
                int(self.position.x + self.size.width/2),
                int(self.position.y + self.size.height/2))

    def set_dimension(self, width=None, height=None, x=None, y=None):
        if not width is None:
            self.size.width = width
        if not height is None:
            self.size.height = height
        if not x is None:
            self.position.x = x
        if not y is None:
            self.position.y = y

    def __repr__(self):
        return json.dumps({
            'class': self.__class__.__name__,
            'fields': {
                self.position.__class__.__name__: json.loads(str(self.position)),
                self.size.__class__.__name__: json.loads(str(self.size))}}, indent=4)
