import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

from .viewport_scene import ViewportSceneInfo

class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self) -> None:
        super().__init__()
        self.viewport_scene = None

    def on_startup(self, ext_id):
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id)

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None