class Coordinate2D(object):
    '''
    A simple class used to pass around 2-dimensional coordinates.

        - x: Location on the left-to-right x axis
        - y: Location on the top-to-bottom y axis
    '''

    def __init__(self,
        x: int = 0,
        y: int = 0
    ):
        self.x = x
        self.y = y


class Size2D(object):
    '''
    A simple class used to pass around 2-dimensional size data.

        - width: Length of the size on the left-to-right x axis
        - height: Length of the size on the top-to-bottom y axis
    '''

    def __init__(self,
        width: int = 1,
        height: int = 1
    ):
        self.width = width
        self.height = height


