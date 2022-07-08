from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd
import omni.kit.commands
from pxr import Gf


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

    def __init__(self) -> None:
        super().__init__()

        self.scale = SliderModel.ValueItem()
        self.min = SliderModel.ValueItem()
        self.max = SliderModel.ValueItem(1)

        self.position = SliderModel.PositionItem()

        # Current selection
        self.current_path = ""
        self.stage_listener = None
        self.usd_context = omni.usd.get_context()
        self.stage: Usd.Stage = self.usd_context.get_stage()

        # Track selection
        self.selection = self.usd_context.get_selection()
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Slider Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            prim_paths = self.selection.get_selected_prim_paths()
            if not prim_paths:
                self._item_changed(self.position)
                # Revoke the Tf.Notice listener, we don't need to update anything
                if self.stage_listener:
                    self.stage_listener.Revoke()
                    self.stage_listener = None
                return
            prim = self.stage.GetPrimAtPath(prim_paths[0])
            if not prim.IsA(UsdGeom.Imageable):
                return

            self.current_path = prim_paths[0]

            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(prim)

            scale = old_scale[0]
            _min = scale * 0.1
            _max = scale * 2.0
            self.set_floats(self.min, [_min])
            self.set_floats(self.max, [_max])
            self.set_floats(self.scale, [scale])

            # Add a Tf.Notice listener to update the position
            if not self.stage_listener:
                self.stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, self.stage)

            # Position is changed   
            self._item_changed(self.position)      
            
    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        for p in notice.GetChangedInfoOnlyPaths():
            if self.current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)    

    def get_item(self, identifier):
        if identifier == "position":
            return self.position
        if identifier == "value":
            return self.scale
        if identifier == "min":
            return self.min
        if identifier == "max":
            return self.max

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value
        return []

    def set_floats(self, item, value):
        if not self.current_path:
            return

        if not value or not item or item.value == value:
            return

        if item == self.scale:
            # Set the scale when setting the value.
            value[0] = min(max(value[0], self.min.value[0]), self.max.value[0])
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(
                self.stage.GetPrimAtPath(self.current_path)
            )
            omni.kit.commands.execute(
                "TransformPrimSRTCommand",
                path=self.current_path,
                new_translation=old_translation,
                new_rotation_euler=old_rotation_euler,
                new_scale=Gf.Vec3d(value[0], value[0], value[0]),
            )

        # Set directly to the item
        item.value = value
        # This makes the manipulator updated
        self._item_changed(item)

    def get_position(self):
        """Returns position of currently selected object"""
        if not self.current_path:
            return [0, 0, 0]

        # Get position directly from USD
        prim = self.stage.GetPrimAtPath(self.current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        x_Pos = (bboxMin[0] + bboxMax[0]) * 0.5
        y_Pos = (bboxMax[1] + 10)
        z_Pos = (bboxMin[2] + bboxMax[2]) * 0.5
        position = [x_Pos, y_Pos, z_Pos]
        return position
