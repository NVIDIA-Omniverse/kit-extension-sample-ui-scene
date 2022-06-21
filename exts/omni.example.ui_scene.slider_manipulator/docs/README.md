# Overview

We provide the End-to-End example that draws a 3D slider in the viewport overlay
on the top of the bounding box of the selected imageable. The slider controls
the scale of the prim. It has a custom manipulator, model, and gesture. When the
slider's value is changed, the manipulator processes the custom gesture that
changes the data in the model, which changes the data directly in the USD stage.

The viewport overlay is synchronized with the viewport using `Tf.Notice` that
watches the USD Camera.

![](../data/preview.png)

The extension name is `omni.example.ui_scene.slider_manipulator`.

## Manipulator

The manipulator is a very basic implementation of the slider in 3D space. The
main feature of the manipulator is that it redraws and recreates all the
children once the model is changed. It makes the code straightforward. It takes
the position and the slider value from the model, and when the user changes the
slider position, it processes a custom gesture. It doesn't write to the model
directly to let the user decide what to do with the new data and how the
manipulator should react to the modification. For example, if the user wants to
implement the snapping to the round value, it would be handy to do it in the
custom gesture.

## Model

The model contains the following named items:

 - `value` - the current value of the slider
 - `min` - the minimum value of the slider
 - `max` - the maximum value of the slider
 - `position` - the position of the slider in 3D space

The model demonstrates two main strategies working with the data.

The first strategy is that the model is the bridge between the manipulator and
the data, and it doesn't keep and doesn't duplicate the data. When the
manipulator requests the position from the model, the model computes the
position using USD API and returns it to the manipulator.

The first strategy is that the model can be a container of the data. For
example, the model pre-computes min and max values and passes them to the
manipulator once the selection is changed.

## Working with the main viewport

To display the manipulator, it should be parented to sc.SceneView object. It's
possible to create a new sc.SceneView object and overlay it with the viewport.
This way, it's necessary to synchronize the camera with the viewport.

Another way to put the manipulator to the viewport is to register it in the main
viewport `sc.SceneView`. This way, the manipulator's gestures can interact with
the gestures of the main transform manipulator. The Viewport Legacy and Viewport
Next have different ways to register manipulators. Viewport Legasyc has a
registry module, `ManipulatorFactory`. And the Viewport Next has registry object
`RegisterScene`. Fortunately, it's possible to write code that is compatible
with both of them.

```python
# Viewport Next: omni.kit.viewport.window
self._slider_registry = RegisterScene(SliderRegistry, "omni.example.ui_scene.slider_manipulator")
# Viewport Legacy: omni.kit.window.viewport
self._slider_factory = ManipulatorFactory.create_manipulator(SliderRegistry)
```

Both Viewport Legacy and Viewport Next will construct the given class under the
appropriate `sc.SceneView` object. The given class `SliderRegistry` is a simple
class that creates a manipulator.

```python
class SliderRegistry:
    """
    Created by omni.kit.viewport.registry or omni.kit.manipulator.viewport per
    viewport. Keeps the manipulator and some properties that are needed to the
    viewport.
    """

    def __init__(self, description: Optional[Dict[str, Any]] = None):
        self.__slider_manipulator = SliderManipulator(model=SliderModel(), gesture=SliderChangedGesture())

    def destroy(self):
        if self.__slider_manipulator:
            self.__slider_manipulator.destroy()
            self.__slider_manipulator = None
```

The manipulator will appear in both Viewport Legacy and Viewport Next and
correctly interact with other viewport manipulators, including camera transform,
object transform and rect selection manipulators. The rect selection of Viewport
Legacy is not implemented as a manipulator. Thus it requires additional code to
disable it when the user drags the slider.


```python
class ViewportLegacyDisableSelection:
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
```
