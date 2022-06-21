# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["WidgetInfoExtension"]

from .widget_info_scene import WidgetInfoScene
from omni.kit.viewport.utility import get_active_viewport_window
import carb
import omni.ext


class WidgetInfoExtension(omni.ext.IExt):
    """The entry point to the extension"""

    def on_startup(self, ext_id):
        # Get the active (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()

        # Issue an error if there is no Viewport
        if not viewport_window:
            carb.log_warn(f"No Viewport Window to add {ext_id} scene to")
            self._widget_info_viewport = None
            return

        # Build out the scene
        self._widget_info_viewport = WidgetInfoScene(viewport_window, ext_id)

    def on_shutdown(self):
        if self._widget_info_viewport:
            self._widget_info_viewport.destroy()
            self._widget_info_viewport = None
