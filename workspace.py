import rtrace_wrapper as rtw

# The bits you'll use
from rtrace_wrapper import Material
from rtrace_wrapper import (
    add_cube, add_sphere, use_ground,
    set_camera_center, set_camera_target, set_camera_fov
)

from rtrace_wrapper import render

# Add the ground object, comment out if needed
# use_ground()


add_sphere(
    (0, 0, 0),
    0.5,
    Material.metal(fuzz=0.5)
)

add_cube(
    (0, -1, 0),
    (200, 1, 100),
    material=Material.metal(
        (0.3, 0.5, 0.7),
        0
    )
)

set_camera_center((0, 0.1, 3))
set_camera_fov(40)


# Render call must always be in the protected entry point
if __name__ == '__main__':
    """Note that it takes about 31 seconds to fully render a scene"""
    render()