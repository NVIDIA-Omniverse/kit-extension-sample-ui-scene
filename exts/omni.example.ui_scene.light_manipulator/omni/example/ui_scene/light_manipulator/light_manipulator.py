# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__all__ = ["LightManipulator"]

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.kit
import omni.kit.commands

INTENSITY_SCALE = 500.0

ARROW_WIDTH = 0.015
ARROW_HEIGHT = 0.1
ARROW_P = [
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
]

ARROW_VC = [3, 3, 3, 3, 4]
ARROW_VI = [i for i in range(sum(ARROW_VC))]


class _ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact is the focused window!
            # And there's no good solution to this when mutliple Viewport-1 instances are open; so we just have to
            # operate on all Viewports for a given usd_context.
            import omni.kit.viewport_legacy as vp

            vpi = vp.acquire_viewport_interface()
            for instance in vpi.get_instance_list():
                window = vpi.get_viewport_window(instance)
                if not window:
                    continue
                focused_windows.append(window)
            if focused_windows:
                self._focused_windows = focused_windows
                for window in self._focused_windows:
                    # Disable the selection_rect, but enable_picking for snapping
                    window.disable_selection_rect(True)
        except Exception:
            pass


class _DragGesture(sc.DragGesture):
    """"Gesture to disable rectangle selection in the viewport legacy"""
    def __init__(self, manipulator, orientation, flag):
        super().__init__()
        self._manipulator = manipulator
        # record this _previous_ray_point to get the mouse moved vector
        self._previous_ray_point = None
        # this defines the orientation of the move, 0 means x, 1 means y, 2 means z. It's a list so that we can move a selection
        self.orientations = orientation
        # global flag to indicate if the manipulator changes all the width, height and intensity, rectangle manipulator
        # in the example
        self.is_global = len(self.orientations) > 1
        # this defines the negative or positive of the move. E.g. when we move the positive x line to the right, it
        # enlarges the width, and when we move the negative line to the left, it also enlarges the width
        # 1 means positive and -1 means negative. It's a list so that we can reflect list orientation
        self.flag = flag

    def on_began(self):
        # When the user drags the slider, we don't want to see the selection
        # rect. In Viewport Next, it works well automatically because the
        # selection rect is a manipulator with its gesture, and we add the
        # slider manipulator to the same SceneView.
        # In Viewport Legacy, the selection rect is not a manipulator. Thus it's
        # not disabled automatically, and we need to disable it with the code.
        self.__disable_selection = _ViewportLegacyDisableSelection()

        # initialize the self._previous_ray_point
        self._previous_ray_point = self.gesture_payload.ray_closest_point

        # record the previous value for the model
        self.model = self._manipulator.model
        if 0 in self.orientations:
            self.width_item = self.model.width
            self._manipulator.model.set_item_value(self.width_item, self.model.get_as_floats(self.width_item))
        if 1 in self.orientations:
            self.height_item = self.model.height
            self._manipulator.model.set_item_value(self.height_item, self.model.get_as_floats(self.height_item))
        if 2 in self.orientations or self.is_global:
            self.intensity_item = self.model.intensity
            self._manipulator.model.set_item_value(self.intensity_item, self.model.get_as_floats(self.intensity_item))

    def on_changed(self):
        object_ray_point = self.gesture_payload.ray_closest_point
        # calculate the ray moved vector
        moved = [a - b for a, b in zip(object_ray_point, self._previous_ray_point)]
        # transfer moved from world to object space, [0] to make it a normal, not point
        moved = self._manipulator._x_xform.transform_space(sc.Space.WORLD, sc.Space.OBJECT, moved + [0])
        # 2.0 because `_shape_xform.transform` is a scale matrix and it means
        # the width of the rectangle is twice the scale matrix.
        moved_x = moved[0] * 2.0 * self.flag[0]
        moved_y = moved[1] * 2.0 * (self.flag[1] if self.is_global else self.flag[0])
        moved_z = moved[2] * self.flag[0]

        # update the self._previous_ray_point
        self._previous_ray_point = object_ray_point

        # since self._shape_xform.transform = [x, 0, 0, 0, 0, y, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        # when we want to update the manipulator, we are actually updating self._manipulator._shape_xform.transform[0]
        # for width and self._manipulator._shape_xform.transform[5] for height and
        # self._manipulator._shape_xform.transform[10] for intensity
        width = self._manipulator._shape_xform.transform[0]
        height = self._manipulator._shape_xform.transform[5]
        intensity = self._manipulator._shape_xform.transform[10]

        self.width_new = width + moved_x
        self.height_new = height + moved_y

        # update the USD as well as update the ui
        if 0 in self.orientations:
            # update the data in the model
            self.model.set_floats(self.width_item, self.width_new)
            self._manipulator._shape_xform.transform[0] = self.width_new
        if 1 in self.orientations:
            # update the data in the model
            self.model.set_floats(self.height_item, self.height_new)
            self._manipulator._shape_xform.transform[5] = self.height_new
        if 2 in self.orientations:
            self._manipulator._shape_xform.transform[10] += moved_z
            self.intensity_new = self._manipulator._shape_xform.transform[10] * INTENSITY_SCALE
            self.model.set_floats(self.intensity_item, self.intensity_new)
        if self.is_global:
            # need to update the intensity in a different way
            intensity_new = intensity * width * height / (self.width_new * self.height_new)
            self._manipulator._shape_xform.transform[10] = intensity_new
            self.intensity_new = intensity_new * INTENSITY_SCALE
            self.model.set_floats(self.intensity_item, self.intensity_new)

    def on_ended(self):
        # This re-enables the selection in the Viewport Legacy
        self.__disable_selection = None

        if self.is_global:
            # start group command
            omni.kit.undo.begin_group()
        if 0 in self.orientations:
            self.model.set_floats_commands(self.width_item, self.width_new)
        if 1 in self.orientations:
            self.model.set_floats_commands(self.height_item, self.height_new)
        if 2 in self.orientations or self.is_global:
            self.model.set_floats_commands(self.intensity_item, self.intensity_new)
        if self.is_global:
            # end group command
            omni.kit.undo.end_group()


class LightManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._shape_xform = None

    def __del__(self):
        self.model = None

    def _build_shape(self):
        if not self.model:
            return
        if self.model.width and self.model.height and self.model.intensity:
            x = self.model.get_as_floats(self.model.width)
            y = self.model.get_as_floats(self.model.height)
            # this INTENSITY_SCALE is too make the transform a reasonable length with large intensity number
            z = self.model.get_as_floats(self.model.intensity) / INTENSITY_SCALE
            self._shape_xform.transform = [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1]

    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        model = self.model
        if not model:
            return

        # if we don't have selection then just return
        prim_path_item = model.prim_path
        prim_path = prim_path_item.value if prim_path_item else None
        if not prim_path:
            return

        # Style settings, as kwargs
        thickness = 1
        hover_thickness = 3
        color = cl.yellow
        shape_style = {"thickness": thickness, "color": color}

        def set_thickness(sender, shapes, thickness):
            for shape in shapes:
                shape.thickness = thickness

        self.__root_xf = sc.Transform(model.get_as_floats(model.transform))
        with self.__root_xf:
            self._x_xform = sc.Transform()
            with self._x_xform:
                self._shape_xform = sc.Transform()
                # Build the shape's transform
                self._build_shape()
                with self._shape_xform:
                    # Build the shape geomtery as unit-sized
                    h = 0.5
                    z = -1.0
                    # the rectangle
                    shape1 = sc.Line((-h, h, 0), (h, h, 0), **shape_style)
                    shape2 = sc.Line((-h, -h, 0), (h, -h, 0), **shape_style)
                    shape3 = sc.Line((h, h, 0), (h, -h, 0), **shape_style)
                    shape4 = sc.Line((-h, h, 0), (-h, -h, 0), **shape_style)
                    # add gesture to the lines of the rectangle to update width or height of the light
                    vertical_hover_gesture = sc.HoverGesture(
                        on_began_fn=lambda sender: set_thickness(sender, [shape1, shape2], hover_thickness),
                        on_ended_fn=lambda sender: set_thickness(sender, [shape1, shape2], thickness),
                    )
                    shape1.gestures = [_DragGesture(self, [1], [1]), vertical_hover_gesture]
                    shape2.gestures = [_DragGesture(self, [1], [-1]), vertical_hover_gesture]

                    horizontal_hover_gesture = sc.HoverGesture(
                        on_began_fn=lambda sender: set_thickness(sender, [shape3, shape4], hover_thickness),
                        on_ended_fn=lambda sender: set_thickness(sender, [shape3, shape4], thickness),
                    )
                    shape3.gestures = [_DragGesture(self, [0], [1]), horizontal_hover_gesture]
                    shape4.gestures = [_DragGesture(self, [0], [-1]), horizontal_hover_gesture]

                    # create z-axis to indicate the intensity
                    z1 = sc.Line((h, h, 0), (h, h, z), **shape_style)
                    z2 = sc.Line((-h, -h, 0), (-h, -h, z), **shape_style)
                    z3 = sc.Line((h, -h, 0), (h, -h, z), **shape_style)
                    z4 = sc.Line((-h, h, 0), (-h, h, z), **shape_style)

                    def make_arrow(translate):
                        vert_count = len(ARROW_VI)
                        with sc.Transform(
                            transform=sc.Matrix44.get_translation_matrix(translate[0], translate[1], translate[2])
                            * sc.Matrix44.get_rotation_matrix(0, -180, 0, True)
                        ):
                            return sc.PolygonMesh(ARROW_P, [color] * vert_count, ARROW_VC, ARROW_VI, visible=False)

                    # arrows on the z-axis
                    arrow_1 = make_arrow((h, h, z))
                    arrow_2 = make_arrow((-h, -h, z))
                    arrow_3 = make_arrow((h, -h, z))
                    arrow_4 = make_arrow((-h, h, z))

                    # the line underneath the arrow which is where the gesture applies
                    z1_arrow = sc.Line((h, h, z), (h, h, z - ARROW_HEIGHT), **shape_style)
                    z2_arrow = sc.Line((-h, -h, z), (-h, -h, z - ARROW_HEIGHT), **shape_style)
                    z3_arrow = sc.Line((h, -h, z), (h, -h, z - ARROW_HEIGHT), **shape_style)
                    z4_arrow = sc.Line((-h, h, z), (-h, h, z - ARROW_HEIGHT), **shape_style)

                    def set_visible(sender, shapes, thickness, arrows, visible):
                        set_thickness(sender, shapes, thickness)
                        for arrow in arrows:
                            arrow.visible = visible

                    thickness_group = [z1, z1_arrow, z2, z2_arrow, z3, z3_arrow, z4, z4_arrow]
                    visible_group = [arrow_1, arrow_2, arrow_3, arrow_4]
                    visible_arrow_gesture = sc.HoverGesture(
                        on_began_fn=lambda sender: set_visible(sender, thickness_group, hover_thickness, visible_group, True),
                        on_ended_fn=lambda sender: set_visible(sender, thickness_group, thickness, visible_group, False),
                    )
                    gestures = [_DragGesture(self, [2], [-1]), visible_arrow_gesture]
                    z1_arrow.gestures = gestures
                    z2_arrow.gestures = gestures
                    z3_arrow.gestures = gestures
                    z4_arrow.gestures = gestures

                    # create 4 rectangles at the corner, and add gesture to update width, height and intensity at the same time
                    s = 0.03

                    def make_corner_rect(translate):
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(translate[0], translate[1], translate[2])):
                            return sc.Rectangle(s, s, color=0x0)

                    r1 = make_corner_rect((h - 0.5 * s, -h + 0.5 * s, 0))
                    r2 = make_corner_rect((h - 0.5 * s, h - 0.5 * s, 0))
                    r3 = make_corner_rect((-h + 0.5 * s, h - 0.5 * s, 0))
                    r4 = make_corner_rect((-h + 0.5 * s, -h + 0.5 * s, 0))

                    def set_color_and_visible(sender, shapes, thickness, arrows, visible, rects, color):
                        set_visible(sender, shapes, thickness, arrows, visible)
                        for rect in rects:
                            rect.color = color

                    highlight_group = [shape1, shape2, shape3, shape4] + thickness_group
                    color_group = [r1, r2, r3, r4]
                    hight_all_gesture = sc.HoverGesture(
                        on_began_fn=lambda sender: set_color_and_visible(sender, highlight_group, hover_thickness, visible_group, True, color_group, color),
                        on_ended_fn=lambda sender: set_color_and_visible(sender, highlight_group, thickness, visible_group, False, color_group, 0x0),
                    )
                    r1.gestures = [_DragGesture(self, [0, 1], [1, -1]), hight_all_gesture]
                    r2.gestures = [_DragGesture(self, [0, 1], [1, 1]), hight_all_gesture]
                    r3.gestures = [_DragGesture(self, [0, 1], [-1, 1]), hight_all_gesture]
                    r4.gestures = [_DragGesture(self, [0, 1], [-1, -1]), hight_all_gesture]

    def on_model_updated(self, item):
        # Regenerate the mesh
        if not self.model:
            return

        if item == self.model.transform:
            # If transform changed, update the root transform
            self.__root_xf.transform = self.model.get_as_floats(item)
        elif item == self.model.prim_path:
            # If prim_path or width or height or intensity changed, redraw everything
            self.invalidate()
        elif item == self.model.width or item == self.model.height or item == self.model.intensity:
            # Interpret None as changing multiple light shape settings
            self._build_shape()
