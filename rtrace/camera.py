from __future__ import annotations
import typing as t
from math import ceil, pi, tan
from random import random

import multiprocessing as mp
from PIL import Image
from tqdm import tqdm

from .color import Color
from .vec3 import Vector3
from .ray import Ray

if t.TYPE_CHECKING:
    import os
    from .scene import Scene
    from .vec3 import Point3

# The boundary for the height parameter to 
# be interpreted as an aspect ratio
_HEIGHT_ASPECT_BOUNDARY = 4

# After testing, its faster to use smaller numbers
# 16 yielded the best results
_MULTIPROCESS_BLOCK_SIZE = 16

_PI_OVER_SEMICIRCLE = pi / 180.0

def degrees_to_radians(deg: float) -> float:
    return deg * _PI_OVER_SEMICIRCLE

class Camera:
    """Represents a camera within a scene, given location and scale"""
    
    _img_width: int
    _img_height: int
    _aspect_ratio: float
    
    samples: int
    sample_scale: float
    recursion_limit: float
    
    viewport_width: float
    viewport_height: float
    
    viewport_u: Vector3
    viewport_v: Vector3
    
    defocus_angle: float
    defocus_disc_u: Vector3
    defocus_disc_v: Vector3
    
    center: Point3
    
    offset_server: t.Callable
    
    use_multiprocess: bool
    
    fov: float
    
    u: Vector3 
    v: Vector3 
    w: Vector3
    
    def __init__(self, 
            width: int, 
            height: int | float, 
            center: Point3, 
            lookat: Point3,
            upvec: Vector3 = Vector3(0, 1, 0),
            samples: int = 10,
            recursion_limit: int = 16,
            fov: float = 90,
            focus_angle: float = 0,
            focus_dist: float = 10,
            offset_server: t.Literal["s", "d"] = "s",
            use_multiprocess: bool = True
        ) -> None:
        """Creates a camera for a virtual scene

        Args:
            width (int): 
                The width of the output image
                
            height (int | float): 
                Interpreted as the height of the image if an integer larger than 
                4 otherwise as the aspect ratio of the image
                
            center (Point3): 
                The center of the camera in 3D space
                
            samples (int, optional): 
                The number of times to sample a single pixel, must be greater than 0. 
                Defaults to 10. (PROCESSING INTENSIVE)
                
            viewport_height (float, optional): 
                The height of the viewport, all rays cast intersect with the viewport. 
                Defaults to 2.0.
            
            focal_length (float, optional): 
                The distance from the center of the camera to the viewport. Defaults to 1.0.
            
            offset_server (Literal['s', 'd'], optional): 
                Changes what function is used to generate offsets for each ray sample. 
                Disregarded if the :samples: param is set to 1. Defaults to "s".
        """
        self._img_width = width
        
        if isinstance(height, int) and height > _HEIGHT_ASPECT_BOUNDARY:
            # assume height is to be interpreted as a height
            self._img_height = height
            self._aspect_ratio = self.img_width / self.img_height
        else:
            # assume height param is the aspect ratio of the image
            self._aspect_ratio = height
            self._img_height = max(int(self.img_width / self.aspect_ratio), 1)
        
        # self.focal_length = (center - lookat).length
        self.center = center
        
        self.samples = max(samples, 1)
        self.sample_scale = 1 / samples
        self.recursion_limit = recursion_limit
        
        self.fov = fov
        # This calculation generates the viewport height constant
        theta = degrees_to_radians(fov)
        h = tan(theta / 2)
            
        self.viewport_height = 2 * h * focus_dist
        self.viewport_width = self.viewport_height * (self.img_width / self.img_height)
        
        self.w = (center - lookat).unit_vector
        self.u = Vector3.cross(upvec, self.w).unit_vector
        self.v = Vector3.cross(self.w, self.u)
        
        self.viewport_u = self.viewport_width * self.u
        self.viewport_v = self.viewport_height * -self.v
        
        self.pixel_delta_u = self.viewport_u / self.img_width
        self.pixel_delta_v = self.viewport_v / self.img_height
        
        self.viewport_upper_left = self.center - (focus_dist * self.w) - self.viewport_u/2 - self.viewport_v/2
        self.pixel00_loc = self.viewport_upper_left + 0.5 * (self.pixel_delta_u + self.pixel_delta_v)
        
        self.defocus_angle = focus_angle
        defocus_radians = focus_dist * tan(degrees_to_radians((self.defocus_angle / 2)))
        self.defocus_disc_u = self.u * defocus_radians 
        self.defocus_disc_v = self.v * defocus_radians
        
        self.offset_server = {
            "s" : self.sample_square,
            "d" : self.derterministic_square
        }[offset_server] if self.samples > 1 else self.monosampled_square
        
        self.center_server = self.get_center if self.defocus_angle <= 0 else self.defocus_disc_sample
        
        self.use_multiprocess = use_multiprocess
        
    
    @classmethod
    def pre_render(cls, aspect_ratio: float, center: Point3) -> Camera:
        return Camera(
            100, aspect_ratio,
            center
        )
    
    @classmethod
    def standard(cls, width: int, aspect_ratio: float, center: Point3) -> Camera:
        return Camera(
            width, aspect_ratio, center
        )
    
    @property
    def img_width(self) -> int:
        """The width of the rendered image"""
        return self._img_width
    
    @img_width.setter
    def img_width(self, value: int) -> None:
        # This abstraction exists to allow for the 
        # modification of the image size after camera 
        # init while preserving all other settings. 
        # Mainly for use with external applications like a GUI
        self._img_width = value
    
    @property
    def img_height(self) -> int:
        """The height of the rendered image"""
        return self._img_height
    
    @img_height.setter
    def img_height(self, value: int | float) -> None:
        self._img_height = value
    
    @property
    def aspect_ratio(self) -> float:
        """The aspect ratio, or the relation of width to height, of the rendered image."""
        return self._aspect_ratio
    
    @aspect_ratio.setter
    def aspect_ratio(self, value: float) -> None:
        self._aspect_ratio = value
    
    def render(self, scene: Scene, fp: os.PathLike, filter: t.Callable[[Image.Image],Image.Image] | None = None, silent: bool = False) -> None:
        """Renders an image by propogating rays though a selec scene and saves to a file
        
        >>> Camera.render(scene, "im.png", silent = False)
        
        Args:
            scene (Scene): The scene to render
            fp (os.PathLike): The path to save to, including file name.
            filter (t.Callable[[Image.Image],Image.Image] | None, optional): A function to call that applies a filter to the final image be fore saving. Defaults to None.
            silent (bool, optional): Whether to print updates to the console. Defaults to False.
        """
        if self.use_multiprocess:
            self.render_multi(scene=scene, fp=fp, filter=filter, silent = silent)
        else:
            self.render_mono(scene=scene, fp=fp, filter=filter, silent = silent)
    
    def render_multi(self, scene: Scene, fp: os.PathLike, filter: t.Callable[[Image.Image],Image.Image] | None = None, silent: bool = False, show: bool = False) -> None:
        """Renders a scene by segmenting into blocks and executing each as a subprocess
        To respect camera settings, call the standard render method
        >>> Camera.render(scene, "im.png", silent = False)
        
        Args:
            scene (Scene): The scene to render
            fp (os.PathLike): The path to save to
        """
        # Multiprocessing results in a 688.57% speed increase from standard.
        im = Image.new("RGB", (self.img_width, self.img_height), (0, 0, 0))
        
        # Generate a list of block bounds
        def block_args():
            for blc_y in range(ceil(self.img_height / _MULTIPROCESS_BLOCK_SIZE)):
                for blc_x in range(ceil(self.img_width / _MULTIPROCESS_BLOCK_SIZE)):
                    yield (
                        scene, 
                        (blc_x * _MULTIPROCESS_BLOCK_SIZE, min((blc_x + 1) * _MULTIPROCESS_BLOCK_SIZE, self.img_width)), 
                        (blc_y * _MULTIPROCESS_BLOCK_SIZE, min((blc_y + 1) * _MULTIPROCESS_BLOCK_SIZE, self.img_height)),
                        silent
                    )

        # Dispaatch each block to a process and paste the resulting image to the main canvas
        with mp.Pool() as pool:
            
            progress = tqdm(
                total = ceil(self.img_height / _MULTIPROCESS_BLOCK_SIZE) * ceil(self.img_width / _MULTIPROCESS_BLOCK_SIZE), 
                desc="waiting for worker threads"
            ) if not silent else None
            
            for pos, img_block in pool.starmap(self._render_block, block_args()):
                im.paste(img_block, pos)
                
                if not silent:
                    progress.update()
            
            if not silent:
                progress.close()
        
        # Image filter step, user defined
        if filter is not None:
            im = filter(im)
        # Save the image
        im.save(fp)
    
    
    # Convert to a single function definition to save 
    def _render_block(self, scene: Scene, range_x: tuple[int, int], range_y: tuple[int, int], silent: bool = False) -> None:
        """Renders a set block of the image, used for worker threads when multiprocessing

        Args:
            im (Image.Image): The PIL.Image to write data to
            scene (Scene): The scene to propogate rays through
            range_x (tuple[int, int]): The x parameters of the block where range_x[0] < range_x[1]
            range_y (tuple[int, int]): The y corners of the block, where range_y[0] < range_y[1]
        """
    
        block_width, block_height = range_x[1] - range_x[0], range_y[1] - range_y[0]
        
        im = Image.new("RGB", (block_width, block_height), (0, 0, 0))
        
        gr = self.get_ray
        rlim = self.recursion_limit
        sample_scale = self.sample_scale
        
        for i in range(block_width * block_height):
            x, y = i % block_width, i // block_width
            # For loop completion, move to seperate function
            pixel_color = Color(0, 0, 0)
            
            for iter in range(self.samples):
                # Optional index for deterministic offset servers
                r = gr(x + range_x[0], y + range_y[0], iter)
                pixel_color += scene.ray_color(r, rlim)
            
            im.putpixel((x, y), (pixel_color * sample_scale).as_tuple(256))
        
        if not silent:
            print(f"Block ({range_x[0]}, {range_y[0]}) finished")
         
        return (range_x[0], range_y[0]), im
    
    def render_mono(self, scene: Scene, fp: os.PathLike, filter: t.Callable[[Image.Image],Image.Image] | None = None, silent: bool = False) -> None:
        """Exact same as Camera.render() except renders the entire image
        on a single process rather than the entire CPU

        Args:
            im (Image.Image): The image to write data to
            scene (Scene): The scene to propogate rays through
        """
        im = Image.new("RGB", (self.img_width, self.img_height), (0, 0, 0))
        
        # Get functions to avoid using .__getattr__ in loop
        # Attrs are hashed, meaning the loop would have to
        # hash this each time
        gr = self.get_ray
        rlim = self.recursion_limit
        sample_scale = self.sample_scale
        width, height = self.img_width, self.img_width
        # Not consistently faster to assign local for non-self methods
        
        # Reducing the number of assignments makes the program consistently 
        # run 5 iterations / sec faster per improvement
        
        for i in (tqdm(range(self.img_width * self.img_height)) if not silent else range(self.img_width * self.img_height)):
            x, y = i % width, i // height
            # For loop completion
            pixel_color = Color(0, 0, 0)
            
            for iter in range(self.samples):
                # Optional index for deterministic offset servers
                r = gr(x, y, iter)
                pixel_color += scene.ray_color(r, rlim)
            
            im.putpixel((x, y), (pixel_color * sample_scale).as_tuple(256))
        
        if filter is not None:
            im = filter(im)
        
        im.save(fp)
    
    def get_ray(self, i: int, j: int, iter: int) -> Ray:
        """Returns a Ray object with some offset directed through 
        the viewport of the camera with an origin at some pixel
        at (i, j)

        Args:
            i (int): Pixel X location
            j (int): Pixel Y location
            iter (int): The current iteration for that pixel, used for some offset generators.

        Returns:
            Ray: A ray cast from the camera position through a pixel in the viewport
        """
        offset = self.offset_server(iter)
        pixel_sample = self.pixel00_loc + ((i + offset.x) * self.pixel_delta_u) + ((j + offset.y) * self.pixel_delta_v)
        return Ray(self.center_server(), pixel_sample - self.center)
    
    def defocus_disc_sample(self):
        p = Vector3.random_on_unit_disc()
        return self.center + (p.x * self.defocus_disc_u) + (p.y * self.defocus_disc_v)
    
    def get_center(self):
        return self.center
    
    def sample_square(self, iter: int) -> Vector3:
        """Creates a random offset between -0.5 and 0.5 in both the
        x and y directions

        Args:
            iter (int): The current iteration, not used for generation

        Returns:
            Vector3: A vector containing the offset positions in the x and y properties and 0 in the z property
        """
        return Vector3(random() - 0.5, random() - 0.5, 0)
    
    def derterministic_square(self, iter: int) -> Vector3:
        """A deterministic version of the Camera.sample_square() function
        that intended to generate offsets faster, marginally slower than
        it's precursor. Generates an offset based on the current iteration.

        Args:
            iter (int): The current iteration of some pixel

        Returns:
            Vector3: A vector containing the offset positions in the x and y properties and 0 in the z property
        """
        # Barely faster than generating random numbers
        return Vector3((iter / self.samples) % 1 - 0.5, (3 * iter / self.samples) - 0.5, 0)
    
    def monosampled_square(self, iter: int) -> Vector3:
        return Vector3(0, 0, 0)
    