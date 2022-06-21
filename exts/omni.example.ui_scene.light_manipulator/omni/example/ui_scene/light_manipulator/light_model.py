# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LightModel"]

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


class LightModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the attributes of the selected light.
    """

    class MatrixItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the tranformation. It doesn't contain anything
        because we take the tranformation directly from USD when requesting.
        """

        identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

        def __init__(self):
            super().__init__()
            self.value = self.identity.copy()

    class FloatItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value about some attibute"""

        def __init__(self, value=0.0):
            super().__init__()
            self.value = value

    class StringItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single string value about some attibute"""

        def __init__(self, value=""):
            super().__init__()
            self.value = value

    def __init__(self):
        super().__init__()

        self.prim_path = LightModel.StringItem()
        self.transform = LightModel.MatrixItem()
        self.intensity = LightModel.FloatItem()
        self.width = LightModel.FloatItem()
        self.height = LightModel.FloatItem()

        # Save the UsdContext name (we currently only work with single Context)
        self._usd_context_name = ""

        # Current selection
        self._light = None
        self._stage_listener = None

        # Track selection change
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
        """Called by Tf.Notice. When USD data changes, we update the ui"""
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
            elif self.width and p.name == "width":
                changed_items.add(self.width)
            elif self.height and p.name == "height":
                changed_items.add(self.height)
            elif self.intensity and p.name == "intensity":
                changed_items.add(self.intensity)

        for item in changed_items:
            self._item_changed(item)

    def get_as_floats(self, item):
        """get the item value directly from USD"""
        if item == self.transform:
            return self._get_transform(self._time)
        if item == self.intensity:
            return self._get_intensity(self._time)
        if item == self.width:
            return self._get_width(self._time)
        if item == self.height:
            return self._get_height(self._time)

        if item:
            # Get the value directly from the item
            return item.value
        return None

    def set_floats_commands(self, item, value):
        """set the item value to USD using commands, this is useful because it supports undo/redo"""
        if not self._current_path:
            return

        if not value or not item:
            return

        # we get the previous value from the model instead of USD
        if item == self.height:
            prev_value = self.height.value
            if prev_value == value:
                return
            height_attr = self._light.GetHeightAttr()
            omni.kit.commands.execute('ChangeProperty', prop_path=height_attr.GetPath(), value=value, prev=prev_value)
        elif item == self.width:
            prev_value = self.width.value
            if prev_value == value:
                return
            width_attr = self._light.GetWidthAttr()
            omni.kit.commands.execute('ChangeProperty', prop_path=width_attr.GetPath(), value=value, prev=prev_value)
        elif item == self.intensity:
            prev_value = self.intensity.value
            if prev_value == value:
                return
            intensity_attr = self._light.GetIntensityAttr()
            omni.kit.commands.execute('ChangeProperty', prop_path=intensity_attr.GetPath(), value=value, prev=prev_value)

        # This makes the manipulator updated
        self._item_changed(item)

    def set_item_value(self, item, value):
        """ This is used to set the model value instead of the usd. This is used to record previous value for
            omni.kit.commands """
        item.value = value

    def set_floats(self, item, value):
        """set the item value directly to USD. This is useful when we want to update the usd but not record it in commands"""
        if not self._current_path:
            return

        if not value or not item:
            return

        pre_value = self.get_as_floats(item)
        # no need to update if the updated value is the same
        if pre_value == value:
            return

        if item == self.height:
            self._set_height(self._time, value)
        elif item == self.width:
            self._set_width(self._time, value)
        elif item == self.intensity:
            self._set_intensity(self._time, value)

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
        settings.set("/persistent/app/viewport/gizmo/lineWidth", 0)

        # Clear any cached UsdLux.Light object
        self._light = None

        # Set the prim_path to empty
        self.prim_path.value = ""
        self._item_changed(self.prim_path)

    def _on_kit_selection_changed(self):
        # selection change, reset it for now
        self._light = None

        # Turn off any native selected light drawing
        settings = carb.settings.get_settings()
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
        if prim and prim.IsA(UsdLux.RectLight):
            self._light = UsdLux.RectLight(prim)

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
        return _flatten_matrix(world_xform)

    def _get_intensity(self, time: Usd.TimeCode):
        """Returns intensity of currently selected light"""
        if not self._light:
            return 0.0

        # Get intensity directly from USD
        return self._light.GetIntensityAttr().Get(time)

    def _set_intensity(self, time: Usd.TimeCode, value):
        """set intensity of currently selected light"""
        if not self._light:
            return

        # set height dirctly to USD
        self._light.GetIntensityAttr().Set(value, time=time)

    def _get_width(self, time: Usd.TimeCode):
        """Returns width of currently selected light"""
        if not self._light:
            return 0.0

        # Get radius directly from USD
        return self._light.GetWidthAttr().Get(time)

    def _set_width(self, time: Usd.TimeCode, value):
        """set width of currently selected light"""
        if not self._light:
            return

        # set height dirctly to USD
        self._light.GetWidthAttr().Set(value, time=time)

    def _get_height(self, time: Usd.TimeCode):
        """Returns height of currently selected light"""
        if not self._light:
            return 0.0

        # Get height directly from USD
        return self._light.GetHeightAttr().Get(time)

    def _set_height(self, time: Usd.TimeCode, value):
        """set height of currently selected light"""
        if not self._light:
            return

        # set height dirctly to USD
        self._light.GetHeightAttr().Set(value, time=time)
