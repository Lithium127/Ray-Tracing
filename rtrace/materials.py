from __future__ import annotations
import typing as t

from math import sqrt

from .vec3 import Vector3
from .color import Color

if t.TYPE_CHECKING:
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
    
    
class Lambertian(Material):
    
    albedo: Color
    
    def __init__(self, albedo: Color):
        self.albedo = albedo
    
    def scatter(self, r_in, rec, attenuation, scattered):
        scatter_dir = rec.normal + Vector3.random_unit_vector()
        
        if scatter_dir.near_zero:
            scatter_dir = rec.normal
        
        scattered.origin = rec.p
        scattered.direction = scatter_dir
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
        return True
        

class Metal(Material):
    
    albedo: Color
    fuzz: float
    
    def __init__(self, albedo: Color, fuzz: float = 0.0):
        self.albedo = albedo
        self.fuzz = fuzz
    
    def scatter(self, r_in, rec, attenuation, scattered):
        reflected = Vector3.reflect(r_in.direction, rec.normal)
        reflected = reflected.unit_vector + (self.fuzz * Vector3.random_unit_vector())
        
        scattered.origin, scattered.direction = rec.p, reflected
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
        return (Vector3.dot(scattered.direction, rec.normal) > 0)

class Dielectric(Material):
    
    refraction_index: float
    albedo: Color
    
    def __init__(self, reflection_index: float, albedo = Color.WHITE()):
        self.refraction_index = reflection_index
        self.albedo = albedo
    
    def scatter(self, r_in, rec, attenuation, scattered):
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
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
    def Glass(cls, albedo: Color = Color.WHITE()) -> Material:
        """Returns a Dielectric material with a refractive index similar to glass

        Returns:
            Material: The glass material
        """
        return cls(1.50, albedo)



class VectorShade(Material):
    """Shades an object based on the normal vector of the hit"""
    albedo: Color
    
    def __init__(self) -> None:
        self.albedo = Color(1, 1, 1)
    
    def scatter(self, r_in, rec, attenuation, scattered):
        c_at = 0.5 * (rec.normal + Vector3(1, 1, 1))
        attenuation.x, attenuation.y, attenuation.z = c_at.x, c_at.y, c_at.z
        return False


class MonoShade(Material):
    """Shades an object with a single color and does not propogate rays"""
    
    albedo: Color
    
    def __init__(self, albedo: Color):
        self.albedo = albedo
    
    def scatter(self, r_in, rec, attenuation, scattered):
        attenuation.x, attenuation.y, attenuation.z = self.albedo.x, self.albedo.y, self.albedo.z
        return False