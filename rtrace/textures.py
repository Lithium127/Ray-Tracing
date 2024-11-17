from __future__ import annotations
import typing as t


if t.TYPE_CHECKING:
    from .vec3 import Point3
    from .color import Color

class Texture(object):
    """Parent class for all textures"""
    
    def __init__(self) -> None:
        """The base class for all texture classes, DO NOT USE"""
        ...
    
    def value(self, u: float, v: float, p: Point3) -> Color:
        """Returns the color of this texture at point (u, v)

        Args:
            u (float): The y position to sample
            v (float): The x position to sample
            p (Point3): The point of contact in 3D space

        Returns:
            Color: The color of this texture at the point (u, v)
        """
        ...

class SolidColor(Texture):
    
    albedo: Color
    
    def __init__(self, albedo: Color) -> None:
        self.albedo = albedo
    
    def value(self, u: float, v: float, p: Point3) -> Color:
        return self.albedo