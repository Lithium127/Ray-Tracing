from __future__ import annotations
import typing as t

from math import sqrt

from .hittable import Interval

class Color(object):
    
    x: float
    y: float
    z: float
    
    def __init__(self, r: float, g: float, b: float) -> None:
        """Creates a color with a given r, g, b value between 0.0 and 1.0

        Args:
            r (float): Red aspect
            g (float): Blue aspect
            b (float): Green aspect
        """
        self.x = r
        self.y = g
        self.z = b
    
    def __pos__(self) -> Color:
        return Color(+self.x, +self.y, +self.z)
    
    def __neg__(self) -> Color:
        return Color(-self.x, -self.y, -self.z)
    
    def __abs__(self) -> Color:
        return Color(abs(self.x), abs(self.x), abs(self.x))
    
    def __add__(self, other: Color) -> Color:
        return Color(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: Color) -> Color:
        return Color(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other: Color | float | int) -> Color:
        if isinstance(other, Color):
            return Color(self.x * other.x, self.y * other.y, self.z * other.z)
        return Color(self.x * other, self.y * other, self.z * other)
    
    def __floordiv__(self, other: Color | float | int) -> Color:
        if isinstance(other, Color):
            return Color(self.x // other.x, self.y // other.y, self.z // other.z)
        return Color(self.x // other, self.y // other, self.z // other)
    
    def __truediv__(self, other: Color | float | int) -> Color:
        if isinstance(other, Color):
            return Color(self.x / other.x, self.y / other.y, self.z / other.z)
        return Color(self.x / other, self.y / other, self.z / other)
    
    def __mod__(self, other: Color | float | int) -> Color:
        if isinstance(other, Color):
            return Color(self.x % other.x, self.y % other.y, self.z % other.z)
        return Color(self.x % other, self.y % other, self.z % other)
    
    def __radd__(self, other: Color) -> Color:
        return self.__add__(other)
    
    def __rsub__(self, other: Color) -> Color:
        return self.__sub__(other)
    
    def __rmul__(self, other: Color | float | int) -> Color:
        return self.__mul__(other)
    
    def __rfloordiv__(self, other: Color | float | int) -> Color:
        return self.__floordiv__(other)
    
    def __rtruediv__(self, other: Color | float | int) -> Color:
        return self.__truediv__(other)
    
    def __rmod__(self, other: Color | float | int) -> Color:
        return self.__mod__(other)
    
    def as_tuple(self, shift: int | float = 255, intensity: Interval = Interval(0, 1)) -> tuple[float, float, float]:
        return (
            int(shift * intensity.clamp(self.r_sqrt)), 
            int(shift * intensity.clamp(self.g_sqrt)), 
            int(shift * intensity.clamp(self.b_sqrt))
        )
    
    @property
    def r(self) -> float:
        return self.x

    @property
    def g(self) -> float:
        return self.y

    @property
    def b(self) -> float:
        return self.z
    
    @property
    def r_sqrt(self) -> float:
        return sqrt(self.r)
    
    @property
    def g_sqrt(self) -> float:
        return sqrt(self.g)
    
    @property
    def b_sqrt(self) -> float:
        return sqrt(self.b)
    
    # --< Class Methods >-- #
    @classmethod
    def average(cls, *clr: Color) -> Color:
        return (sum(*clr)) / len(*clr)
    
    # --< Default / Common Colors >-- #
    @classmethod
    def WHITE(cls) -> Color:
        return cls(1, 1, 1)
    
    @classmethod
    def GRAY(cls) -> Color:
        return cls(0.5, 0.5, 0.5)
    
    @classmethod
    def BLACK(cls) -> Color:
        return cls(0, 0, 0)
    
    @classmethod
    def RED(cls) -> Color:
        return cls(1, 0, 0)
    
    @classmethod
    def GREEN(cls) -> Color:
        return cls(0, 1, 0)
    
    @classmethod
    def BLUE(cls) -> Color:
        return cls(0, 0, 1)
    