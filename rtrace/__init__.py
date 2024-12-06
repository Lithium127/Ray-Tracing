"""
This code was created with reference to the mathematical formulas and 
structure from the book Ray Tracing in One Weekend cited at the bottom 
of the documentation

---
Citations:

Ray Tracing in One Weekend. raytracing.github.io/books/RayTracingInOneWeekend.html
Accessed 11 11. 2024.
"""

from .camera import Camera
from .scene import Scene
from .color import Color
from .vec3 import Point3, Vector3

from . import skybox as SkyBox
from .assets import hittable as Assets
from .assets import materials as Mat
from .assets import textures as Texture