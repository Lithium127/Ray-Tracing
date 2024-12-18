from __future__ import annotations
import typing as t

from .color import Color
from .skybox import SkyBox, Lerp
from .assets.hittable import HitRecord, Interval, BVHNode
from .vec3 import Vector3
from .ray import Ray

if t.TYPE_CHECKING:
    from os import PathLike
    from .assets.hittable import Hittable


_MIN_INTERVAL_DIFFERENCE = 0.001

class Scene(object):
    """A collection of hittable objects and a skybox that can be rendered with a camera"""
    
    assets: list[Hittable]
    skybox: SkyBox
    
    def __init__(self, assets: list[Hittable], skybox: SkyBox = Lerp(Color(0.7, 0.5, 1.0), Color(1.0, 1.0, 1.0))) -> None:
        """Creates a list of hittable objects

        Args:
            assets (list[Hittable]): List of Assets for this scene to conatin
            skybox (SkyBox, optional): The skybox object that calculates a color for rays that don't hit anything. Defaults to Lerp(Color(0.7, 0.5, 1.0), Color(1.0, 1.0, 1.0)).
        """
        self.assets = []
        for asset in assets:
            self.add_asset(asset)
        self.skybox = skybox
    
    
    @classmethod
    def from_json(self, fp: PathLike) -> Scene:
        pass
    
    
    def add_asset(self, asset: Hittable) -> t.NoReturn:
        """Adds an Asset to this scene

        Args:
            asset (Hittable): Asset to add to scene
        """
        self.assets.append(asset)
        
    
    def clear(self) -> t.NoReturn:
        """Clears this scene removing all assets"""
        self.assets = []
    
    def hit(self, r: Ray, ray_t: Interval, rec: HitRecord) -> bool:
        """Returns True if Ray r hits any object in the scene and saves the closest hit
        to HitRecord rec

        Args:
            r (Ray): Ray to check
            ray_t (Interval): Interval to check
            rec (HitRecord): _description_

        Returns:
            bool: _description_
        """
        temp_rec = HitRecord()
        hit_anything = False
        
        for asset in self.assets:
            if asset.hit(r, ray_t, temp_rec):
                hit_anything = True
                ray_t.max = temp_rec.t
                rec.copy_data(temp_rec) # Copy all data into temp_rec
        
        return hit_anything
    
    def r_ray_color(self, r: Ray, rec: HitRecord, limit: int, depth: int = 0) -> Color:
        """A recursive copy of ray_color() that doesnt increase memory consumption
        and implements a bounce limit.

        Args:
            r (Ray): A ray cast through this scene
            rec (HitRecord): An already created and populated HitRecord
            limit (int): The bounce limit set by a camera object
            depth (int, optional): The current depth of the ray, to limit bounces. Defaults to 0.

        Returns:
            Color: The color of the ray.
        """
        if limit < depth:
            return Color(0, 0, 0)
        
        if self.hit(r, Interval(_MIN_INTERVAL_DIFFERENCE), rec):
            scattered = Ray(None, None)
            attenuation = Color(0, 0, 0)
            from_emission = rec.mat.emitted(rec.u, rec.v, rec.p)
            
            if not rec.mat.scatter(r, rec, attenuation, scattered):
                return from_emission
            
            from_scatter = attenuation * self.r_ray_color(scattered, rec, limit, depth + 1)
            return from_scatter + from_emission
        
        return self.skybox.get_color(r)
    
    def ray_color(self, r: Ray, limit: int) -> Color:
        """Propogates a ray through this scene and returns the color 

        Args:
            r (Ray): A ray cast through this scene
            limit (int): The bounce limit set by a camera object

        Returns:
            Color: The output color of Ray r
        """
        rec = HitRecord()
        
        if self.hit(r, Interval(_MIN_INTERVAL_DIFFERENCE), rec):
            scattered = Ray(None, None)
            attenuation = Color(0, 0, 0)
            from_emission = rec.mat.emitted(rec.u, rec.v, rec.p)
            
            if not rec.mat.scatter(r, rec, attenuation, scattered):
                return from_emission
            
            from_scatter = attenuation * self.r_ray_color(scattered, rec, limit)
            return from_scatter + from_emission
        
        return self.skybox.get_color(r)