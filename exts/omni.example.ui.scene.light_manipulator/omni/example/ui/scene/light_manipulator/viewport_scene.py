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

from .light_model import LightModel
from .light_manipulator import LightManipulator


class ViewportScene:
    """The Object Info Manupulator, placed into a Viewport"""

    def __init__(self, viewport_window, ext_id: str):
        self._scene_view = None
        self._viewport_window = viewport_window

        # Create a unique frame for our SceneView
        with self._viewport_window.get_frame(ext_id):
            # Create a default SceneView (it has a default camera-model)
            self._scene_view = sc.SceneView()
            # Add the manipulator into the SceneView's scene
            with self._scene_view.scene:
                LightManipulator(model=LightModel())

            # Register the SceneView with the Viewport to get projection and view updates
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None
