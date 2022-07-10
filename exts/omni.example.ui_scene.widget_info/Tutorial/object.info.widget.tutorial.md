# How to make a Object Info Widget Extension
This guide will provide you with a starting point for displaying Object Info and nesting these modules into a Widget. A Widget is a useful utility in `Omniverse Kit` that can be used to add features such as buttons and sliders.


# Learning Objectives
In this guide you will learn how to:
 - Create a Widget Extension 
 - Use Omniverse UI Framework
 - Create a label
 - (optional) Create a toggle button feature
 - (optional) Create a slider

# Prerequisites

It is recommended that you have completed the following:

- [Extension Enviroment Tutorial](https://github.com/NVIDIA-Omniverse/ExtensionEnvironmentTutorial)
- [How to make an extension to display Object Info](../../omni.example.ui_scene.object_info/Tutorial/object_info.tutorial.md) 

# Step 1: Create a Widget Module

In this series of steps, you will be setting up your Extension to create a module needed for a widget.

## Step 1.1: Clone Slider Tutorial Branch

 Clone the `slider-tutorial-start` branch of the `kit-extension-sample-ui-scene` [github respositiory](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene) to get the assets needed for this hands-on lab. 

 ## Step 1.2: Add Extension Path to Extension Manager

Open the `Extensions Manager` in `Omniverse Code` 

Select gear icon to display `Extension Search Paths`. 

Use the <span style="color:green">green</span> :heavy_plus_sign: to add the path to `exts/slider-tutorial-start` from the cloned directory.

![](./Images/add_ext.PNG)



:memo: Check that the `UI Scene Object Info` Extension is enabled in the `Extensions Manager` and working by creating a new primitive in the `Viewport` and selecting it, the object's path and info should be displayed above the object.


## Step 1.3 Open VS Code with Shortcut

Open `VS Code` directly from the `Extension Manager`

![](./Images/openVS.PNG)

:bulb:If you would like to know more about how to create the modules for displaying Object Info, [check out the guide here.](../../omni.example.ui_scene.object_info/Tutorial/object_info.tutorial.md)


## Step 1.4: Create the Module

Create a new module called `object_info_widget.py` in the `exts` hierarchy that our other modules are located in. 

This will be our widget module.

`object_info_widget.py` will be building off the Object Info modules provided for you. You will see these modules as `object_info_manipulator.py`, `object_info_model.py`, `viewport_scene.py`, and an updated `extension.py`.


:memo: Visual Studio Code (VS Code) is our preferred IDE, hence forth referred to throughout this guide.

## Step 1.5: Set up Widget Class

Inside of the `object_info_widget.py`, import `omni.ui` then create the `WidgetInfoManipulator` class to nest our functions. After, initialize our methods, as so:

   ```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class WidgetInfoManipulator(sc.Manipulator):
     def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.destroy()

    def destroy(self):
        self._root = None
        self._name_label = None
```

This widget will house our widget info to make the information contrasted in the viewport and add other utilities later on.

You will accomplish this by creating a box for the label with a background color.

## Step 1.6: Build the widget

Let's define this as `on_build_widgets` and use the `Omniverse UI Framework` to create the label for this widget in a `ZStack`. [See here for more documentation on Omniverse UI Framework](https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.ui/docs/index.html).

```python
...
    def on_build_widgets(self):
        with ui.ZStack():
```

Once you have established the UI layout, you can create the background for the widget using `ui.Rectangle` and set the border attributes and background color. You can then create the `ui.Label` and set its alignment, as so:

```python
...
    def on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(style={
                "background_color": cl(0.2),
                "border_color": cl(0.7),
                "border_width": 2,
                "border_radius": 4,
            })
            self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)
```

## Step 1.7: Create Manipulator Functions

With a Manipulator, you need to define an `on_build` function.

This function is called when the model is changed so that the widget is rebuilt. [You can find more information about the Manipulator here.](https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.ui.scene/docs/Manipulator.html)

```python
...
        self.on_model_updated(None)

    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN): 
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    self._widget = sc.Widget(500, 150, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                    self._widget.frame.set_build_fn(self.on_build_widgets)
```

Now define `on_model_updated()` that was called above. In this function you need to establish what happens if nothing is selected, when to update the prims, and when to update the prim name, as so:

```python
...
    def on_model_updated(self, _):
        # if you don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return
        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        if self._root:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True
        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"
```

<details>
<summary>Click here for the end code of <b>widget_info_manipulator.py</b></summary>

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.destroy()

    def destroy(self):
        self._root = None
        self._name_label = None
    
    def on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(style={
                "background_color": cl(0.2),
                "border_color": cl(0.7),
                "border_width": 2,
                "border_radius": 4,
            })
            self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)

        self.on_model_updated(None)

    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN): 
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    self._widget = sc.Widget(500, 150, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                    self._widget.frame.set_build_fn(self.on_build_widgets)

    def on_model_updated(self, _):
        # if you don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return
        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        if self._root:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True
        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"
```

</details>


# Step 2: Update Viewport and Extension

Now that you have created a new module, it is important for us to bring this information into `viewport_scene.py` and update `extension.py` to reflect these new changes.

## Step 2.1: Import Widget Info

Begin by updating `viewport_scene.py` and importing `WidgetInfoManipulator` at the top of the file with the other imports.

```python
from omni.ui import scene as sc
import omni.ui as ui

from .object_info_manipulator import ObjInfoManipulator
from .object_info_model import ObjInfoModel
# NEW
from .widget_info_manipulator import WidgetInfoManipulator
# END NEW
```

### Step 2.2: Add Display Widget

Inside the `ViewportSceneInfo` class, you will add a `display_widget` parameter to `__init__()`:

```python
...
class ViewportSceneInfo():
    # NEW PARAMETER: display_widget
    def __init__(self, viewport_window, ext_id, display_widget) -> None:
        self.scene_view = None
        self.viewport_window = viewport_window
...
```

### Step 2.3: Use `display_widget`

Use `display_widget` to control whether to show `WidgetInfoManipulator` or `ObjInfoManipulator` as so:

```python
...
class ViewportSceneInfo():
    # NEW PARAMETER: display_widget
    def __init__(self, viewport_window, ext_id, display_widget) -> None:
        self.scene_view = None
        self.viewport_window = viewport_window

        with self.viewport_window.get_frame(ext_id):
            self.scene_view = sc.SceneView()

            with self.scene_view.scene:
              # NEW
                if display_widget:
                    WidgetInfoManipulator(model=ObjInfoModel())                    
                else:
              # END NEW
                    ObjInfoManipulator(model=ObjInfoModel())
...
```
<details>
<summary>Click here for the updated <b>viewport_scene.py</b></summary>

```python
from omni.ui import scene as sc
import omni.ui as ui

from .object_info_manipulator import ObjInfoManipulator
from .object_info_model import ObjInfoModel
from .widget_info_manipulator import WidgetInfoManipulator

class ViewportSceneInfo():
    def __init__(self, viewport_window, ext_id, display_widget) -> None:
        self.scene_view = None
        self.viewport_window = viewport_window

        with self.viewport_window.get_frame(ext_id):
            self.scene_view = sc.SceneView()

            with self.scene_view.scene:
                if display_widget:
                    WidgetInfoManipulator(model=ObjInfoModel())                    
                else:
                    ObjInfoManipulator(model=ObjInfoModel())

            self.viewport_window.viewport_api.add_scene_view(self.scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.scene_view:
            self.scene_view.scene.clear()

            if self.viewport_window:
                self.viewport_window.viewport_api.remove_scene_view(self.scene_view)
            
        self.viewport_window = None
        self.scene_view = None
```

</details>

<br>

## Step 3: Update `extension.py`

Now that you have created the widget and passed it into the viewport, you need to call this in the `extension.py` module for it to function.
### Step 3.1: Edit the Class Name

Start by changing the class name of `extension.py` from `MyExtension` to something more descriptive, like `ObjectInfoWidget`:

```python
...

## Replace ##
class MyExtension(omni.ext.IExt):

## With ##
class ObjectInfoWidget(omni.ext.IExt):
## END ##

    def __init__(self) -> None:
        super().__init__()
        self.viewportScene = None
```

### Step 3.2: Pass the Parameter

Pass the new parameter in `on_startup()` as follows:

```python
...
    def on_startup(self, ext_id):
        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        # NEW PARAMETER PASSED
        self.viewportScene = ViewportSceneInfo(viewport_window, ext_id, True)
...
```

<details>
<summary>Click here for the updated <b>extension.py</b> module </summary>

```python
import omni.ext
import omni.ui as ui
from omni.ui import scene as sc
from omni.ui import color as cl
from omni.kit.viewport.utility import get_active_viewport_window
from .viewport_scene import ViewportSceneInfo


class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        self.viewportScene = None

    def on_startup(self, ext_id):
        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        self.viewportScene = ViewportSceneInfo(viewport_window, ext_id, True)

    def on_shutdown(self):
        if self.viewportScene:
            self.viewportScene.destroy()
            self.viewportScene = None
```

</details>

Excellent, You should now see these updates in Omniverse Code at this point.

![](./Images/step2_complete.gif)


## Step 4: Create a Toggle Button

In this section you will create a button that enables us to turn the object info widget on and off in the viewport. This feature is built in `extension.py` and is an optional section. If you do not want the toggle button, feel free to skip this part. 

## Step 4.1: Add the button to `extension.py`

First define new properties in `extension.py` for `viewport_scene`,`widget_view`, and `ext_id`, as follows:

```python
...
class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        # NEW VALUES
        self.viewport_scene = None
        self.widget_view_on = False
        self.ext_id = None
        # END NEW
```

### Step 4.2 Update Startup

Update `on_startup()` to create a new window for the button. 

### Step 4.3 Passs `self.widget_view_on` into ViewportSceneInfo

```python
...
    def on_startup(self, ext_id):
        # NEW: Window with a label and button to toggle the widget / info 
        self.window = ui.Window("Toggle Widget View", width=300, height=300)
        self.ext_id = ext_id
        with self.window.frame:
            with ui.HStack(height=0):
                ui.Label("Toggle Widget View", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.Button("Toggle Widget", clicked_fn=self.toggle_view)
        # END NEW

        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        # NEW: passed in our new value self.widget_view_on
        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id, self.widget_view_on)
...
```
### Step 4.4 Create the Toggle

Define `toggle_view()`.

This function will be bound to the button's clicked function, thus requiring an `if` statement to check when the button is on/off:

```python
...
    # NEW: New function that is binded to our button's clicked_fn
    def toggle_view(self):
        self.reset_viewport_scene()
        self.widget_view_on = not self.widget_view_on
        if self.widget_view_on:
            self._toggle_button.text = "Toggle Widget Info Off"
        else:
            self._toggle_button.text = "Toggle Widget Info On"
        viewport_window = get_active_viewport_window()
        self.viewport_scene = ViewportSceneInfo(viewport_window, self.ext_id, self.widget_view_on)
    # END NEW
...
```

### Step 4.5: Create Reset Viewport Scene Function

This button is used in more than one spot, therefore define `reset_viewport_scene()`.

This function will purge our viewport scene when the button is reset.

```python
...
    # NEW: New function for resetting the viewport scene (since this will be used in more than one spot)
    def reset_viewport_scene(self):
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None
    # END NEW
...
```

### Step 4.6: Reset Viewport Scene on Shutdown

Update `on_shutdown` to remove the `viewport_scene` parameters you moved into the reset function and then call that function.

```python
...
    def on_shutdown(self):
        # NEW: Moved code block to a function and call it
        self.reset_viewport_scene()
        # END NEW
```

<br>

<details>
<summary>Click here for the updated <b>extension.py</b> module </summary>

```python
import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window
from .viewport_scene import ViewportSceneInfo


class ObjectInfoWidget(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()
        self.viewport_scene = None
        self.widget_view_on = False
        self.ext_id = None

    def on_startup(self, ext_id):
        self.window = ui.Window("Toggle Widget View", width=300, height=300)
        self.ext_id = ext_id
        with self.window.frame:
            with ui.HStack(height=0):
                ui.Label("Toggle Widget View", alignment=ui.Alignment.CENTER_TOP, style={"margin": 5})
                ui.Button("Toggle Widget", clicked_fn=self.toggle_view)

        #Grab a reference to the viewport
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id, self.widget_view_on)

    def toggle_view(self):
        self.reset_viewport_scene()
        self.widget_view_on = not self.widget_view_on
        if self.widget_view_on:
            self._toggle_button.text = "Toggle Widget Info Off"
        else:
            self._toggle_button.text = "Toggle Widget Info On"
        viewport_window = get_active_viewport_window()
        self.viewport_scene = ViewportSceneInfo(viewport_window, self.ext_id, self.widget_view_on)

    def reset_viewport_scene(self):
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None

    def on_shutdown(self):
        self.reset_viewport_scene()

```

</details>

<br>

Here is what you should see in the viewport at this point:

<br>

![](./Images/togglewidget_window.gif)

## Step 5: Add a Slider

In this step, you will be adding a slider to the widget. This slider will change the scale of the object. This is an optional step and may be skipped as it is just to showcase a simple addition of what a widget can do. For a more complex slider, [check out the guide to `Slider Manipulator` here.](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/blob/main/exts/omni.example.ui_scene.slider_manipulator/Tutorial/slider_Manipulator_Tutorial.md)

### Step 5.1: Add to `widget_info_manipulator.py`

Use `omni.ui` to build the framework for the slider in the function `on_build_widgets()`.

This slider is an optional feature to the widget but is a great way to add utility. 

 ```python
...
    def on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(style={
                "background_color": cl(0.2),
                "border_color": cl(0.7),
                "border_width": 2,
                "border_radius": 4,
            })
            # NEW: Adding the Slider to the widget in the scene
            with ui.VStack(style={"font_size": 24}):
                self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)
                # setup some model, just for simple demonstration here
                self._slider_model = ui.SimpleFloatModel()
                ui.Spacer(height=5)
                with ui.HStack():
                    ui.Spacer(width=10)
                    ui.Label("scale", height=0, width=0)
                    ui.Spacer(width=5)
                    ui.FloatSlider(self._slider_model)
                    ui.Spacer(width=5)
                ui.Spacer(height=5)

              # END NEW
        self.on_model_updated(None)
...
 ```
### Step 5.2: Update the Scale with a Slider Function

Add a new function that will scale the model when the slider is dragged.

Define this function after `on_model_updated` and name it `update_scale`.

 ```python
 ...
    def on_model_updated(self, _):
        # if you don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return
        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        if self._root:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True

        # NEW
        # Update the slider
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")
            stage = self.model.usd_context.get_stage()
            prim = stage.GetPrimAtPath(self.model.current_path)
            scale = prim.GetAttribute("xformOp:scale")
            scale.Set(Gf.Vec3d(value, value, value))      

        if self._slider_model:
            self._slider_subscription = None
            self._slider_model.as_float = 1.0
            self._slider_subscription = self._slider_model.subscribe_value_changed_fn(
                lambda m, p=self.model.get_item("name"): update_scale(p, m.as_float)
            )
        # END NEW
 ...
 ```

 <details>
 <summary>Click here for the updated `widget_info_manipulator.py` module  </summary>

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui
from pxr import Gf


class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.destroy()

    def destroy(self):
        self._root = None
        self._name_label = None
        self._slider_model = None

    def on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(style={
                "background_color": cl(0.2),
                "border_color": cl(0.7),
                "border_width": 2,
                "border_radius": 4,
            })
            with ui.VStack():
                self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)
                # setup some model, just for simple demonstration here
                self._slider_model = ui.SimpleFloatModel()
                ui.Spacer(height=5)
                with ui.HStack():
                    ui.Spacer(width=10)
                    ui.Label("scale", height=0, width=0)
                    ui.Spacer(width=5)
                    ui.FloatSlider(self._slider_model)
                    ui.Spacer(width=5)
                ui.Spacer(height=5)
        self.on_model_updated(None)

    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        self._root = sc.Transform(visibile=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN): 
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    self._widget = sc.Widget(500, 150, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                    self._widget.frame.set_build_fn(self.on_build_widgets)

    def on_model_updated(self, _):
        # if you don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return
        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        if self._root:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True

        # Update the slider
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")
            stage = self.model.usd_context.get_stage()
            prim = stage.GetPrimAtPath(self.model.current_path)
            scale = prim.GetAttribute("xformOp:scale")
            scale.Set(Gf.Vec3d(value, value, value))      

        if self._slider_model:
            self._slider_subscription = None
            self._slider_model.as_float = 1.0
            self._slider_subscription = self._slider_model.subscribe_value_changed_fn(
                lambda m, p=self.model.get_item("name"): update_scale(p, m.as_float)
            )

        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"
```

 </details>

 <br>

 Here is what is created in the viewport of Omniverse Code:
<br>

 ![](./Images/sliderWorking.gif)

 # Congratulations!

 You have successfully created a Widget Info Extension! 