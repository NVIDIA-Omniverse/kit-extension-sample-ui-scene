# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SliderExtension"]

from .slider_registry import SliderRegistry
from omni.kit.manipulator.viewport import ManipulatorFactory
from omni.kit.viewport.registry import RegisterScene
import omni.ext


class SliderExtension(omni.ext.IExt):
    """The entry point to the extension"""

    def on_startup(self, ext_id):
        # Viewport Next: omni.kit.viewport.window
        self._slider_registry = RegisterScene(SliderRegistry, "omni.example.ui_scene.slider_manipulator")
        # Viewport Legacy: omni.kit.window.viewport
        self._slider_factory = ManipulatorFactory.create_manipulator(SliderRegistry)

    def on_shutdown(self):
        ManipulatorFactory.destroy_manipulator(self._slider_factory)
        self._slider_factory = None

        self._slider_registry.destroy()
        self._slider_registry = None
