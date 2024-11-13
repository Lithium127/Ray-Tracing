from __future__ import annotations
import typing as t
from PIL import Image

if t.TYPE_CHECKING:
    import os
    from .ray import Ray
    from .color import Color

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
    
    fp: os.PathLike
    texture: Image.Image
    
    def __init__(self, texture_path: os.PathLike):
        super(Textured, self).__init__()
    
    def get_color(self, r: Ray):
        return Color.BLACK()
        