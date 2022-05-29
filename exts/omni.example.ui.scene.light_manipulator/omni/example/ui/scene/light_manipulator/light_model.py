# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LightModel", "LightShape"]

import carb
from omni.ui import scene as sc
import omni.usd

from pxr import Usd, UsdGeom, UsdLux, Tf, Gf


def _flatten_matrix(matrix: Gf.Matrix4d):
    m0, m1, m2, m3 = matrix[0], matrix[1], matrix[2], matrix[3]
    return [
        m0[0],
        m0[1],
        m0[2],
        m0[3],
        m1[0],
        m1[1],
        m1[2],
        m1[3],
        m2[0],
        m2[1],
        m2[2],
        m2[3],
        m3[0],
        m3[1],
        m3[2],
        m3[3],
    ]


class LightShape:
    NONE = 0
    SPHERE = 1
    DISK = 2
    CYLINDER = 3
    RECTANGLE = 4


class LightModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the position and info of the selected object.
    """

    class MatrixItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because because we take the position directly from USD when requesting.
        """

        identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

        def __init__(self):
            super().__init__()
            self.value = self.identity.copy()

    class VectorItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because because we take the position directly from USD when requesting.
        """

        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

    class FloatItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value about some attibute"""

        def __init__(self, value=0.0):
            super().__init__()
            self.value = [value]

    class IntItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value about some attibute"""

        def __init__(self, value=0):
            super().__init__()
            self.value = [value]

    class StringItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single string value about some attibute"""

        def __init__(self, value=""):
            super().__init__()
            self.value = [value]

    def __init__(self):
        super().__init__()
        self.__vp_line_width = None

        self.prim_path = LightModel.StringItem()
        self.transform = LightModel.MatrixItem()
        self.shape = LightModel.IntItem()
        self.itensity = LightModel.FloatItem()
        self.intensity = LightModel.FloatItem()
        self.radius = None
        self.length = None
        self.width = None
        self.height = None

        # Save the UsdContext name (we currently only work with single Context)
        self._usd_context_name = ""

        # Current selection
        self._light = None
        self._stage_listener = None

        # Track selection
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Light Manipulator Selection Change"
        )

    def __del__(self):
        self._invalidate_object()

    @property
    def _usd_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context(self._usd_context_name)

    @property
    def _current_path(self):
        return self.prim_path.value

    @property
    def _time(self):
        return Usd.TimeCode.Default()

    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        light_path = self.prim_path.value
        if not light_path:
            return

        changed_items = set()
        for p in notice.GetChangedInfoOnlyPaths():
            prim_path = p.GetPrimPath().pathString
            if prim_path != light_path:
                # Update on any parent transformation changes too
                if light_path.startswith(prim_path):
                    if UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(p.name):
                        changed_items.add(self.transform)
                continue

            if UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(p.name):
                changed_items.add(self.transform)
            elif self.radius and p.name == "radius":
                changed_items.add(None)
            elif self.length and p.name == "length":
                changed_items.add(None)
            elif self.width and p.name == "width":
                changed_items.add(None)
            elif self.height and p.name == "height":
                changed_items.add(None)

        for item in changed_items:
            self._item_changed(item)

    def get_item(self, identifier):
        if identifier == "prim_path":
            return self.prim_path
        if identifier == "transform":
            return self.transform
        if identifier == "radius":
            return self.radius
        if identifier == "length":
            return self.length
        if identifier == "width":
            return self.width
        if identifier == "height":
            return self.height
        if identifier == "shape":
            return self.shape

    def get_as_floats(self, item):
        if item == self.transform:
            return self._get_transform(self._time)
        if item == self.itensity:
            return self._get_intensity(self._time)
        if self.radius and item == self.radius:
            return self._get_radius(self._time)
        if self.length and item == self.length:
            return self._get_length(self._time)
        if self.width and item == self.width:
            return self._get_width(self._time)
        if self.height and item == self.height:
            return self._get_height(self._time)

        if item:
            # Get the value directly from the item
            return item.value
        return []

    def get_as_ints(self, item):
        if item == self.shape:
            return item.value
        return []

    def set_floats(self, item, value):
        if not self._current_path:
            return

        if not value or not item or item.value == value:
            return

        # Set directly to the item
        item.value = value
        # This makes the manipulator updated
        self._item_changed(item)

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def _invalidate_object(self, settings):
        # Revoke the Tf.Notice listener, we don't need to update anything
        if self._stage_listener:
            self._stage_listener.Revoke()
            self._stage_listener = None

        # Reset original Viewport gizmo line width
        if self.__vp_line_width:
            settings.set("/persistent/app/viewport/gizmo/lineWidth", self.__vp_line_width)
            self.__vp_line_width = None

        # Clear any cached UsdLux.Light object
        self._light = None

        # Set the prim_path to empty
        self.prim_path.value = ""
        self._item_changed(self.prim_path)

    def _on_kit_selection_changed(self):
        # selection change, reset it for now
        self._light = None
        self.width, self.height = None, None
        self.radius, self.length = None, None

        # Turn off any native selected light drawing
        settings = carb.settings.get_settings()
        if bool(self.__vp_line_width):
            self.__vp_line_width = settings.get("/persistent/app/viewport/gizmo/lineWidth")
            settings.set("/persistent/app/viewport/gizmo/lineWidth", 0)

        usd_context = self._usd_context
        if not usd_context:
            return self._invalidate_object(settings)

        stage = usd_context.get_stage()
        if not stage:
            return self._invalidate_object(settings)

        prim_paths = usd_context.get_selection().get_selected_prim_paths() if usd_context else None
        if not prim_paths:
            return self._invalidate_object(settings)

        prim = stage.GetPrimAtPath(prim_paths[0])
        if prim:
            if prim.IsA(UsdLux.SphereLight):
                self.shape.value = [LightShape.SPHERE]
                self.radius = LightModel.FloatItem()
                self._light = UsdLux.SphereLight(prim)
            elif prim.IsA(UsdLux.RectLight):
                self.shape.value = [LightShape.RECTANGLE]
                self.width = LightModel.FloatItem()
                self.height = LightModel.FloatItem()
                self._light = UsdLux.RectLight(prim)
            elif prim.IsA(UsdLux.DiskLight):
                self.shape.value = [LightShape.DISK]
                self.radius = LightModel.FloatItem()
                self._light = UsdLux.DiskLight(prim)
            elif prim.IsA(UsdLux.CylinderLight):
                self.shape.value = [LightShape.CYLINDER]
                self.radius = LightModel.FloatItem()
                self.length = LightModel.FloatItem()
                self._light = UsdLux.CylinderLight(prim)

        if not self._light:
            return self._invalidate_object(settings)

        selected_path = self._light.GetPrim().GetPath().pathString
        if selected_path != self.prim_path.value:
            self.prim_path.value = selected_path
            self._item_changed(self.prim_path)

        # Add a Tf.Notice listener to update the light attributes
        if not self._stage_listener:
            self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

    def _get_transform(self, time: Usd.TimeCode):
        """Returns world transform of currently selected object"""
        if not self._light:
            return LightModel.MatrixItem.identity.copy()

        # Compute matrix from world-transform in USD
        world_xform = self._light.ComputeLocalToWorldTransform(time)

        # Flatten Gf.Matrix4d to list
        # XXX: May want to strip out any shear here.
        return _flatten_matrix(world_xform)

    def _get_intensity(self, time: Usd.TimeCode):
        """Returns intensity of currently selected light"""
        if not self._light:
            return [0.0]

        # Get intensity directly from USD
        return self._light.GetIntensityAttr().Get(time)

    def _get_radius(self, time: Usd.TimeCode):
        """Returns radius of currently selected light"""
        # Not all light types have radius
        if not self._light or not hasattr(self._light, "GetRadiusAttr"):
            return [0.0]

        # Get radius directly from USD
        return [self._light.GetRadiusAttr().Get(time)]

    def _get_length(self, time: Usd.TimeCode):
        """Returns length of currently selected light"""
        # Not all light types have length
        if not self._light or not hasattr(self._light, "GetLengthAttr"):
            return [0.0]

        # Get length directly from USD
        return [self._light.GetLengthAttr().Get(time)]

    def _get_width(self, time: Usd.TimeCode):
        """Returns width of currently selected light"""
        # Not all light types have width
        if not self._light or not hasattr(self._light, "GetWidthAttr"):
            return [0.0]

        # Get radius directly from USD
        return [self._light.GetWidthAttr().Get(time)]

    def _get_height(self, time: Usd.TimeCode):
        """Returns height of currently selected light"""
        # Not all light types have height
        if not self._light or not hasattr(self._light, "GetHeightAttr"):
            return [0.0]

        # Get height directly from USD
        return [self._light.GetHeightAttr().Get(time)]
