# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SliderModel"]

from omni.ui import scene as sc
from pxr import Gf
from pxr import UsdGeom
from pxr import Usd
import omni.usd
import omni.kit.commands


class SliderModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the position and scale of the selected
    object.
    """

    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because because we take the position directly from USD when requesting.
        """

        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

    class ValueItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value"""

        def __init__(self, value=0):
            super().__init__()
            self.value = [value]

    def __init__(self):
        super().__init__()

        self.scale = SliderModel.ValueItem()
        self.min = SliderModel.ValueItem()
        self.max = SliderModel.ValueItem(1)
        self.position = SliderModel.PositionItem()

        # The distance from the bounding box to the position the model returns
        self._offset = 10
        # Current selection
        self._current_path = ""

        usd_context = omni.usd.get_context()
        self._stage: Usd.Stage = None

        # Track selection
        self._selection = usd_context.get_selection()
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Slider Selection Update"
        )

    def get_item(self, identifier):
        if identifier == "value":
            return self.scale
        if identifier == "position":
            return self.position
        if identifier == "min":
            return self.min
        if identifier == "max":
            return self.max

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self._get_position()
        if item:
            # Get the value directly from the item
            return item.value
        return []

    def set_floats(self, item, value):
        if not self._current_path:
            return

        if not value or not item or item.value == value:
            return

        if item == self.scale:
            # Set the scale when setting the value.
            value[0] = min(max(value[0], self.min.value[0]), self.max.value[0])
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(
                self._stage.GetPrimAtPath(self._current_path)
            )
            omni.kit.commands.execute(
                "TransformPrimSRTCommand",
                path=self._current_path,
                new_translation=old_translation,
                new_rotation_euler=old_rotation_euler,
                new_scale=Gf.Vec3d(value[0], value[0], value[0]),
            )

        # Set directly to the item
        item.value = value
        # This makes the manipulator updated
        self._item_changed(item)

    def _get_stage(self):
        if not self._stage:
            usd_context = omni.usd.get_context()
            self._stage: Usd.Stage = usd_context.get_stage()
        return self._stage

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def _on_kit_selection_changed(self):
        prim_paths = self._selection.get_selected_prim_paths()
        if not prim_paths:
            return

        prim = self._get_stage().GetPrimAtPath(prim_paths[0])
        if not prim.IsA(UsdGeom.Imageable):
            return

        self._current_path = prim_paths[0]

        (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(prim)

        scale = old_scale[0]
        _min = scale * 0.1
        _max = scale * 2.0
        self.set_floats(self.min, [_min])
        self.set_floats(self.max, [_max])
        self.set_floats(self.scale, [scale])

        # Position is changed
        self._item_changed(self.position)

    def _get_position(self):
        """Returns position of currently selected object"""
        if not self._current_path:
            return [0, 1e38, 0]

        # Get position directly from USD
        prim = self._get_stage().GetPrimAtPath(self._current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        position = [(bboxMin[0] + bboxMax[0]) * 0.5, bboxMax[1] + self._offset, (bboxMin[2] + bboxMax[2]) * 0.5]
        return position
