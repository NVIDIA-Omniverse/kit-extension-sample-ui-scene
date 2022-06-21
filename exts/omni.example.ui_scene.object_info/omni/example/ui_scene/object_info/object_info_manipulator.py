# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__all__ = ["ObjectInfoManipulator"]

from omni.ui import color as cl
from omni.ui import scene as sc
import omni.ui as ui

LEADER_LINE_CIRCLE_RADIUS = 2
LEADER_LINE_THICKNESS = 2
LEADER_LINE_SEGMENT_LENGTH = 20
VERTICAL_MULT = 1.5
HORIZ_TEXT_OFFSET = 5
LINE1_OFFSET = 3
LINE2_OFFSET = 0


class ObjectInfoManipulator(sc.Manipulator):
    """Manipulator that displays the object path and material assignment
    with a leader line to the top of the object's bounding box.
    """
    def on_build(self):
        """Called when the model is changed and rebuilds the whole manipulator"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        position = self.model.get_as_floats(self.model.get_item("position"))

        # Move everything to where the object is
        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Rotate everything to face the camera
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                # Leader lines with a small circle on the end
                sc.Arc(LEADER_LINE_CIRCLE_RADIUS, axis=2, color=cl.yellow)
                sc.Line([0, 0, 0], [0, LEADER_LINE_SEGMENT_LENGTH, 0],
                        color=cl.yellow, thickness=LEADER_LINE_THICKNESS)
                sc.Line([0, LEADER_LINE_SEGMENT_LENGTH, 0],
                        [LEADER_LINE_SEGMENT_LENGTH, LEADER_LINE_SEGMENT_LENGTH * VERTICAL_MULT, 0],
                        color=cl.yellow, thickness=LEADER_LINE_THICKNESS)

                # Shift text to the end of the leader line with some offset
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(
                        LEADER_LINE_SEGMENT_LENGTH + HORIZ_TEXT_OFFSET,
                        LEADER_LINE_SEGMENT_LENGTH * VERTICAL_MULT,
                        0)):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        # Offset each Label vertically in screen space
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, LINE1_OFFSET, 0)):
                            sc.Label(f"Path: {self.model.get_item('name')}",
                                     alignment=ui.Alignment.LEFT_BOTTOM)
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, LINE2_OFFSET, 0)):
                            sc.Label(f"Material: {self.model.get_item('material')}",
                                     alignment=ui.Alignment.LEFT_TOP)

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
