from __future__ import annotations
import typing as t
from types import FunctionType

from asciimatics.widgets import Widget, Frame, Layout, Button

if t.TYPE_CHECKING:
    from asciimatics.screen import Screen
    from asciimatics.scene import Scene

class PopUpInput(Frame):
    
    def __init__(self, screen: Screen, widget: Widget | list[Widget], callback: t.Callable, cast_as: t.Any = str, theme: str = "default"):
        """Creates a popup dialoug to obtain user input, ex: changing tha value of an element in a listbox

        Args:
            screen (Screen): The screen to render from, use self.screen
            widget (Widget): The widget to display in the input
            callback (t.Callable): A callable function that accepts a list of widgets values cast as type [cast_as]
            theme (str, optional): The theme of the modal. Defaults to "default".
        """
    
        self._widgets = widget
        if not isinstance(self._widgets, list):
            self._widgets = [self._widgets]
        self._callback = callback
        self._cast_as = cast_as
        
        super().__init__(
            screen,
            min(len(self._widgets) + 4, screen.height // 2),
            screen.width // 2,
            is_modal = True
        )
    
        input_layout = Layout([1], fill_frame=True)
        self.add_layout(input_layout)
        for i in range(len(self._widgets)):
            input_layout.add_widget(self._widgets[i], 0)
        
        button_layout = Layout([1, 1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(Button("Cancel", self._destroy), 0)
        button_layout.add_widget(Button("Save", self._save), 2)
        
        self.fix()
        
        self.set_theme(theme)
    
    def _save(self):
        if self._callback:
            self._callback([self._cast_as(wgt.value) for wgt in self._widgets])
        self._destroy()
    
    def _destroy(self):
        self._scene.remove_effect(self)
    
    def clone(self, screen, scene):
        
        if self._callback is None or isinstance(self._callback, FunctionType):
            scene.add_effect(PopUpInput(screen, self._widgets, self._callback))
        


class NewAssetModal(Frame):
    
    
    def __init__(self):
        
        pass