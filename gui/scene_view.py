from __future__ import annotations
import typing as t

from asciimatics.widgets import Frame, Widget, Button, Layout, Label, TextBox, ListBox, VerticalDivider, Divider, PopUpDialog, Text
from asciimatics.renderers.images import ColourImageFile
from asciimatics.parsers import AsciimaticsParser

import rtrace

from .modals import PopUpInput

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
        
        self.set_theme("bright")
        
        self._render_scene = scene
        self._camera = camera
        self._render_image_path = render_fp
        
        # Idea is, we place a textbox and update its content each time we want to render
        self._scene_view = TextBox(
            height = Widget.FILL_FRAME,
            parser=AsciimaticsParser(),
            readonly = True,
            disabled = False
        )
        
        self._asset_list = ListBox(
            Widget.FILL_COLUMN,
            self.get_scene_assets(),
            on_select=self.on_asset_select
        )
        
        self._object_attrs = ListBox(
            screen.height // 2 - 4,
            [],
            on_select=self.change_object_attr
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
        render_layout.add_widget(Button("New Asset", on_click=self.add_asset),2)
        render_layout.add_widget(Divider(), 2)
        render_layout.add_widget(self._object_attrs, 2)

        # Conditionally add a divider if the screen is too large
        if screen.height > 25:
            div1 = Layout([1])
            self.add_layout(div1)
            div1.add_widget(Divider())
        
        bottom_toolbar = Layout([1, 1, 1, 1, 1])
        self.add_layout(bottom_toolbar)
        
        self.fix()
        
        # --< Some widget specific cleanup >-- #
        # self._camera.img_width = self._scene_view._w
        # self._camera.img_height = self._scene_view._h

    def on_load(self):
        self.update_render_view()
    
    
    def update_render_view(self):
        image = ColourImageFile(self.screen, self._render_image_path, self._scene_view._h, uni=True, dither=True)
        text_image = image._images[0].split('\n')
        self._scene_view.value = text_image
    
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
    
    def on_asset_select(self):
        attr_list = []
        for key, value in self._render_scene.assets[self._asset_list.value].__dict__.items():
            if isinstance(value, rtrace.Point3) or isinstance(value, rtrace.Vector3):
                value = f"({value.x}, {value.y}, {value.z})"
            attr_list.append(
                (
                    f"{key} : {value}", 
                    key
                )
            )
        self._object_attrs.options = attr_list
    
    def change_object_attr(self):
        attr = self._render_scene.assets[self._asset_list.value].__dict__.get(self._object_attrs.value, None)
        
        w_list = [Text(str(self._object_attrs.value))]
        func = self.update_object_attr
        cast_as = attr.__class__
        
        if isinstance(attr, rtrace.Point3) or isinstance(attr, rtrace.Vector3):
            w_list = [
                Text("X", value = str(attr.x)),
                Text("Y"),
                Text("Z")
            ]
            func = self.update_object_point3
            cast_as=str
        
        self._scene.add_effect(PopUpInput(
            self.screen, 
            w_list,
            self.wrap_update_object_attr(func),
            cast_as=cast_as
        ))
    
    def wrap_update_object_attr(self, callback: t.Callable) -> None:
        def wrapper(values):
            callback(values)
            self.on_asset_select()
        return wrapper
    
    def update_object_attr(self, value):
        self._render_scene.assets[self._asset_list.value].__dict__.__setitem__(
            self._object_attrs.value, 
            value[0]
        )
    
    def update_object_point3(self, values):
        self._render_scene.assets[self._asset_list.value].__dict__.__setitem__(
            self._object_attrs.value, 
            rtrace.Point3(float(values[0]), float(values[1]), float(values[2]))
        )
    
    def show_warning_modal(self, text: str) -> None:
        self._scene.add_effect(
            PopUpDialog(self.screen, text, buttons=["OK"])
        )
    
    def add_asset(self):
        # Supposed to open a modal to add assets
        self.show_warning_modal("Adding assets has not yet been implemented")