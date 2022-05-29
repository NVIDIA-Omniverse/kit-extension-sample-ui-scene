## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["ObjectInfoManipulator"]

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class ObjectInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._radius = 2
        self._distance_to_top = 5
        self._thickness = 2
        self._radius_hovered = 20

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # if we don't have selection then just return
        if self.model.get_item("name") == "":
            return

        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Label
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                # Circle
                sc.Arc(self._radius, axis=2, color=cl.yellow)
                sc.Line([0, 0, 0], [0, self._radius_hovered, 0], color=cl.yellow, thickness=self._thickness)
                sc.Line([0, self._radius_hovered, 0], [self._radius_hovered, self._radius_hovered * 1.5, 0] , color=cl.yellow, thickness=self._thickness)

                # Move it to the top
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(self._radius_hovered + 5, self._radius_hovered * 1.5 - 10, 0)):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        # Move it 5 points more to the top in the screen space
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 30, 0)):
                            sc.Label(f"Path: {self.model.get_item('name')}", alignment=ui.Alignment.LEFT_BOTTOM)
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                            sc.Label(f"Material: {self.model.get_item('material')}", alignment=ui.Alignment.LEFT_BOTTOM)

    def on_model_updated(self, item):
        # Regenerate the mesh
        self.invalidate()
