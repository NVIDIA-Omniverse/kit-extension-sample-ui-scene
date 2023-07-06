# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["WidgetInfoExtension"]

from .widget_info_manipulator import WidgetInfoManipulator
from .widget_info_model import WidgetInfoModel
from omni.kit.viewport.registry import RegisterScene
import omni.ext


class WidgetInfoExtension(omni.ext.IExt):
    """The entry point to the extension"""

    def on_startup(self, ext_id):
        self._manipulator_registry = RegisterScene(
            lambda *_: WidgetInfoManipulator(model=WidgetInfoModel()), "WidgetInfoManipulator"
        )

    def on_shutdown(self):
        self._manipulator_registry = None
