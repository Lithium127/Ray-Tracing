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
    
    def __init__(self) -> None:
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
            p (Point3): _description_

        Returns:
            Color: _description_
        """
        return Color(0, 0, 0)
    
    
class Lambertian(Material):
    
    texture: Texture
    
    def __init__(self, texture: Color | Texture):
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
    
    texture: Texture
    fuzz: float
    
    def __init__(self, texture: Color | Texture, fuzz: float = 0.0):
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
    
    refraction_index: float
    texture: Texture
    
    def __init__(self, reflection_index: float, texture: Color | Texture = Color.WHITE()):
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

        Returns:
            Material: The glass material
        """
        return cls(1.50, texture)



class VectorShade(Material):
    """Shades an object based on the normal vector of the hit"""
    albedo: Color
    reflection_rules: Material
    
    def __init__(self, *, rlike: Material | None = None) -> None:
        self.albedo = Color(1, 1, 1)
        self.reflection_rules = rlike
    
    def scatter(self, r_in, rec, attenuation, scattered):
        c_at = 0.2 * (rec.normal + Vector3(1, 1, 1))
        attenuation.x, attenuation.y, attenuation.z = c_at.x, c_at.y, c_at.z
        if self.reflection_rules is not None:
            return self.reflection_rules.scatter(r_in=r_in, rec=rec, attenuation=Color.BLACK(), scattered=scattered)
        return False
    


class MonoShade(Material):
    """Shades an object with a single color and does not propogate rays"""
    
    albedo: Color
    
    def __init__(self, albedo: Color):
        self.albedo = albedo
    
    def scatter(self, r_in, rec, attenuation, scattered):
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
        return False
    


class DiffuseLight(Material):
    
    texture: Texture
    intensity: Color
    
    def __init__(self, intensity: float, texture: Color | Texture = Color(1, 1, 1)) -> None:
        if isinstance(texture, Color):
            self.texture = SolidColor(texture)
            
        self.intensity = Color(intensity, intensity, intensity)
    
    def emitted(self, u: float, v: float, p: Point3):
        return self.texture.value(u, v, p) * self.intensity