import sys

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.renderers.images import ColourImageFile

import rtrace
from .scene_view import SceneView

def main_app(screen: Screen, last_scene: Scene, rtrace_scene: rtrace.Scene, cam: rtrace.Camera):
    
    scenes = [
        Scene([SceneView(screen, rtrace_scene, cam, "images/__gui_temp__.png")], -1, "scene_view")
    ]
    
    screen.play(scenes, stop_on_resize=True, start_scene=last_scene)

def run():
    rtrace_scene = rtrace.Scene([
        rtrace.Assets.Sphere(rtrace.Point3(0, 0, -1),0.5, rtrace.Mat.Metal(rtrace.Color.WHITE())),
        rtrace.Assets.Sphere(rtrace.Point3(0, -100.5, -1),100, rtrace.Mat.Lambertian(rtrace.Color.GRAY()))
    ])
    cam = rtrace.Camera(128, 16/9, rtrace.Point3(0, 0, 1.5), rtrace.Point3(0, 0, -1), samples=1, use_multiprocess=False)
    
    last_scene = None
    while True:
        try:
            Screen.wrapper(main_app, arguments=[last_scene, rtrace_scene, cam])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene