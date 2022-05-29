## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["WidgetInfoManipulator"]
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class WidgetInfoManipulator(sc.Manipulator):
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
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Label
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        widget = sc.Widget(500, 150, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                        with widget.frame:
                            with ui.ZStack():
                                ui.Rectangle(
                                    style={
                                        "background_color": cl(0.2),
                                        "border_color": cl(0.7),
                                        "border_width": 2,
                                        "border_radius": 4,
                                    }
                                )
                                with ui.VStack(style={"font_size": 24}):
                                    ui.Spacer(height=4)
                                    with ui.ZStack(style={"margin": 1}, height=30):
                                        ui.Rectangle(
                                            style={
                                                "background_color": cl(0.0),
                                            }
                                        )
                                        ui.Line(
                                            style={"color": cl(0.7), "border_width": 2}, alignment=ui.Alignment.BOTTOM
                                        )
                                        ui.Label(
                                            "Hello world, I am a scene.Widget!", height=0, alignment=ui.Alignment.CENTER
                                        )

                                    ui.Spacer(height=4)
                                    ui.Label(
                                        f"Prim:{self.model.get_item('name')}", height=0, alignment=ui.Alignment.CENTER
                                    )

                                    # setup some model, just for simple demonstration here
                                    model = ui.SimpleFloatModel()

                                    def update_scale(prim_name):
                                        print(f"changing scale of {prim_name}")

                                    model.add_value_changed_fn(lambda p=self.model.get_item("name"): update_scale(p))

                                    ui.Spacer(height=10)
                                    with ui.HStack():
                                        ui.Spacer(width=10)
                                        ui.Label("scale", height=0, width=0)
                                        ui.Spacer(width=5)
                                        ui.FloatSlider(model)
                                        ui.Spacer(width=10)
                                    ui.Spacer(height=4)
                                    ui.Spacer()

    def on_model_updated(self, item):
        # Regenerate the mesh
        self.invalidate()
