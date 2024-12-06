"""
This module implements variables that change
"""
from __future__ import annotations
import typing as t



class TimeVar(object):
    
    max_frames: int
    current_frame: int
    
    equation: t.Callable[[int], int | float]
    
    def __init__(self, equation: t.Callable[[int], int | float]) -> None:
        """Creates a variable that changes with relation to the current frame

        Args:
            equation (t.Callable[[int], int  |  float]): The equation to modify the frame number by
        """
        pass
    
    
    @classmethod
    def _set_frame(cls, frame: int) -> None:
        """Sets the global frame number of all TimeVars

        Args:
            frame (int): The frame number
        """
        TimeVar.current_frame = frame
    
    
    @classmethod
    def _set_frame_max(cls, frame: int) -> None:
        """Sets the global maximum frames of all TimeVars

        Args:
            frame (int): The max frame number
        """
        TimeVar.max_frames = frame
    
    
    def value(self) -> int | float:
        """Gets the current value of this TimeVar using
        the frame number and equation

        Returns:
            int | float: The current value of this var at this frame
        """
        return self.equation(TimeVar.current_frame)


class Interpolate(TimeVar):
    
    def __init__(self, t0: int | float, t1: int | float) -> None:
        
        slope = (max(t0, t1) - min(t0, t1)) / TimeVar.max_frames
        
        super().__init__(
            equation = lambda frame: t0 + (frame * slope)
        )