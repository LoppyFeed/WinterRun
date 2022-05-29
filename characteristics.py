class Position:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __add__(self, other):
        if type(other) is not Shift:
            raise NotImplementedError

        return Position(self.__x + other.x, self.__y + other.y)

    def set_position(self, x: int, y: int):
        self.__x = x
        self.__y = y


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.__r = r % 256
        self.__g = g % 256
        self.__b = b % 256

    def __str__(self):
        return str((self.__r, self.__g, self.__b))

    def __call__(self, *args, **kwargs):
        return self.__r, self.__g, self.__b

    def set_color(self, r: int, g: int, b: int):
        self.__r = r % 256
        self.__g = g % 256
        self.__b = b % 256


class Colors:
    Black = Color(0, 0, 0)
    Red = Color(255, 0, 0)
    Green = Color(0, 255, 0)
    Blue = Color(0, 0, 255)
    White = Color(255, 255, 255)
    LiteBlue = Color(100, 180, 255)


class Size:
    def __init__(self, width: int, height: int):
        self.__width = width
        self.__height = height

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def set_size(self, width: int, height: int):
        self.__width = width
        self.__height = height


class Shift:
    def __init__(self, dx: int, dy: int):
        self.__dx = dx
        self.__dy = dy

    @property
    def x(self):
        return self.__dx

    @property
    def y(self):
        return self.__dy

    def set_shift(self, dx: int, dy: int):
        self.__dx = dx
        self.__dy = dy
