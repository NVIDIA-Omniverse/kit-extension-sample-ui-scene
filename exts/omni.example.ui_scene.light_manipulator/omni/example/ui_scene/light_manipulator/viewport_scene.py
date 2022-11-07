# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportScene"]

from omni.ui import scene as sc

from .light_manipulator import LightManipulator
from omni.kit.viewport.registry import RegisterScene


class ViewportScene:
    """The light Manipulator, placed into a Viewport"""

    def __init__(self, viewport_window, ext_id: str):
        self._viewport_window = viewport_window
        self._light_manip = RegisterScene(LightManipulator, "Bla")

    def __del__(self):
        self.destroy()

    def destroy(self):

        # Remove our references to these objects
        self._viewport_window = None
        self._light_manip = None
