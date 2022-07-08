import omni.ext
from omni.kit.manipulator.viewport import ManipulatorFactory
from omni.kit.viewport.registry import RegisterScene
from .slider_registry import SliderRegistry


class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        self.slider_registry = RegisterScene(SliderRegistry, "omni.example.slider")
        self.slider_factory = ManipulatorFactory.create_manipulator(SliderRegistry)

    def on_shutdown(self):
        ManipulatorFactory.destroy_manipulator(self.slider_factory)
        self.slider_factory = None
        self.slider_registry.destroy()
        self.slider_registry = None
