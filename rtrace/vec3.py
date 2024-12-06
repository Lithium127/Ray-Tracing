from __future__ import annotations
import typing as t
import math
from random import uniform

class Vector3(object):
    """A vector object in 3D space, usually a direction"""

    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float) -> None:
        """An object representing a vector in 3D space, usually direction

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate
        """
        self.x = x
        self.y = y
        self.z = z
    
    def __pos__(self) -> Vector3:
        return self.__class__(+self.x, +self.y, +self.z)
    
    def __neg__(self) -> Vector3:
        return self.__class__(-self.x, -self.y, -self.z)
    
    def __abs__(self) -> Vector3:
        return self.__class__(abs(self.x), abs(self.x), abs(self.x))
    
    def __add__(self, other: Vector3) -> Vector3:
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: Vector3) -> Vector3:
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other: Vector3 | float | int) -> Vector3:
        if isinstance(other, Vector3):
            return self.__class__(self.x * other.x, self.y * other.y, self.z * other.z)
        return self.__class__(self.x * other, self.y * other, self.z * other)
    
    def __floordiv__(self, other: Vector3 | float | int) -> Vector3:
        if isinstance(other, Vector3):
            return self.__class__(self.x // other.x, self.y // other.y, self.z // other.z)
        return self.__class__(self.x // other, self.y // other, self.z // other)
    
    def __truediv__(self, other: Vector3 | float | int) -> Vector3:
        if isinstance(other, Vector3):
            return self.__class__(self.x / other.x, self.y / other.y, self.z / other.z)
        return self.__class__(self.x / other, self.y / other, self.z / other)
    
    def __mod__(self, other: Vector3 | float | int) -> Vector3:
        if isinstance(other, Vector3):
            return self.__class__(self.x % other.x, self.y % other.y, self.z % other.z)
        return self.__class__(self.x % other, self.y % other, self.z % other)
    
    def __radd__(self, other: Vector3) -> Vector3:
        return self.__add__(other)
    
    def __rsub__(self, other: Vector3) -> Vector3:
        return self.__sub__(other)
    
    def __rmul__(self, other: Vector3 | float | int) -> Vector3:
        return self.__mul__(other)
    
    def __rfloordiv__(self, other: Vector3 | float | int) -> Vector3:
        return self.__floordiv__(other)
    
    def __rtruediv__(self, other: Vector3 | float | int) -> Vector3:
        return self.__truediv__(other)
    
    def __rmod__(self, other: Vector3 | float | int) -> Vector3:
        return self.__mod__(other)
    
    def __iadd__(self, other: Vector3) -> Vector3:
        return NotImplemented
    
    @property
    def length(self) -> float:
        """The length of the vector"""
        return math.sqrt(self.length_squared)
    
    @property
    def length_squared(self) -> float:
        """The length of the vector, squared"""
        return (self.x * self.x) + (self.y * self.y) + (self.z * self.z)
    
    @property
    def unit_vector(self) -> Vector3:
        """Returns a new vector with the same direction, normalized to between 1 and 0"""
        return self / self.length
    
    @property
    def near_zero(self) -> bool:
        """Returns true if this vector is near zero"""
        s = 1e-8 # A very small constant
        return (abs(self.x) < s) and (abs(self.y) < s) and (abs(self.z) < s)
    
    @classmethod
    def dot(cls, v1: Vector3, v2: Vector3) -> float:
        """Take the dot product of two vectors

        Args:
            v1 (Vector3): Vector 1
            v2 (Vector3): Vector 2

        Returns:
            float: The dot product of v1 and v2
        """
        return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)
    
    @classmethod
    def cross(cls, v1: Vector3, v2: Vector3) -> Vector3:
        """Calculate the cross product of two vectors

        Args:
            v1 (Vector3): Vector 1
            v2 (Vector3): Vector 2

        Returns:
            Vector3: The vector containing the cross product of v1 and v2
        """
        return cls(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x
        )
    
    @classmethod
    def random(cls, min: float = 0.0, max: float = 1.0) -> Vector3:
        """Generates a random vector with length in all directions in a range of min and max

        Args:
            min (float, optional): The minimum value to generate. Defaults to 0.0.
            max (float, optional): The maximum allowed value. Defaults to 1.0.

        Returns:
            Vector3: The random vector
        """
        return cls(
            uniform(min, max),
            uniform(min, max),
            uniform(min, max)
        )
    
    @classmethod
    def random_unit_vector(cls) -> Vector3:
        """Generates a random vector with a length of 1
        essentially just a vector pointing in a random direction

        Returns:
            Vector3: The randomized vector
        """
        while True:
            p = Vector3.random(-1, 1)
            lensq = p.length_squared
            # The constant here just checks for arbitrarialy 
            # small vectors that can't be normalized
            if 1e-160 < lensq and lensq <= 1:
                return p / math.sqrt(lensq)
    
    @classmethod
    def random_on_hemisphere(cls, normal: Vector3) -> Vector3:
        """Generates a random vector that is contained within a 
        hemisphere around a normal vector

        Args:
            normal (Vector3): The normal of some surface

        Returns:
            Vector3: A random vector on that hemisphere
        """
        on_unit_sphere = Vector3.random_unit_vector()
        if Vector3.dot(on_unit_sphere, normal) > 0:
            return on_unit_sphere
        else:
            return -on_unit_sphere
    
    @classmethod
    def random_on_unit_disc(cls) -> Vector3:
        """Generates a random vector that is pointed at the edge
        of a disc (x, y)

        Returns:
            Vector3: A random vector on a disc
        """
        while True:
            p = Vector3(uniform(-1, 1), uniform(-1, 1), 0)
            if p.length_squared < 1:
                return p
    
    @classmethod
    def reflect(cls, v: Vector3, n: Vector3) -> Vector3:
        """Reflects a vector v over the normal n

        Args:
            v (Vector3): The vector origin to reflect
            n (Vector3): The normal to reflect over

        Returns:
            Vector3: The reflected vector
        """
        return v - (2 * Vector3.dot(v, n) * n)
    
    @classmethod
    def refract(cls, uv: Vector3, n: Vector3, etai_over_etat: float) -> Vector3:
        """Calculates the refraction of a vector uv through a surface over
        the normal n with a set refraction index

        Args:
            uv (Vector3): The incoming vector
            n (Vector3): The normal of the surface
            etai_over_etat (float): The refractive index

        Returns:
            Vector3: The refracted vector
        """
        cos_theta = min(Vector3.dot(-uv, n), 1.0)
        r_out_perp = etai_over_etat * (uv + cos_theta*n)
        r_out_parallel = -math.sqrt(abs(1.0 - r_out_perp.length_squared)) * n
        return r_out_perp + r_out_parallel

class Point3(Vector3):
    """The exact same as a vector3 internally, just represents a point in 3D space."""
    pass # Exists just for readability