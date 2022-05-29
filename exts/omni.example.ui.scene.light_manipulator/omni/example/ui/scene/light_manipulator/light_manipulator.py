# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__all__ = ["LightManipulator"]

from .light_model import LightShape
from omni.ui import scene as sc
from omni.ui import color as cl


class LightManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __del__(self):
        self.model = None

    def _build_shape(self, model):
        shape_item = model.get_item("shape")
        shape = model.get_as_floats(shape_item)[0]

        x, y, z = None, None, None
        radius_item = model.get_item("radius")
        if radius_item:
            y = model.get_as_floats(radius_item)[0]
            length_item = model.get_item("length")
            if length_item:
                x = model.get_as_floats(length_item)[0]
            else:
                x = y
        else:
            width_item, height_item = model.get_item("width"), model.get_item("height")
            if width_item and height_item:
                x = model.get_as_floats(width_item)[0]
                y = model.get_as_floats(height_item)[0]
                z = min(x, y)

        if shape != LightShape.NONE:
            if not z:
                z = y
            self._shape_xform.transform = [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1]

        return shape

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        model = self.model
        if not model:
            return

        # if we don't have selection then just return
        prim_path_item = model.get_item("prim_path")
        prim_path = prim_path_item.value if prim_path_item else None
        if not prim_path:
            return

        # Style settings, as kwargs
        thickness = 1
        color = cl.yellow
        line_style = {"thickness": thickness, "color": color}
        shape_style = {"thickness": thickness, "color": color, "wireframe": True}

        self.__root_xf = sc.Transform(model.get_as_floats(model.get_item("transform")))
        with self.__root_xf:
            self._x_xform = sc.Transform()
            with self._x_xform:
                self._shape_xform = sc.Transform()
                # Build the shape's transform
                shape = self._build_shape(model)
                with self._shape_xform:
                    # Build the shape geomtery as unit-sized
                    h = 0.5
                    z = -0.25
                    if shape == LightShape.SPHERE:
                        sc.Arc(axis=0, radius=1, **shape_style)
                        sc.Arc(axis=1, radius=1, **shape_style)
                        sc.Arc(axis=2, radius=1, **shape_style)
                        with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                            sc.Arc(axis=2, radius=1, **shape_style)
                    elif shape == LightShape.CYLINDER:
                        sc.Line((-h, 1, 0), (h, 1, 0), **line_style)
                        sc.Line((-h, -1, 0), (h, -1, 0), **line_style)
                        sc.Line((-h, 0, 1), (h, 0, 1), **line_style)
                        sc.Line((-h, 0, -1), (h, 0, -1), **line_style)
                        with sc.Transform([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -h, 0, 0, 1]):
                            sc.Arc(axis=0, radius=1, **shape_style)
                        with sc.Transform([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, h, 0, 0, 1]):
                            sc.Arc(axis=0, radius=1, **shape_style)
                    elif shape == LightShape.DISK:
                        sc.Line((1, 0, 0), (1, 0, z), **line_style)
                        sc.Line((-1, 0, 0), (-1, 0, z), **line_style)
                        sc.Line((0, -1, 0), (0, -1, z), **line_style)
                        sc.Line((0, 1, 0), (0, 1, z), **line_style)
                        sc.Arc(axis=2, radius=1, **shape_style)
                    elif shape == LightShape.RECTANGLE:
                        sc.Rectangle(axis=2, width=1, height=1, **shape_style)
                        sc.Line((h, h, 0), (h, h, z), **line_style)
                        sc.Line((-h, -h, 0), (-h, -h, z), **line_style)
                        sc.Line((h, -h, 0), (h, -h, z), **line_style)
                        sc.Line((-h, h, 0), (-h, h, z), **line_style)

    def on_model_updated(self, item):
        # Regenerate the mesh
        model = self.model
        if not model:
            return

        if item == model.get_item("transform"):
            # If transform changed, update the root transform
            self.__root_xf.transform = model.get_as_floats(item)
        elif item == model.get_item("prim_path"):
            # If prim_path changed, invalidate everything
            self.invalidate()
        elif item:
            # Interpret None as changing multiple light shape settings
            self._build_shape(model)
