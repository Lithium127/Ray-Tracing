from __future__ import annotations
import typing as t
from PIL import Image

from math import atan2, asin
from math import pi as PI
from .color import Color

if t.TYPE_CHECKING:
    import os
    from .ray import Ray


_PI_OVER_TWO = PI / 2
_TWO_PI = 2 * PI

class SkyBox(object):
    """
    The base class for a skybox, does nothing on its own 
    but all other skyboxes inherit from this one
    
    To write a custom skybox, a class must inherit from 
    this skybox object and override the get_color() method 
    which accepts a Ray and return a Color object. Then just 
    pass that skybox as a parameter to your scene and it 
    will be rendered whenever a ray doesn't hit anything
    """
    
    def __init__(self) -> None:
        ...
    
    def get_color(self, r: Ray) -> Color:
        """Returns the color of the skybox given a single ray

        Args:
            r (Ray): The ray that hits the skybox

        Returns:
            Color: The color of the skybox at that point
        """
        ...

class Lerp(SkyBox):
    """A skybox that linearly interpolates between two colors depending on ray angle"""
    
    c1: Color
    c2: Color
    
    def __init__(self, upper: Color, lower: Color) -> None:
        """Creates a skybox that linearly interpolates between an upper 
        color and a lower color depending on the direction of an input ray

        Args:
            upper (Color): The color at the top of the skybox
            lower (Color): The color at the bottom of the skybox
        """
        super(Lerp, self).__init__()
        self.c1 = upper
        self.c2 = lower
    
    def get_color(self, r: Ray) -> Color:
        unit_direction = r.direction.unit_vector
        a = 0.5*(unit_direction.y + 1.0)
        return (1.0-a) * self.c2 + a * self.c1

class Mono(SkyBox):
    """A skybox that returns a single color"""
    color: Color
    
    def __init__(self, color: Color) -> None:
        """Creates a skybox that returns a single color regardless of ray direction

        Args:
            color (Color): The color of the skybox
        """
        super(Mono, self).__init__()
        self.color = color
    
    def get_color(self, r: Ray) -> Color:
        return self.color


class Textured(SkyBox):
    
    _color_handle: t.Callable
    
    fp: os.PathLike
    img: Image.Image
    offset: tuple[float, float]
    mul: float
    
    def __init__(self, fp: os.PathLike, offsets: tuple[float, float] = (0, 0), mul: float = 1):
        super(Textured, self).__init__()
        self.fp = fp if not isinstance(fp, Image.Image) else None
        self.mul = mul
        
        if isinstance(fp, Image.Image):
            self.img = fp
        else:
            self.img = Image.open(fp)
        
        self._color_handle = {
            "L" : self._load_from_float,
            "P" : self._load_from_float,
            "RGBA" : self._load_from_rgba
        }.get(self.img.mode, self._load_from_rgb)
        
        self.offset = (
            offsets[0] * (self.img.width / 360),
            offsets[1] * (self.img.height / 180)
        )
    
    def get_color(self, r: Ray):
        direction = r.direction.unit_vector
        im = self.img
        
        phi = atan2(direction.z, direction.x)
        theta = asin(direction.y)
        
        u, v = (
            (phi + PI) / (_TWO_PI), 
            (theta - (_PI_OVER_TWO)) / PI
        )
        
        w, h, ox, oy = im.width, im.height, *self.offset
        albedo = im.getpixel((
            (int(u * w + ox)) % w, 
            -(int(v * h - oy)) % h
        ))
        return self._color_handle(albedo) * self.mul
        
    
    @staticmethod
    def _load_from_float(c: float) -> Color:
        return Color(c, c, c)
    
    
    @staticmethod
    def _load_from_rgb(c: tuple[float, float, float]) -> Color:
        return Color(*c) / 256
    
    
    @staticmethod
    def _load_from_rgba(c: tuple[float, float, float, float]) -> Color:
        return Color(*c[:2])