# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TestInfo"]

from omni.example.ui_scene.widget_info.widget_info_manipulator import WidgetInfoManipulator
from omni.ui import scene as sc
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
import omni.kit.app
import omni.kit.test


EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class WidgetInfoTestModelItem(sc.AbstractManipulatorItem):
    pass


class WidgetInfoTestModel(sc.AbstractManipulatorModel):
    def __init__(self):
        super().__init__()

        self.position = WidgetInfoTestModelItem()

    def get_item(self, identifier):
        if identifier == "position":
            return self.position
        if identifier == "name":
            return "Name"
        if identifier == "material":
            return "Material"

    def get_as_floats(self, item):
        if item == self.position:
            return [0, 0, 0]


class TestInfo(OmniUiTest):
    async def test_general(self):
        """Testing general look of the item"""
        window = await self.create_test_window(width=256, height=256)

        with window.frame:
            # Camera matrices
            projection = [1e-2, 0, 0, 0]
            projection += [0, 1e-2, 0, 0]
            projection += [0, 0, -2e-7, 0]
            projection += [0, 0, 1, 1]
            view = sc.Matrix44.get_translation_matrix(0, 0, 0)

            scene_view = sc.SceneView(sc.CameraModel(projection, view))
            with scene_view.scene:
                # The manipulator
                model = WidgetInfoTestModel()
                WidgetInfoManipulator(model=model)

        await omni.kit.app.get_app().next_update_async()
        model._item_changed(None)

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(threshold=100, golden_img_dir=TEST_DATA_PATH, golden_img_name="general.png")
