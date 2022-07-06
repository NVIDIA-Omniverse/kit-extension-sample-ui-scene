# How to make a Slider Manipulator
   In this guide you will learn how to draw a 3D slider in the viewport that overlays on the top of the bounding box of the selected primitive. This slider will control the scale of the primitive with a custom manipulator, model, and gesture. When the slider is changed, the manipulator processes the custom gesture that changes the data in the model, which changes the data directly in the USD stage. 

   ![](/Images/sliderPreview.png)

# Learning Objectives
 - TODO

 
 # Prereqs
  - TODO
 - Eric's guide - LINK
 - Spawning primitives guide - LINK
 - Object Info Guide - LINK
 


# Table of Contents
 - [Step 1: Create the extension](#step-1-create-the-extension)
    - [Step 1.1: Create new extension template](#step-11-create-new-extension-template)
    - [Step 1.2: Naming your extension](#step-12-naming-your-extension)
- [Step 2: Model Script](#step-2-model-script)
   - [Step 2.1: Import omni.ui and USD](#step-21-import-omniui-and-usd)
   - [Step 2.2: Model and Position Item Class](#step-22-model-and-position-item-class)
   - [Step 2.3: Current Selection and Tracking Selection](#step-23-current-selection-and-tracking-selection)
   - [Step 2.4: Set the stage ](#step-24-set-the-stage)
   - [Step 2.5: Tf.Notice Function](#step-25-tf-notice-function)
   - [Step 2.6: Set the position identifier and request position](#step-26-set-the-position-identifier-and-request-position)
   - [Step 2.7: Position from USD](#step-27-position-from-usd)
- [Step 3: Manipulator Script ](#step-3-manipulator-script)
   - [Step 3.1: Import omni.ui](#step-31-import-omniui)
   - [Step 3.2: Create Manipulator Class](#step-32-create-manipulator-class)
   - [Step 3.3: Call on_build and create the label](#step-33-call-onbuild-and-create-the-label)
   - [Step 3.4: Regenerate the manipulator](#step-34-regenerate-the-manipulator)
- [Step 4: Registry Script ](#step-4-registry-script)
  - [Step 4.1: Import from Model and Manipulator](#step-41-import-from-model-and-manipulator)
  - [Step 4.2: Disable Selection in Viewport Legacy](#step-42-disable-selection-in-viewport-legacy)
  - [Step 4.3: Slider Registry Class](#step-43-slider-registry-class)
- [Step 5: Update extension.py](#step-5-update-extensionpy)
  - [Step 5.1: Import Omniverse Viewport Library and Registry Script](#step-51-import-omniverse-viewport-library-and-registry-script)
  - [Step 5.2: References in on_startup](#step-52-references-in-onstartup)
  - [Step 5.3: Update on_shutdown](#step-53-update-onshutdown)
- [Step 6: Creating the slider widget ](#step-6-creating-the-slider-widget)
  - [Step 6.1: Geometry Properties](#step-61-geometry-properties)
  - [Step 6.2: Create the Line](#step-62-create-the-line)
  - [Step 6.3: Create the Circle](#step-63-create-the-circle)
- [Step 7: Set up the Model ](#step-7-set-up-the-model)
  - [Step 7.1: Import Omniverse Command Library](#step-71-import-omniverse-command-library)
  - [Step 7.2: Value Item Class](#step-72-valueitem-class)
  - [Step 7.3: Set Scale to Stage](#step-73-set-scale-to-stage)
  - [Step 7.4: Define identifiers](#step-74-define-identifiers)
  - [Step 7.5: Set Floats](#step-75-set-floats)
- [Step 8: Add Gestures ](#step-8-add-gestures)
  - [Step 8.1: SliderGradGesturePayload Class](#step-81-sliderdraggesturepayload-class)
  - [Step 8.2: SliderChangedGesture Class](#step-82-sliderchangedgesture-class)
  - [Step 8.3: _ArcGesturePriorities Class](#step-83-arcgesturepriorities-class)
  - [Step 8.4: _ArcGesture Class](#step-84-arcgesture-class)
  - [Step 8.5: Restructure Geometry Properties](#step-85-restructure-geometry-parameters)
  - [Step 8.6: Add Hover Gestures](#step-86-add-hover-gestures)
  - [Step 8.7: UI Getters and Setters](#step-87-ui-getters-and-setters)
  - [Step 8.8: Update on_build](#step-88-update-onbuild)
- [Congratulations!](#congratulations)



# Step 1: Create the extension
> :memo: Note: This is a review from Object Info guide. If you know how to create an extension, feel free to skip this step. 

In this section, we will walk you through how to create a new extension in Omniverse Code, including how to change how it is viewed in the Extension Manager.

## Step 1.1: Create new extension template
  In Omniverse Code navigate to the `Extensions` tab and create a new extension by clicking the ➕ icon in the upper left corner and select `New Extension Template Project`.

  ![](./Images/ext_tab.png)

  <icon>                       |  <new template>
:-------------------------:|:-------------------------:
![icon](./Images/icon_create.png "Plus Icon")  |  ![new template](./Images/new_template.png "New Extension Template")

<br>

A new extension template window and Visual Studio Code will open after you have selected the folder location, folder name, and extension ID.

## Step 1.2: Naming your extension

In the extension manager, you may have noticed that each extension has a title and description:

![](./Images/extensionManager_example.PNG)

We can change this in the `extension.toml` file by navigating to `VS Code` and editing the file there. It is important that we give our extension a detailed title and summary for the end user to understand what our extension will accomplish or display. Here is how we changed it for this guide:

```python
# The title and description fields are primarily for displaying extension info in UI
title = "UI Scene Slider Manipulator"
description="Interactive example of the slider manipulator with omni.ui.scene"
```


 <br><br>

# Step 2: Model script
### Theory:
In this step we will be creating the `sliderModel.py` script where we will be tracking the current selected primitive, calling the stage event, and getting the position directly from USD.

## Step 2.1: Import omni.ui and USD
After creating `sliderModely.py` in the same folder as `extension.py`, import the omni.ui and the necessary USD, as follows:

```python
from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd
```

## Step 2.2: Model and Position Item Class

Next, let's set up our Model class and Position Item class. The Model class tracks the positon and scale of the selected object and because we will be obtaining the position directly from USD, the Position Item class doesn't contain anything.

```python
from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd

# NEW
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

    def __init__(self) -> None:
        super().__init__()

        self.position = SliderModel.PositionItem()
# END NEW
```

## Step 2.3: Current Selection and Tracking Selection
In this section, we will be setting the variables for the current selection and tracking the selected, where we will also set parameters for the stage event later on. 

```python
...

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

    def __init__(self) -> None:
        super().__init__()

        self.position = SliderModel.PositionItem()

        # NEW
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
        # END NEW
```
## Step 2.4: Set the Stage
With our selection variables set, we now need to call the stage and  Stage Event then grab reference to the path of the primitives:

```python
...
    def get_stage(self):
        if not self.stage:
            usd_context = omni.usd.get_context()
            self.stage: Usd.Stage = usd_context.get_stage()
        return self.stage
 
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

            # Add a Tf.Notice listener to update the position
            if not self.stage_listener:
                self.stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, self.stage)

            # Position is changed   
            self._item_changed(self.position)    
            
```

## Step 2.5: Tf. Notice function
In the previous step, we created a Tf.Notice to update the position. Now, we will define the function for what happens when Tf.Notice is called:

```python
...

    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        for p in notice.GetChangedInfoOnlyPaths():
            if self.current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)    
```

## Step 2.6: Set the Position Identifier and Request Position
Let's define the identifier for Position like so:

```python
...

    def get_item(self, identifier):
        if identifier == "position":
            return self.position
```

And now, we will set item to request the position and get the value from the item:

```python
...

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value
        return []
```
## Step 2.7: Position from USD
In this last section of the Model script, we will be defining `get_position` to get position directly from USD, like so:

```python
...
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
```

<details>
<summary> Click here for the full Model script </summary>

```python
from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd

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

    def __init__(self) -> None:
        super().__init__()

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

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value
        return []

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
```

</details>

<br>
<br>

# Step 3: Manipulator Script
### Theory:
In this step, we will be creating `sliderManipulator.py` in the same folder as our Model script. The Manipulator class will define the `on_build` function as well as create the Label and regenerate the model.

## Step 3.1: Import omni.ui
After creating the Manipulator script, import omni.ui as follows:

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui
```
## Step 3.2: Create Manipulator class
Now, we will begin the SliderManipulator class and insert the init method:

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
```

## Step 3.3: Call on_build and create the Label
The `on_build` function is called when the model is changed and then will rebuild the slider. We will also create the Label for the slider and position it more towards the top of the screen.

```python
...

    def on_build(self):
        """Called when the model is changed and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        value = 0.0
        position = self.model.get_as_floats(self.model.get_item("position"))
        

        # Label
        with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
            with sc.Transform(scale_to=sc.Space.SCREEN):
                # Move it 5 points more to the top in the screen space
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                    sc.Label(f"{value:.1f}", alignment=ui.Alignment.CENTER_BOTTOM)

```

## Step 3.4: Regenerate the Manipulator
Finally, let's define `on_model_updated` to regenerate the manipulator:

```python
...
    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

<details>
<summary>Click here for the full Manipulator script </summary>

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        value = 0.0
        position = self.model.get_as_floats(self.model.get_item("position"))
        

        # Label
        with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
            with sc.Transform(scale_to=sc.Space.SCREEN):
                # Move it 5 points more to the top in the screen space
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                    sc.Label(f"{value:.1f}", alignment=ui.Alignment.CENTER_BOTTOM)

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

</details>

<br>
<br>

# Step 4: Registry Script

### Theory:

In this step, we will create `sliderRegistry.py` in the same location as the Model and Manipulator scripts. We will use the registry script to have the number display on the screen when the primitive is selected.

## Step 4.1: Import from Model and Manipulator

After creating the registry script, import from the Model and Manipulator, as well as import typing to help make the script more readable, like so:

```python
from .SliderModel import SliderModel
from .sliderManipulator import SliderManipulator
from typing import Any
from typing import Dict
from typing import Optional
```

## Step 4.2: Disable Selection in Viewport Legacy

We need to disable the selection in the viewport legacy first, so we will set `focused_windows` to do so and import from Omniverse Viewport Library, as so:

```python
...

class ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact the focused window!
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

## Step 4.3: Slider Registry Class
This class is created by `omni.kit.viewport.registry` or `omni.kit.manipulator.viewport` per viewport and will keep the manipulator and some other properties that are needed in the viewport:

```python
...
class SliderRegistry:
    """
    Created by omni.kit.viewport.registry or omni.kit.manipulator.viewport per
    viewport. Keeps the manipulator and some properties that are needed to the
    viewport.
    """

    def __init__(self, description: Optional[Dict[str, Any]] = None):
        self.__slider_manipulator = SliderManipulator(model=SliderModel(), gesture=None)

    def destroy(self):
        if self.__slider_manipulator:
            self.__slider_manipulator.destroy()
            self.__slider_manipulator = None

    # PrimTransformManipulator & TransformManipulator don't have their own visibility
    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, value):
        pass

    @property
    def categories(self):
        return ("manipulator",)

    @property
    def name(self):
        return "Example Slider Manipulator"
```

<details>
<summary>Click here for the full Registry script  </summary>

```python
from .SliderModel import SliderModel
from .sliderManipulator import SliderManipulator
from typing import Any
from typing import Dict
from typing import Optional

class ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact the focused window!
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

class SliderRegistry:
    """
    Created by omni.kit.viewport.registry or omni.kit.manipulator.viewport per
    viewport. Keeps the manipulator and some properties that are needed to the
    viewport.
    """

    def __init__(self, description: Optional[Dict[str, Any]] = None):
        self.__slider_manipulator = SliderManipulator(model=SliderModel(), gesture=None)

    def destroy(self):
        if self.__slider_manipulator:
            self.__slider_manipulator.destroy()
            self.__slider_manipulator = None

    # PrimTransformManipulator & TransformManipulator don't have their own visibility
    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, value):
        pass

    @property
    def categories(self):
        return ("manipulator",)

    @property
    def name(self):
        return "Example Slider Manipulator"
```

</details>

<br>
<br>

# Step 5: Update extension.py

### Theory

We still have the default code in `extension.py` so now we will update the code to reflect the the scripts we made. 

## Step 5.1: Import Omniverse Viewport Library and Registry Script

Let's begin by updating the imports at the top of `extension.py` to include the Omniverse Viewport Library and the new Registry script so that we can reference it later on:

```python
import omni.ext
# NEW
from omni.kit.manipulator.viewport import ManipulatorFactory
from omni.kit.viewport.registry import RegisterScene
from .sliderRegistry import SliderRegistry
# END NEW
```

## Step 5.2: References in on_startup

In this step, we will remove the default code in `on_startup` and replace it with a reference to the `slider_registry` and `slider_factory`, like so:

```python
...

class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        # NEW
        self.slider_registry = RegisterScene(SliderRegistry, "omni.example.slider")
        self.slider_factory = ManipulatorFactory.create_manipulator(SliderRegistry)
        # END NEW
```

## Step 5.3: Update on_shutdown

Now, we need to properly shutdown the extension. Let's remove the print statement and replace it with:

```python
...

    def on_shutdown(self):
        # NEW
        ManipulatorFactory.destroy_manipulator(self.slider_factory)
        self.slider_factory = None
        self.slider_registry.destroy()
        self.slider_registry = None
        # END NEW

```
<details>
<summary>Click here for the full extension script</summary>

```python
import omni.ext
# NEW
from omni.kit.manipulator.viewport import ManipulatorFactory
from omni.kit.viewport.registry import RegisterScene
from .sliderRegistry import SliderRegistry
# END NEW

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        # NEW
        self.slider_registry = RegisterScene(SliderRegistry, "omni.example.slider")
        self.slider_factory = ManipulatorFactory.create_manipulator(SliderRegistry)
        # END NEW

    def on_shutdown(self):
        # NEW
        ManipulatorFactory.destroy_manipulator(self.slider_factory)
        self.slider_factory = None
        self.slider_registry.destroy()
        self.slider_registry = None
        # END NEW
```

</details>

<br>

This is what you should see at this point in the viewport:

![](./Images/step5EndView.png)

<br>

# Step 6: Creating the Slider Widget

### Theory
Now that we have all of the variables and necessary properties referenced, let's start to create the slider widget. We will begin by creating the geometry needed for the widget, like the line, and then we will add a circle to the line. 

## Step 6.1: Geometry Properties

We are going to begin by adding new geometry to `sliderManipulator.py`. We will set the geometry properties like so:

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # NEW
        # Geometry properties
        self.width = 100
        self.thickness = 5
        self.radius = 5
        self.radius_hovered = 7
        # END NEW
```

## Step 6.2: Create the line

Next, we will create a line above the selected primities. Let's add this to `on_build`:

```python
...
    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        value = 0.0
        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            
            # NEW: Creates a line above the prim
            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * 1 - self.radius
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)
            # END NEW
```



This should be the result in your viewport:

![](./Images/step6Result.png)

## Step 6.3: Create the circle

We are still working in `sliderManipulator.py` and now we will be adding the circle on the line. This will also be added to `on_build` like so:

```python
...
   def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        value = 0.0
        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * 1 - self.radius
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

            # NEW
            # Circle
            circle_position = -self.width * 0.5 + self.width * 1
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(circle_position, 0, 0)):
                radius = self.radius
                sc.Arc(radius, axis=2, color=cl.gray)
            # END NEW
...
```

Now, your line in your viewport should look like this:

![](./Images/step6CircleResult.png)

<details>
<summary>Click here for the full Manipulator script</summary>

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Geometry properties
        self.width = 100
        self.thickness = 5
        self.radius = 5
        self.radius_hovered = 7

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        value = 0.0
        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * 1 - self.radius
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

            # Circle
            circle_position = -self.width * 0.5 + self.width * 1
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(circle_position, 0, 0)):
                radius = self.radius
                sc.Arc(radius, axis=2, color=cl.gray)
            
            # Label
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                with sc.Transform(scale_to=sc.Space.SCREEN):
                    # Move it 5 points more to the top in the screen space
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                        sc.Label(f"{value:.1f}", alignment=ui.Alignment.CENTER_BOTTOM)

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

</details>

<br>

# Step 7: Set up the Model

### Theory

  For this step, we will need to set up the slider Model class to hold the information we need for the size of the selected primitive. We will later use this information to connect it to the Manipulator. 

## Step 7.1: Import Omniverse Command Library

   First, let's start by importing the Omniverse Command Library to `sliderModel.py`

   ```python
from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd
# NEW IMPORT
import omni.kit.commands
# END NEW 
   ```

## Step 7.2: ValueItem Class

Next, we will add a new Manipulator Item class, which we will name `ValueItem`, like so:

```python
...
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

    # NEW MANIPULATOR ITEM
    class ValueItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value"""

        def __init__(self, value=0):
            super().__init__()
            self.value = [value]
    # END NEW 
   ...
```
We will use this new class to create the variables for the min and max of the scale:

```python
...
    def __init__(self) -> None:
        super().__init__()

        # NEW
        self.scale = SliderModel.ValueItem()
        self.min = SliderModel.ValueItem()
        self.max = SliderModel.ValueItem(1)
        # END NEW

        self.position = SliderModel.PositionItem()
   ...
```

## Step 7.3: Set Scale to Stage

With the new variables for the scale, let's define them in `on_stage_event` like so:

```python
...
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
            
            # NEW
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(prim)

            scale = old_scale[0]
            _min = scale * 0.1
            _max = scale * 2.0
            self.set_floats(self.min, [_min])
            self.set_floats(self.max, [_max])
            self.set_floats(self.scale, [scale])
            # END NEW
      ...
```

## Step 7.4: Define Identifiers

Just as we defined the identifier for position, we must do the same for value, min, and max. We will add these to `get_item`:

```python
...
    def get_item(self, identifier):
        if identifier == "position":
            return self.position
        # NEW 
        if identifier == "value":
            return self.scale
        if identifier == "min":
            return self.min
        if identifier == "max":
            return self.max
        # END NEW 
   ...
```

## Step 7.5: Set Floats

Previously, we made a call to `set_floats`, now let's create this pass. In this function, we will set the scale when setting the value, set directly to the item, and update the manipulator:

```python
    def set_floats(self, item, value):
        if not self.current_path:
            return

        if not value or not item or item.value == value:
            return

        if item == self.scale:
            # Set the scale when setting the value.
            value[0] = min(max(value[0], self.min.value[0]), self.max.value[0])
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(
                self._stage.GetPrimAtPath(self.current_path)
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
```

<details>
<summary>Click here for the full Model script  </summary>

```python
from omni.ui import scene as sc
from pxr import Tf
from pxr import Usd
from pxr import UsdGeom
import omni.usd
# NEW IMPORT
import omni.kit.commands
# END NEW 

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

    # NEW MANIPULATOR ITEM
    class ValueItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value"""

        def __init__(self, value=0):
            super().__init__()
            self.value = [value]
    # END NEW 

    def __init__(self) -> None:
        super().__init__()

        # NEW
        self.scale = SliderModel.ValueItem()
        self.min = SliderModel.ValueItem()
        self.max = SliderModel.ValueItem(1)
        # END NEW

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
            
            # NEW
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(prim)

            scale = old_scale[0]
            _min = scale * 0.1
            _max = scale * 2.0
            self.set_floats(self.min, [_min])
            self.set_floats(self.max, [_max])
            self.set_floats(self.scale, [scale])
            # END NEW
            
            if not prim.IsA(UsdGeom.Imageable):
                return

            self.current_path = prim_paths[0]
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
        # NEW 
        if identifier == "value":
            return self.scale
        if identifier == "min":
            return self.min
        if identifier == "max":
            return self.max
        # END NEW 

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value
        return []

    # NEW
    def set_floats(self, item, value):
        if not self.current_path:
            return

        if not value or not item or item.value == value:
            return

        if item == self.scale:
            # Set the scale when setting the value.
            value[0] = min(max(value[0], self.min.value[0]), self.max.value[0])
            (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(
                self._stage.GetPrimAtPath(self.current_path)
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

      # END NEW

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
```

</details>

<br>
<br>

# Step 8: Add Gestures

### Theory

For our final step, we will be updating `sliderManipulator.py` to add the gestures needed to connect what we programmed in the Model. This will includechecking that the gesture is not prevented during drag, calling the gesture, restructure the geometry properties, and update the Line and Circle.

## Step 8.1: SliderDragGesturePayload Class

Let's begin by creating a new class that the user will access to get the current value of the slider, like so:

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):
  
    # NEW
    class SliderDragGesturePayload(sc.AbstractGesture.GesturePayload):
        """
        Public payload. The user will access it to get the current value of
        the slider.
        """

        def __init__(self, base):
            super().__init__(base.item_closest_point, base.ray_closest_point, base.ray_distance)
            self.slider_value = 0
```

## Step 8.2 SliderChangedGesture Class

Next, we will create another new class that the user will reimplement to process the manipulator's callbacks:

```python
...
class SliderManipulator(sc.Manipulator):
  
    
    class SliderDragGesturePayload(sc.AbstractGesture.GesturePayload):
        """
        Public payload. The user will access it to get the current value of
        the slider.
        """

        def __init__(self, base):
            super().__init__(base.item_closest_point, base.ray_closest_point, base.ray_distance)
            self.slider_value = 0

# NEW
    class SliderChangedGesture(sc.ManipulatorGesture):
        """
        Public Gesture. The user will reimplement it to process the
        manipulator's callbacks.
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

```

Inside of the `SliderChangedGesture` class, let's define a process function for our methods:

```python
...
        def process(self):
            # Redirection to methods
            if self.state == sc.GestureState.BEGAN:
                self.on_began()
            elif self.state == sc.GestureState.CHANGED:
                self.on_changed()
            elif self.state == sc.GestureState.ENDED:
                self.on_ended()

```

Now, we need to pass through a few of the Public API functions:

```python
        # Public API:
        def on_began(self):
            pass

        def on_changed(self):
            pass

        def on_ended(self):
            pass
```

## Step 8.3 _ArcGesturePriorities Class

We will be adding an `_ArcGesture` class in the next step that needs the manager `_ArcGesturePriorities` to make it the priority gesture, this will also make sure that the gesture is not prevented in the middle of drag:

```python
    class _ArcGesturePrioritize(sc.GestureManager):
        """
        Manager makes _ArcGesture the priority gesture
        """

        def can_be_prevented(self, gesture):
            # Never prevent in the middle of drag
            return gesture.state != sc.GestureState.CHANGED

        def should_prevent(self, gesture, preventer):
            if isinstance(preventer, SliderManipulator._ArcGesture):
                if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
                    return True
```

## Step 8.4: _ArcGesture Class

Now, let's create the class `_ArcGesture` where we will set the new slider value and redirect to `SliderChangedGesture`.

```python
    class _ArcGesture(sc.DragGesture):
        """
        Internal gesture that sets the new slider value and redirects to
        public SliderChangedGesture.
        """

        def __init__(self, manipulator):
            super().__init__(manager=SliderManipulator._ArcGesturePrioritize())
            self._manipulator = manipulator

        def __repr__(self):
            return f"<_ArcGesture at {hex(id(self))}>"

        def process(self):
            if self.state in [sc.GestureState.BEGAN, sc.GestureState.CHANGED, sc.GestureState.ENDED]:
                # Form new gesture_payload object
                new_gesture_payload = SliderManipulator.SliderDragGesturePayload(self.gesture_payload)
                # Save the new slider position in the gesture_payload object
                object_ray_point = self._manipulator.transform_space(
                    sc.Space.WORLD, sc.Space.OBJECT, self.gesture_payload.ray_closest_point
                )
                center = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("position"))
                slider_value = (object_ray_point[0] - center[0]) / self._manipulator.width + 0.5
                _min = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("min"))[0]
                _max = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("max"))[0]
                new_gesture_payload.slider_value = _min + slider_value * (_max - _min)
                # Call the public gesture
                self._manipulator._process_gesture(
                    SliderManipulator.SliderChangedGesture, self.state, new_gesture_payload
                )
            # Base process of the gesture
            super().process()
```

## Step 8.5: Restructure Geometry Parameters

For this step, we will be restructuring the Geometry properties:

```python
        # Geometry properties
        self._width = 100
        self._thickness = 5
        self._radius = 5
        self._radius_hovered = 7

        def set_radius(circle, radius):
            circle.radius = radius

        # We don't recreate the gesture to make sure it's active when the
        # underlying object is recreated
        self._arc_gesture = self._ArcGesture(self)
```

## Step 8.6: Add Hover Gestures

If you noticed in our new geometry properties, we referenced a hover gesture. Let's create this gesture now:

```python
        # Compatibility with old versions of ui.scene
        if hasattr(sc, "HoverGesture"):
            self._hover_gesture = sc.HoverGesture(
                on_began_fn=lambda sender: set_radius(sender, self._radius_hovered),
                on_ended_fn=lambda sender: set_radius(sender, self._radius),
            )
        else:
            self._hover_gesture = None
```

## Step 8.7: UI Getters and Setters

We need to add a few Python decoraters for the UI, such as @property and @width-setter and @height-setter:

```python
    def destroy(self):
        pass

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        # Regenerate the mesh
        self.invalidate()

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        # Regenerate the mesh
        self.invalidate()
```

## Step 8.8: Update on_build

For our final step, we will update the `on_build` function to updatethe min and max values of the model, update the line and circle,  and update the label.

Let's start with updating the min and max values like so: 

```python
    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        # NEW
        _min = self.model.get_as_floats(self.model.get_item("min"))[0]
        _max = self.model.get_as_floats(self.model.get_item("max"))[0]
        value = float(self.model.get_as_floats(self.model.get_item("value"))[0])
        value_normalized = (value - _min) / (_max - _min)
        value_normalized = max(min(value_normalized, 1.0), 0.0)
        # END NEW
```

Now, we will add a new line so that we have a Left and Right line:

```python
        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * value_normalized - self._radius # REPLACED THE 1 WITH value_normalized
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

            # NEW: Basically the same as left line but flipped
            # Right line
            line_from = -self.width * 0.5 + self.width * value_normalized + self._radius
            line_to = self.width * 0.5
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)
            # END NEW
```

To update the circle, we will add a gesture so when hovered, the circle will increase in size:

```python
            # Circle
            circle_position = -self.width * 0.5 + self.width * value_normalized
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(circle_position, 0, 0)):
                radius = self._radius
                # NEW: Added Gesture when hovering over the circle it will increase in size
                gestures = [self._arc_gesture]
                if self._hover_gesture:
                    gestures.append(self._hover_gesture)

                    if self._hover_gesture.state == sc.GestureState.CHANGED:
                        radius = self._radius_hovered
                # END NEW
                sc.Arc(radius, axis=2, color=cl.gray, gestures=gestures)
```

Last of all, let's update the label to add more space between the slider and the label:

```python
                # Label
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    # NEW: Added more space between the slider and the label
                    # Move it to the top
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, self._radius_hovered, 0)):
                    # END NEW
                        with sc.Transform(scale_to=sc.Space.SCREEN):
                            # Move it 5 points more to the top in the screen space
                            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                                sc.Label(f"{value:.1f}", alignment=ui.Alignment.CENTER_BOTTOM)
```

<details>
<summary>Click here for the full Manipulator script</summary>

```python
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):
  
    # NEW
    class SliderDragGesturePayload(sc.AbstractGesture.GesturePayload):
        """
        Public payload. The user will access it to get the current value of
        the slider.
        """

        def __init__(self, base):
            super().__init__(base.item_closest_point, base.ray_closest_point, base.ray_distance)
            self.slider_value = 0

    class SliderChangedGesture(sc.ManipulatorGesture):
        """
        Public Gesture. The user will reimplement it to process the
        manipulator's callbacks.
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def process(self):
            # Redirection to methods
            if self.state == sc.GestureState.BEGAN:
                self.on_began()
            elif self.state == sc.GestureState.CHANGED:
                self.on_changed()
            elif self.state == sc.GestureState.ENDED:
                self.on_ended()

        # Public API:
        def on_began(self):
            pass

        def on_changed(self):
            pass

        def on_ended(self):
            pass

    class _ArcGesturePrioritize(sc.GestureManager):
        """
        Manager makes _ArcGesture the priority gesture
        """

        def can_be_prevented(self, gesture):
            # Never prevent in the middle of drag
            return gesture.state != sc.GestureState.CHANGED

        def should_prevent(self, gesture, preventer):
            if isinstance(preventer, SliderManipulator._ArcGesture):
                if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
                    return True

    class _ArcGesture(sc.DragGesture):
        """
        Internal gesture that sets the new slider value and redirects to
        public SliderChangedGesture.
        """

        def __init__(self, manipulator):
            super().__init__(manager=SliderManipulator._ArcGesturePrioritize())
            self._manipulator = manipulator

        def __repr__(self):
            return f"<_ArcGesture at {hex(id(self))}>"

        def process(self):
            if self.state in [sc.GestureState.BEGAN, sc.GestureState.CHANGED, sc.GestureState.ENDED]:
                # Form new gesture_payload object
                new_gesture_payload = SliderManipulator.SliderDragGesturePayload(self.gesture_payload)
                # Save the new slider position in the gesture_payload object
                object_ray_point = self._manipulator.transform_space(
                    sc.Space.WORLD, sc.Space.OBJECT, self.gesture_payload.ray_closest_point
                )
                center = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("position"))
                slider_value = (object_ray_point[0] - center[0]) / self._manipulator.width + 0.5
                _min = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("min"))[0]
                _max = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("max"))[0]
                new_gesture_payload.slider_value = _min + slider_value * (_max - _min)
                # Call the public gesture
                self._manipulator._process_gesture(
                    SliderManipulator.SliderChangedGesture, self.state, new_gesture_payload
                )
            # Base process of the gesture
            super().process()
    
    # END NEW

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # NEW restructured parameters and added hover gestures
        
        # Geometry properties
        self._width = 100
        self._thickness = 5
        self._radius = 5
        self._radius_hovered = 7

        def set_radius(circle, radius):
            circle.radius = radius

        # We don't recreate the gesture to make sure it's active when the
        # underlying object is recreated
        self._arc_gesture = self._ArcGesture(self)

        # Compatibility with old versions of ui.scene
        if hasattr(sc, "HoverGesture"):
            self._hover_gesture = sc.HoverGesture(
                on_began_fn=lambda sender: set_radius(sender, self._radius_hovered),
                on_ended_fn=lambda sender: set_radius(sender, self._radius),
            )
        else:
            self._hover_gesture = None
          # END NEW

    # NEW
    def destroy(self):
        pass

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        # Regenerate the mesh
        self.invalidate()

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        # Regenerate the mesh
        self.invalidate()
    # END NEW

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        # NEW
        _min = self.model.get_as_floats(self.model.get_item("min"))[0]
        _max = self.model.get_as_floats(self.model.get_item("max"))[0]
        value = float(self.model.get_as_floats(self.model.get_item("value"))[0])
        value_normalized = (value - _min) / (_max - _min)
        value_normalized = max(min(value_normalized, 1.0), 0.0)
        # END NEW

        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * value_normalized - self._radius # REPLACED THE 1 WITH value_normalized
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

            # NEW: Basically the same as left line but flipped
            # Right line
            line_from = -self.width * 0.5 + self.width * value_normalized + self._radius
            line_to = self.width * 0.5
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)
            # END NEW

            # Circle
            circle_position = -self.width * 0.5 + self.width * value_normalized
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(circle_position, 0, 0)):
                radius = self._radius
                # NEW: Added Gesture when hovering over the circle it will increase in size
                gestures = [self._arc_gesture]
                if self._hover_gesture:
                    gestures.append(self._hover_gesture)

                    if self._hover_gesture.state == sc.GestureState.CHANGED:
                        radius = self._radius_hovered
                # END NEW
                sc.Arc(radius, axis=2, color=cl.gray, gestures=gestures)


                # Label
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    # NEW: Added more space between the slider and the label
                    # Move it to the top
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, self._radius_hovered, 0)):
                    # END NEW
                        with sc.Transform(scale_to=sc.Space.SCREEN):
                            # Move it 5 points more to the top in the screen space
                            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 5, 0)):
                                sc.Label(f"{value:.1f}", alignment=ui.Alignment.CENTER_BOTTOM)

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

</details>

<br>
<br>

# Congratulations!

You have completed the guide `How to make a Slider Manipulator` and now have a working scale slider!