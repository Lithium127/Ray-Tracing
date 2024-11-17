from __future__ import annotations
import typing as t

from asciimatics.widgets import Frame, Widget, Button, Layout, Label, TextBox, ListBox, VerticalDivider, Divider
from asciimatics.renderers.images import ImageFile

import rtrace

if t.TYPE_CHECKING:
    from asciimatics.screen import Screen
    from ..rtrace import Scene, Camera


class SceneView(Frame):
    
    def __init__(self, screen: Screen, scene: Scene, camera: Camera, render_fp: str):
        super(SceneView, self).__init__(
            screen,
            screen.height,
            screen.width,
            on_load=self.on_load,
            title="Scene Viewer"
        )
        
        self._render_scene = scene
        self._camera = camera
        self._render_image_path = render_fp
        
        # Idea is, we place a textbox and update its content each time we want to render
        self._scene_view = TextBox(
            height = Widget.FILL_FRAME,
            readonly=True
        )
        
        self._asset_list = ListBox(
            Widget.FILL_COLUMN,
            self.get_scene_assets()
        )
        
        top_toolbar = Layout([1, 1, 1, 1, 1])
        self.add_layout(top_toolbar)
        top_toolbar.add_widget(Button("Render Scene", on_click=self.render_image))
        
        render_layout = Layout([75,2,25], fill_frame=True)
        self.add_layout(render_layout)
        render_layout.add_widget(self._scene_view, 0)
        render_layout.add_widget(VerticalDivider(), 1)
        render_layout.add_widget(Label("Scene Assets", align="^"), 2)
        render_layout.add_widget(Divider(), 2)
        render_layout.add_widget(self._asset_list, 2)

        # Conditionally add a divider if the screen is too large
        if screen.height > 25:
            div1 = Layout([1])
            self.add_layout(div1)
            div1.add_widget(Divider())
        
        bottom_toolbar = Layout([1, 1, 1, 1, 1])
        self.add_layout(bottom_toolbar)
        
        self.fix()

    def on_load(self):
        self.update_render_view()
    
    def update_render_view(self):
        image = ImageFile(self._render_image_path, 50)
        self._scene_view.value = image.rendered_text[0]
    
    def get_scene_assets(self) -> tuple[str, int]:
        str_list = []
        for index, asset in enumerate(self._render_scene.assets):
            str_list.append((asset.__class__.__name__, index))
        return str_list
    
    def render_image(self):
        self._camera.render(
            self._render_scene,
            self._render_image_path,
            silent=True
        )
        self.update_render_view()
    