from __future__ import annotations
import typing as t

from math import sqrt

from .vec3 import Vector3
from .color import Color
from .textures import SolidColor

if t.TYPE_CHECKING:
    from .vec3 import Point3
    from .textures import Texture
    from .hittable import HitRecord
    from .ray import Ray

class Material(object):
    """The base class for a Material"""
    
    def __init__(self) -> None:
        """Creates a base material without color that does not reflect"""
        ...
    
    def scatter(self, r_in: Ray, rec: HitRecord, attenuation: Color, scattered: Ray) -> bool:
        """Scatters a ray based off an input ray and hit record with the current attenuation

        Args:
            r_in (Ray): The incoming ray that hit this object
            rec (HitRecord): The record of the object hit
            attenuation (Color): The current color the ray is returning
            scattered (Ray): The scattered ray, modified within the function

        Returns:
            bool: Wheather or not this material scatters a ray
        """
        return False
    
    def emitted(self, u: float, v: float, p: Point3) -> Color:
        """Returns the intensity of emmisive lighting from this material
        based of the color of its texture at point (u, v)

        Args:
            u (float): The y position to sample
            v (float): The x position to sample
            p (Point3): The point of intersection with the object

        Returns:
            Color: The amount of emitted light
        """
        return Color(0, 0, 0)
    
    
class Lambertian(Material):
    """A material with perfectly random reflections"""
    
    texture: Texture
    
    def __init__(self, texture: Color | Texture):
        """A material that reflects light randomly and emits no light

        Args:
            texture (Color | Texture): The texture or color for the material to use
        """
        if isinstance(texture, Color):
            texture = SolidColor(texture)
        self.texture = texture
    
    def scatter(self, r_in, rec, attenuation, scattered):
        scatter_dir = rec.normal + Vector3.random_unit_vector()
        
        if scatter_dir.near_zero:
            scatter_dir = rec.normal
        
        scattered.origin = rec.p
        scattered.direction = scatter_dir
        albedo = self.texture.value(rec.u, rec.v, rec.p)
        attenuation.x, attenuation.y, attenuation.z = albedo.x, albedo.y, albedo.z
        return True
        

class Metal(Material):
    """A metallic material"""
    
    texture: Texture
    fuzz: float
    
    def __init__(self, texture: Color | Texture, fuzz: float = 0.0):
        """A material that reflects light perfecty across the normal of a hit
        and emits no light
        
        Creates a metallic look for materials

        Args:
            texture (Color | Texture): The texture of color for the material
            fuzz (float, optional): How much a ray should deviate from perfect reflection. Higher values mean less shiny, must be between 0 - 1. Defaults to 0.0.
        """
        if isinstance(texture, Color):
            texture = SolidColor(texture)
        self.texture = texture
        self.fuzz = fuzz
    
    def scatter(self, r_in, rec, attenuation, scattered):
        reflected = Vector3.reflect(r_in.direction, rec.normal)
        reflected = reflected.unit_vector + (self.fuzz * Vector3.random_unit_vector())
        
        scattered.origin, scattered.direction = rec.p, reflected
        
        albedo = self.texture.value(rec.u, rec.v, rec.p)
        attenuation.x, attenuation.y, attenuation.z = albedo.x, albedo.y, albedo.z
        
        return (Vector3.dot(scattered.direction, rec.normal) > 0)

class Dielectric(Material):
    """A glass-like material"""
    refraction_index: float
    texture: Texture
    
    def __init__(self, reflection_index: float, texture: Color | Texture = Color.WHITE()):
        """A material that refracts light similar to glass
        
        Use known reflection indexes to create materials

        Args:
            reflection_index (float): The number to determine how much a ray should refract, see wikipedia for how this works and for indexes of common materials
            texture (Color | Texture, optional): The texture or color for the material. Defaults to Color.WHITE().
        """
        if isinstance(texture, Color):
            texture = SolidColor(texture)
        self.texture = texture
        self.refraction_index = reflection_index
    
    def scatter(self, r_in, rec, attenuation, scattered):
        
        albedo = self.texture.value(rec.u, rec.v, rec.p)
        attenuation.x, attenuation.y, attenuation.z = albedo.x, albedo.y, albedo.z
        
        
        ri = (1/self.refraction_index) if rec.front_face else self.refraction_index
        unit_direction = r_in.direction.unit_vector
        
        cos_theta = min(Vector3.dot(-unit_direction, rec.normal), 1.0)
        sin_theta = sqrt(1.0 - cos_theta*cos_theta)
        
        direction: Vector3
        if (ri * sin_theta) > 1.0:
            direction = Vector3.reflect(unit_direction, rec.normal)
        else:
            direction = Vector3.refract(unit_direction, rec.normal, ri)
        
        scattered.origin, scattered.direction = rec.p, direction
        
        return True
    
    @classmethod
    def Glass(cls, texture: Color | Texture = Color.WHITE()) -> Material:
        """Returns a Dielectric material with a refractive index similar to glass

        Args:
            texture (Color | Texture, optional): The texture or color of the material. Defaults to Color.WHITE().

        Returns:
            Material: The glass material
        """
        return cls(1.50, texture)



class VectorShade(Material):
    """(WIP) - Shades an object based on the normal vector of the hit"""
    albedo: Color
    reflection_rules: Material
    
    def __init__(self, *, rlike: Material | None = None) -> None:
        raise NotImplementedError()
        self.albedo = Color(1, 1, 1)
        self.reflection_rules = rlike
    
    def scatter(self, r_in, rec, attenuation, scattered):
        c_at = 0.2 * (rec.normal + Vector3(1, 1, 1))
        attenuation.x, attenuation.y, attenuation.z = c_at.x, c_at.y, c_at.z
        if self.reflection_rules is not None:
            return self.reflection_rules.scatter(r_in=r_in, rec=rec, attenuation=Color.BLACK(), scattered=scattered)
        return False
    


class MonoShade(Material):
    """(WIP) - Shades an object with a single color and does not propogate rays"""
    
    albedo: Color
    
    def __init__(self, albedo: Color):
        raise NotImplementedError()
        self.albedo = albedo
    
    def scatter(self, r_in, rec, attenuation, scattered):
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
        return False
    


class DiffuseLight(Material):
    """Makes an object emit light to the scene around it"""
    
    texture: Texture
    intensity: Color
    
    def __init__(self, intensity: float, texture: Color | Texture = Color(1, 1, 1)) -> None:
        """A material that emits light into the scene on to other objects
        when using this material it is reccommended to use a high ray sample per pixel
        to alliviate noisiness
        
        The object emits light by random rays bouncing into the object

        Args:
            intensity (float): The intensity of the light, greater than 1 (>1) will light up more than just the object itself
            texture (Color | Texture, optional): The texure or color this object should use, affects how much light is emitted. Defaults to white.
        """
        self.texture = texture
        if isinstance(texture, Color):
            self.texture = SolidColor(texture)
            
        self.intensity = Color(intensity, intensity, intensity)
    
    def emitted(self, u: float, v: float, p: Point3):
        return self.texture.value(u, v, p) * self.intensity



class MonoDirectionalScatter(Material):
    """(WIP) - Attempts to scatter all incoming rays opposite the normal direction of this object"""
    scatter_dir: Vector3
    
    def __init__(self, direction: Vector3):
        raise NotImplementedError()
        self.scatter_dir = direction
    
    def scatter(self, r_in, rec, attenuation, scattered):
        scattered.origin, scattered.direction = rec.p, self.scatter_dir
        return True