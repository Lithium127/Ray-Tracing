"""
This module exists just to wrap the rtrace library
to make it much simpler to use

scripts will modify exactly one scene
"""
from __future__ import annotations
import typing as t
import sys

import rtrace

# Image Information
RENDER_IMG_WIDTH    = 768
RENDER_ASPECT_RATIO = 16/9
SAVE_PATH = "images"
FILE_NAME = "current_workspace_render"

# Rendering Quality
SAMPLES_PER_PIXEL = 4
RAY_BOUNCE_LIMIT  = 16

# Camera Data
CAMERA_CENTER  = rtrace.Point3(0, 1, 2)
CAMERA_LOOK_AT = rtrace.Point3(0, 0, 0)
FIELD_OF_VIEW  = 90
DRAW_SILENT    = False
MULTIPROCESS   = True

# Workspace Constants
TEXTURE_DIRECTORY = "textures/"
MODEL_DIRECTORY = "models/"

# Create scene
SCENE = rtrace.Scene(
    [],
    rtrace.SkyBox.Textured(
        fp      = "textures/rogland_clear_night.jpg",
        offsets = (0, 0),
        mul     = 0.5
    )
)


class Material(object):
    """A set of common material constructors"""
    
    @staticmethod
    def default(color: tuple[float, float, float] = (1, 1, 1)) -> rtrace.Mat.Material:
        """Creates a basic material that reflects randomly,
        use for the `material` parameter of assets
        
        Usage:
        >>> Material.default(<color>)
        
        Args:
            color (tuple[float, float, float]): The color of the object ordered `(R, G, B)`

        Returns:
            rtrace.Mat.Material: A material instance
        """
        return rtrace.Mat.Lambertian(
            rtrace.Color(*color)
        )
    
    @staticmethod
    def metal(color: tuple[float, float, float] = (0.5, 0.5, 0.5), fuzz: float = 0) -> rtrace.Mat.Metal:
        """Gives an object a metal-like appearance

        Args:
            color (tuple[float, float, float], optional): The color of the object ordered `(R, G, B)`. Defaults to (128, 128, 128).
            fuzz (float, optional): How 'fuzzy' the surface is, lower numbers result in a cleaner reflection. Defaults to 0.

        Returns:
            rtrace.Mat.Metal: A material instance
        """
        fuzz = min(1, max(fuzz, 0))
        return rtrace.Mat.Metal(
            rtrace.Color(*color),
            fuzz
        )
    
    @staticmethod
    def image(img_name: t.Literal["checkerboard", "earth", "sun"]) -> rtrace.Mat.Material:
        """Maps an image to the object

        Args:
            img_name (Literal['checkerboard', 'earth', 'sun']): The image to use, must be in the afformentioned list

        Returns:
            rtrace.Mat.Material: The material of this object
        """
        filename = {
            "checkerboard" : "ArtificialTexture.png",
            "earth" : "Earth.jpg",
            "sun" : "Sun.jpg"
        }[img_name]
        return rtrace.Mat.Lambertian(
            rtrace.Texture.ImageMap(
                TEXTURE_DIRECTORY + filename
            )
        )
    


def add_sphere(center: tuple[float, float, float], radius: float, material: rtrace.Mat.Material = Material.default()) -> None:
    """Adds a sphere to the scene centered at a position with a radius
    and material
    
    set the material with the `material` class
    ```
    add_sphere(
        center = (0, 0, 0),
        radius = 0.5,
        material = Material.default(
            (255, 255, 255)
        )
    )
    ```

    Args:
        center (tuple[float, float, float]): The center of the object in 3d space ordered `(X, Y, Z)`
        radius (float): The radius of the sphere
        material (rtrace.Mat.Material): The material, look at the `Material` object for more info
    """
    SCENE.add_asset(
        rtrace.Assets.Sphere(
            center = rtrace.Point3(*center),
            radius = radius,
            mat = material
        )
    )

def add_cube(center: tuple[float, float, float], dimensions: tuple[float, float, float] = (0.5, 0.5, 0.5), material: rtrace.Mat.Material = Material.default()) -> None:
    """Adds a cube to the scene centered at a position scaled by
    the dimension parameter in all directions
    
    for example, this code will create a 1x1x1 cube centered at the origin
    ```
    add_cube(
        center = (0, 0, 0),
        dimensions = (1, 1, 1)
    )
    ```

    Args:
        center (tuple[float, float, float]): The center of the cube in 3d space
        dimensions (tuple[float, float, float], optional): The dimensions of each side of the cube ordered `(X, Y, Z)`. Defaults to (0.5, 0.5, 0.5).
        material (rtrace.Mat.Material, optional): The material, look at the `Material` object for more info. Defaults to Material.default().
    """
    center = rtrace.Point3(*center)
    half_dim = rtrace.Point3(*dimensions) / 2
    SCENE.add_asset(
        rtrace.Assets.Quad.Cube(
            a = center - half_dim,
            b = center + half_dim,
            mat = material
        )
    )


def add_plane(center: tuple[float, float, float], dim: tuple[float, float], axis: t.Literal["x", "y", "z"] = "y", material: rtrace.Mat.Material = Material.default()) -> None:
    """Adds a 2D plane to the scene centered at some point
    extending in a direction facing an axis
    
    Args:
        center (tuple[float, float, float]): The center of the plane
        dim (tuple[float, float]): The size of each of it's sides
        axis (Literal["x", "y", "z"], optional): The axis to face. Defaults to "y".
        material (rtrace.Mat.Material, optional): The material of this object. Defaults to Material.default().
    """
    raise NotImplementedError("This method has not yet been implemented")
    center = rtrace.Vector3(*center)
    
    SCENE.add_asset(
        rtrace.Assets.Quad(
            
        )
    )
    


def use_ground(material: rtrace.Mat.Material | None = None) -> None:
    """Adds a ground object to the scene

    Args:
        material (rtrace.Mat.Material, optional): The material of the ground object. Defaults to None.
    """
    SCENE.add_asset(
        rtrace.Assets.Sphere(
            center = rtrace.Point3(0, -100.5, 0),
            radius = 100,
            mat = rtrace.Mat.Lambertian(
                rtrace.Color.GRAY()
            )
        )
    )


def set_camera_target(pos: tuple[float, float, float]) -> None:
    """Sets the position the camera is looking at

    Args:
        pos (tuple[float, float, float]): The position of the camera target ordered `(X, Y, Z)`
    """
    global CAMERA_LOOK_AT
    CAMERA_LOOK_AT = rtrace.Point3(*pos)

def set_camera_center(pos: tuple[float, float, float]) -> None:
    """Sets the position of the camera in 3D space

    Args:
        pos (tuple[float, float, float]): The position of the camera ordered `(X, Y, Z)`
    """
    global CAMERA_CENTER
    CAMERA_CENTER = rtrace.Point3(*pos)


def set_camera_fov(fov: int | float) -> None:
    """Sets the field of view of the camera
    
    Args:
        fov (int | float): The field of view in degrees, ***must never exceed 180***
    """
    global FIELD_OF_VIEW
    FIELD_OF_VIEW = fov


def render():
    try:
        cam = rtrace.Camera(
            RENDER_IMG_WIDTH, 
            RENDER_ASPECT_RATIO, 
            CAMERA_CENTER,
            CAMERA_LOOK_AT,
            samples = SAMPLES_PER_PIXEL,
            recursion_limit = RAY_BOUNCE_LIMIT,
            fov = FIELD_OF_VIEW,
            use_multiprocess = MULTIPROCESS
        )
    except:
        print("[ERROR] - An error was found, most likely with the camera position, make sure the camera is not placed directly above its target")
        sys.exit()
    print("Starting Render")
    cam.render(SCENE, f"{SAVE_PATH}/{FILE_NAME}.png", silent=DRAW_SILENT)