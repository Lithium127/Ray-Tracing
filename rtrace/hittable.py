from __future__ import annotations
import typing as t

from math import sqrt, inf

from .vec3 import Point3, Vector3

if t.TYPE_CHECKING:
    from .ray import Ray
    from .materials import Material


# --< Utility Classes >-- #
class Interval:
    min: float
    max: float
    
    def __init__(self, min: int | float = -inf, max: int | float = inf) -> None:
        """Creates an interval between two numbers

        Args:
            min (int | float, optional): The minimum value. Defaults to -math.inf.
            max (int | float, optional): Maximum value. Defaults to math.inf.
        """
        self.min = min
        self.max = max
    
    def size(self) -> float:
        """The difference between min and max

        Returns:
            float: The size of the interval
        """
        return self.max - self.min
    
    def contains(self, x: float) -> bool:
        """Returns true if x is within the interval inclusive

        Args:
            x (float): Value to check

        Returns:
            bool: If that value is contained within the interval
        """
        return self.min <= x and x <= self.max
    
    def surrounds(self, x: float) -> bool:
        """Returns true if x is within the interval exclusively
        Does not include min and max.

        Args:
            x (float): Value to check

        Returns:
            bool: If the value is within the interval
        """
        return self.min < x and x < self.max
    
    def clamp(self, x: float) -> float:
        """Returns value x clamped between min and max

        Args:
            x (float): Value to clamp

        Returns:
            float: x if x is between min and max else min or max
        """
        if x < self.min: return self.min
        if x > self.max: return self.max
        return x
    
    @classmethod
    def empty(cls) -> Interval:
        """Creates an empty interval where the min is greater than the max resulting in no valid x values

        Returns:
            Interval: The interval instance
        """
        return cls(inf, -inf)
    
    @classmethod
    def universe(cls) -> Interval:
        """Creates an interval where all inputs are valid

        Returns:
            Interval: The interval instance
        """
        return cls(-inf, inf)

class HitRecord(object):
    
    p: Point3
    normal: Vector3
    mat: Material
    t: float
    front_face: bool
    
    def __init__(self):
        """Creates a record object to be passed into hit calculations and save data"""
        pass
    
    def copy_data(self, rec: HitRecord) -> t.NoReturn:
        """Copies all the data from one HitRecord rec into this instance

        Args:
            rec (HitRecord): Hit record to copy from
        """
        self.p = rec.p
        self.normal = rec.normal
        self.mat = rec.mat
        self.t = rec.t
        self.front_face = rec.front_face
    
    def set_face_normal(self, r: Ray, outward_normal: Vector3) -> t.NoReturn:
        """Sets the face normal for this object

        Args:
            r (Ray): The ray that intersects an object
            outward_normal (Vector3): The outward normal at the point of intersection
        """
        self.front_face = Vector3.dot(r.direction, outward_normal) < 0
        self.normal = outward_normal if self.front_face else (-1 * outward_normal)
    
    def bounding_box(self) -> None:
        """Returns the calculated bounding box to simplify optimizations

        Raises:
            NotImplementedError: This method is not implemented yet
        """
        raise NotImplementedError()




# --< Hittable Assets >-- #
class Hittable(object):
    """The base hittable class for assets in a scene to inherit from"""
    
    center: Point3
    
    def __init__(self, center: Point3):
        """Creates an instance of the base hittable class
        The base class will never be hittable, please use subclasses

        Args:
            center (Point3): The center of the object
        """
        self.center = center
    
    def hit(self, r: Ray, interval: Interval, h: HitRecord) -> bool:
        """Should return True when if Ray r hit the object within the specified interval
        all data is saved in the hitrecord h parameter

        Args:
            r (Ray): The ray instance to check for intersection
            interval (Interval): Preffered intersection
            h (HitRecord): HitRecord instance to save hit info to

        Returns:
            bool: If the object was hit or not
        """
        return False

class Sphere(Hittable):
    # Transfer to an exposed .cpp file
    
    radius: float
    mat: Material
    
    def __init__(self, center: Point3, radius: float, mat: Material) -> None:
        """Creates a sphere instance

        Args:
            center (Point3): Where the sphere is positioned in 3D space
            radius (float): The radius of the sphere
        """
        super(Sphere, self).__init__(center)
        self.radius = radius
        self.mat = mat
    
    def hit(self, r: Ray, ray_t: Interval, rec: HitRecord) -> bool:
        """Returns True if Ray r hits this sphere within the interval ray_t
        Saves hit information to hit record rec

        Args:
            r (Ray): Ray instance to check hit for
            ray_t (Interval): The interval for valid hits
            rec (HitRecord): HitRecord instance to save hit data to

        Returns:
            bool: If ray r hits this sphere
        """
        oc = self.center - r.origin
        
        # This area could use some major performance boosts
        
        # Calcualted values for quadratic
        a = r.direction.length_squared
        h = Vector3.dot(r.direction, oc)
        c = oc.length_squared - (self.radius * self.radius)
        
        # Check if there are any zeros / intersections at all
        # using the first part of the quadratic formula?
        discriminant = (h * h) - (a * c)
        if discriminant < 0:
            return False
        
        # Check to see if either calculated root is within the selected interval
        sqrtd = sqrt(discriminant)
        root = (h - sqrtd) / a
        if not ray_t.surrounds(root):
            root = (h + sqrtd) / a
            if not ray_t.surrounds(root):
                return False
        
        # Save data to hitrec
        rec.t = root
        rec.p = r.at(root)
        rec.set_face_normal(r, (rec.p - self.center) / self.radius)
        rec.mat = self.mat
        
        return True
        
        
        