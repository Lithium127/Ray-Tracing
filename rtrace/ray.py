from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from .vec3 import Vector3, Point3


class Ray(object):
    """Representa a ray with an origin and a direction"""
    origin: Vector3
    direction: Vector3
    
    def __init__(self, origin: Point3, dir: Vector3) -> None:
        """Creates a ray object at some origin pointing in some direction

        Args:
            origin (Point3): The origin of the ray
            dir (Vector3): The direction of the ray, not relative to the origin
        """
        self.origin = origin
        self.direction = dir
    
    def at(self, t: float | int) -> Point3:
        """Calculates the position of the ray at some distance :t:

        Args:
            t (float | int): The 'time' or distance of sampling

        Returns:
            Point3: The position of the ray at time t
        """
        return self.origin + (t * self.direction)