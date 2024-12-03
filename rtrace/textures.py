from __future__ import annotations
import typing as t

from PIL import Image

from .color import Color

if t.TYPE_CHECKING:
    from .vec3 import Point3
    from os import PathLike

__all__ = ["Texture", "SolidColor", "ImageMap"]

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
    """A solid color texture"""
    
    albedo: Color
    
    def __init__(self, albedo: Color) -> None:
        self.albedo = albedo
    
    def value(self, u: float, v: float, p: Point3) -> Color:
        return self.albedo


class ImageMap(Texture):
    """An image mapped to a texture"""
    
    _color_handle: t.Callable
    
    fp: PathLike
    img: Image.Image
    offset: tuple[int, int]
    
    
    def __init__(self, fp: PathLike | Image.Image, offsets: tuple[float, float] = (0, 0)):
        """Maps an image as a texture color texture for an object

        Args:
            fp (PathLike | Image): The path to an image or already loaded PIL.Image.Image()
            offsets (tuple[int, int], optional): The X, Y offsets in degrees for the image mapping. Defaults to (0, 0).
        """
        super().__init__()
        self.fp = fp if not isinstance(fp, Image.Image) else None
        
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
        
        
    def value(self, u: float, v: float, p: Point3) -> Color:
        im = self.img
        w, h, ox, oy = im.width, im.height, *self.offset
        albedo = im.getpixel((
             (int(u * w + ox)) % w, 
            -(int(v * h - oy)) % h
        ))
        return self._color_handle(albedo)


    @staticmethod
    def _load_from_float(c: float) -> Color:
        return Color(c, c, c)
    
    
    @staticmethod
    def _load_from_rgb(c: tuple[float, float, float]) -> Color:
        return Color(*c) / 256
    
    
    @staticmethod
    def _load_from_rgba(c: tuple[float, float, float, float]) -> Color:
        return Color(*c[:2])