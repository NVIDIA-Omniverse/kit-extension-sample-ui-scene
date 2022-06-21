# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ObjectInfoExtension"]

import carb
import omni.ext
from omni.kit.viewport.utility import get_active_viewport_window

from .viewport_scene import ViewportScene


class ObjectInfoExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    def __init__(self):
        self._viewport_scene = None

    def on_startup(self, ext_id: str) -> None:
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        # Get the active Viewport (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()

        # Issue an error if there is no Viewport
        if not viewport_window:
            carb.log_error(f"No Viewport Window to add {ext_id} scene to")
            return

        # Build out the scene
        self._viewport_scene = ViewportScene(viewport_window, ext_id)

    def on_shutdown(self) -> None:
        """Called when the extension is shutting down."""

        if self._viewport_scene:
            self._viewport_scene.destroy()
            self._viewport_scene = None
