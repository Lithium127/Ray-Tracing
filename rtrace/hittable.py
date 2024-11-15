from __future__ import annotations
import typing as t

from math import sqrt, inf
from random import choice

from .vec3 import Point3, Vector3

if t.TYPE_CHECKING:
    from .materials import Material
    from .ray import Ray


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
    
    def expand(self, delta: float) -> Interval:
        """Expands a select interval by some delta, the delta is 
        the total change, so each side is increased by half the delta

        Args:
            delta (float): The total change to increase by

        Returns:
            Interval: A new interval expanded by delta
        """
        padding = delta / 2
        return Interval(self.min - padding, self.max - padding)
    
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
    
    @classmethod
    def from_intervals(cls, a: Interval, b: Interval) -> Interval:
        return cls(min(a.min, b.min), max(a.max, b.max))

class HitRecord(object):
    
    p: Point3
    normal: Vector3
    mat: Material
    t: float
    front_face: bool
    
    def __init__(self):
        """Creates a record object to be passed into hit calculations and save data"""
        self.p = None
        self.normal = None
        self.mat = None
        self.t = None
        self.front_face = None
    
    def copy_data(self, rec: HitRecord) -> t.NoReturn:
        """Copies all the data from one HitRecord rec into this instance

        Args:
            rec (HitRecord): Hit record to copy from
        """
        self.__dict__.update(rec.__dict__)
    
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
    bbox: AABB
    
    def __init__(self, center: Point3):
        """Creates an instance of the base hittable class
        The base class will never be hittable, please use subclasses

        Args:
            center (Point3): The center of the object
        """
        self.center = center
    
    def hit(self, r: Ray, ray_t: Interval, rec: HitRecord) -> bool:
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
    
    def bounding_box(self) -> AABB:
        return self.bbox

class AABB:
    """Represents an Axis-Aligned Bounding Box (AABB)"""
    x: Interval
    y: Interval
    z: Interval
    
    def __init__(self, x: Interval, y: Interval, z: Interval) -> None:
        """Creates a box within the intervals x, y, z

        Args:
            x (Interval): The x interval
            y (Interval): The y interval
            z (Interval): The z interval
        """
        self.x = x
        self.y = y
        self.z = z
    
    @classmethod
    def from_points(cls, a: Point3, b: Point3) -> AABB:
        """Creates a bounding box from two points in space

        Args:
            a (Point3): A point in space
            b (Point3): A different point in space

        Returns:
            AABB: The bounding box between the two corners
        """
        return cls(
            Interval(a.x, b.x) if a.x <= b.x else Interval(b.x, a.x),
            Interval(a.y, b.y) if a.y <= b.y else Interval(b.y, a.y),
            Interval(a.z, b.z) if a.z <= b.z else Interval(b.z, a.z), 
        )
    
    @classmethod
    def from_box(cls, box0: AABB, box1: AABB) -> AABB:
        return cls(
            Interval.from_intervals(box0.x, box1.x),
            Interval.from_intervals(box0.y, box1.y),
            Interval.from_intervals(box0.z, box1.z),
        )
    
    def _axis_interval(self, r: Ray) -> t.Generator[Interval, Vector3, Point3]:
        """Creates axis aligned pairs from Interval and a ray

        Args:
            r (Ray): The ray to target

        Yields:
            Iterator[t.Generator[Interval, Vector3, Point3]]: Axis aligned pairs
        """
        orig = r.origin
        r_dir = r.direction
        for i in range(3):
            if i == 0:
                yield (self.x, r_dir.x, orig.x)
            if i == 1:
                yield (self.y, r_dir.y, orig.y)
            if i == 2:
                yield (self.z, r_dir.z, orig.z)
    
    def hit(self, r: Ray, ray_t: Interval) -> bool:
        
        for ax, r_dir, orig in self._axis_interval(r):
            adinv = 1.0 / r_dir
            
            t0, t1 = ((ax.min - orig) * adinv), ((ax.max - orig) * adinv)
            
            if (t0 < t1):
                ray_t.min = min(ray_t.min, t0)
                ray_t.max = max(ray_t.max, t1)
            else:
                ray_t.min = min(ray_t.min, t1)
                ray_t.max = max(ray_t.max, t0)
            
            if ray_t.max < ray_t.min:
                return False
    
        return True
            

class BVHNode(Hittable):
    
    left: Hittable
    right: Hittable
    
    def __init__(self, asset_list: list[Hittable], start: int = 0, end: int | None = None) -> None:
        """Creates a Bounding Volume Hierarchy that contains objects within bouding boxes
        REFACTOR REQUESTED

        Args:
            asset_list (list[Hittable]): A list of assets to enclose
            start (int, optional): The start index for tree generation. Defaults to 0.
            end (int | None, optional): The end index for tree generation. Defaults to None.
        """

        end = end or len(asset_list)
        # Comparators should be lambda functions
        comparator = choice([
            self.box_x_compare,
            self.box_y_compare,
            self.box_z_compare,
        ])
        
        object_span = end - start
        
        # Recursively create BVH Nodes until the entire space is filled
        if object_span == 1:
            self.left = self.right = asset_list[start]
        elif object_span == 2:
            self.left = asset_list[start]
            self.right = asset_list[start + 1]
        else:
            asset_list.sort(key = comparator)
            # Refactor this to slice the asset_list list instead of passinng indexes
            mid = start + (object_span // 2)
            self.left = BVHNode(asset_list, start, mid)
            self.right = BVHNode(asset_list, mid, end)

        # Create a new bounding box for this object
        self.bbox = AABB.from_box(self.left.bbox, self.right.bbox)
    
    def __str__(self) -> str:
        return f"<BVH : [{self.left}|{self.right}]>"
    
    def hit(self, r: Ray, ray_t: Interval, rec: HitRecord):
        
        if not self.bbox.hit(r, ray_t):
            return False
        
        temp_rec = rec
        
        hit_left = self.left.hit(r, ray_t, temp_rec)
        hit_right = self.right.hit(r, Interval(ray_t.min, (rec.t if hit_left else ray_t.max)), temp_rec)
        
        if (hit_left or hit_right):
            rec.copy_data(temp_rec)
            return True
        return False
        


    def box_x_compare(self, asset: Hittable) -> None:
        return asset.bbox.x.min
    
    def box_y_compare(self, asset: Hittable) -> None:
        return asset.bbox.y.min
    
    def box_z_compare(self, asset: Hittable) -> None:
        return asset.bbox.z.min
    
class HittableList(Hittable):
    
    assets: list[Hittable]
    
    def __init__(self, objects: list[Hittable] | None = None):
        super().__init__(Point3(0, 0, 0))
        self.assets = []
        if objects is not None:
            [self.add_asset(obj) for obj in objects]
    
    def add_asset(self, asset: Hittable) -> None:
        if len(self.assets) < 1:
            self.center = asset.center
        self.assets.append(asset)
        self.bbox = AABB.from_box(self.bbox, asset.bbox)
    
    def hit(self, r: Ray, ray_t: Interval, rec: HitRecord) -> bool:
        return super().hit(r, ray_t, rec)

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
        
        rvec = Point3(radius, radius, radius)
        self.bbox = AABB.from_points(rvec, -rvec)
    
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
        
        
        