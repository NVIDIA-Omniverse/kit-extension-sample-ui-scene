# How to make an extension to display Object Info

  The object info displays the primitives Path and type. By the end of this guide you will have created an extension that displays this info in the viewport for the selected primitive. This guide is suited for more established begineers (beginning engineers) to Omniverse Kit. We will be walking you through how to create the extension from the beginning but you may refer back to the [github repository](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/tree/main/exts/omni.example.ui_scene.object_info) at any time. 

# Learning Objectives
In this guide you will learn how to:
- Create an extension in Omniverse Code
- Import from Omniverse into your code
- Display object info in viewport
- Translate from World space to Local space

# Prereqs
  It is recommended that you have completed these tutorials before moving forward.

- TODO
- Eric's guide to installing omni, pushing to git [need link]
- [How to make an extension by spawning primitives](https://github.com/NVIDIA-Omniverse/kit-extension-sample-spawnprims/blob/main/exts/omni.example.spawnPrims/tutorial/Spawn_PrimsTutorial.md)

# Table of Contents

- [Step 1: Create an Extension](#step-1-create-an-extension)
  - [Step 1.1: Create the extension template](#step-11-create-the-extension-template)
  - [Step 1.2: Naming your extension](#step-12-naming-your-extension)
- [Step 2: Beginning Your Code](#step-2-beginning-your-code)
   - [Step 2.1: Importing the Viewport](#step-21-importing-the-viewport)
   - [Step 2.2: Create the Object Info Model Script](#step-22-create-the-object-info-model-script)
   - [Step 2.3: Object Model Script Code](#step-23-object-model-script-code)
   - [Step 2.4: Import to extension.py](#step-24-import-to-extensionpy)
- [Step 3: Set the Stage](#step-3-set-the-stage)
   - [Step 3.1: Create a Stage Event](#step-31-create-a-stage-event)
   - [Step 3.2: Object Path Name in Scene](#step-32-object-path-name-in-scene)
   - [Step 3.3: The Manipulator Class](#step-33-the-manipulator-class)
   - [Step 3.4: Displaying in the Viewport](#step-34-displaying-in-the-viewport)
   - [Step 3.5: Cleaning up extension.py](#step-35-cleaning-up-extensionpy)
- [Step 4: Displaying Object Info in Local Space](#step-4-displaying-object-info-in-local-space)
   - [Step 4.1: Updating Object Info Model](#step-41-updating-object-info-model)
   - [Step 4.2: Updating Object Info Manipulator](#step-42-updating-object-info-manipulator)
   - [Step 4.3: Moving the Text with the Primitive](#step-43-moving-the-text-with-the-primitive)
- [Congratulations!](#congratulations-1)

# Step 1: Create an Extension


> 📝 **Note:** For a more detailed introduction to creating an extension, please refer back to `Jen's tutorial` [link to tutorial]

For this guide, we will briefly go over how to create an extension. If you have not completed `Jen's tutorial` it is recommended you pause here and complete that before moving forward.

## Step 1.1: Create the extension template
  In Omniverse Code navigate to the `Extensions` tab and create a new extension by clicking the ➕ icon in the upper left corner and select `New Extension Template Project`. This may be familar from the Tutorial on how to Spawn Primatives.  

  ![extension tab](./images/ext_tab.png "Extension Tab in Omniverse Code")
  
  <icon>                       |  <new template>
:-------------------------:|:-------------------------:
![icon](./Images/icon_create.png "Plus Icon")  |  ![new template](./Images/new_template.png "New Extension Template")

<br>

A new extension template window and Visual Studio Code will open after you have selected the folder location, folder name, and extension ID. 

## Step 1.2: Naming your extension
  Before we begin any code, let's navigate into `VS Code` and change how the extension is viewed in the Extension Manager. It is important to give your extension a title and detailed summarized description for the end user to understand what the extension will accomplish or display. 
 <br><br>

Inside of the `config` folder, locate the `extension.toml` file. The script will look something like this:

![extension.toml](./Images/step1.2_naming_ext_tomlFile.PNG "Extension.toml file Snapshot")
<br><br>

Inside of this file, there is a title and description for how the extension will look in the Extension Manager. Change the title and description for the object info extension. Here is an example of how we changed it for this guide and how it looks in `Omniverse Code Extension Manager`:

![title and description](./Images/step1.2_naming_ext_uiTitle_uiDescrip.PNG "New title and description")
<br>
![new ui](./Images/step1.2_naming_ext_ui_update.PNG "New UI display in Code")
<br><br>

# Step 2: Beginning Your Code
> 📝**Note:** We will be creating new scripts in this section and bouncing between them often. Please note which script the code is written in. 
<br>

To begin coding, we will navigate to the `extension.py` script in Visual Studio Code. It will look something like this:

![extension.py script](./Images/step2.extension_script.PNG "Extension.py script snapshot")
<br>

## Step 2.1: Importing the Viewport

### Theory 
  We first need to import the viewport into the `extension.py` script. We can then begin adding to the `class` so that the active viewport is selected and the action is properly displayed in the console. 

  At the top of `extension.py` we have two imports there by default: 
```python
import omni.ext
import omni.ui as ui
```

  We will import the viewport underneath these, such as:
  ```python
import omni.ext
import omni.ui as ui

# NEW: Import function to get the active viewport
from omni.kit.viewport.utility import get_active_viewport_window
# END NEW
  ```

Now that the we have imported the viewport from Omniverse, we will begin adding to the class.

Inside of the `on_startup` function we will set the viewport variable for the active viewport like so:

```python
class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        print("[omni.objInfo.tutorial] MyExtension startup")
        
        # NEW: Get the active Viewport (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()
        # END NEW
```

Inside of the `on_click` function we will print that the active viewport is selected. Change the print("Text") as follows:

```python
                def on_click():
                    # NEW: Print to see that we did grab the active viewport
                    print(viewport_window)
                    # END NEW
```

At this point, when you navigate back to `Omniverse Code` and click the "Click Me" button inside of the Extension Template Window, you will see `Viewport` appear at the bottom of Code's screen.

![](./Images/viewport%20displayed%20on%20click.PNG "Viewport on Click Me")



  <br>

  ## Step 2.2: Create the Object Info Model Script
 ### Theory
   In this new script, we will be creating the necessary information for the object information to be called, such as the selected primitive and tracking when the selection changes. We will also be creating a stage to be set later on. Before we move on to creating the code, we first need to create a new file. In the same file location as `extension.py` create a new file and name it `objectInfoModel.py`.

  ![](./Images/objectInfoModel%20created.gif "objectInfoModel.py created")


  <br>

  ## Step 2.3: Object Model Script Code
  > 📝**Note:** We are working in the `object_info_model.py` script for this section. 
<br>
The objective of this step is to import and set the basic information that the `Manipulator` and `Viewport` will need to display on the selected primitive. 

As with the `extension.py` script, we need to import from Omniverse. We will start with the following at the top of our new script:

```python
from omni.ui import scene as sc
import omni.usd
```

Next, we will create our class and begin setting variables.

Below the imports create the `ObjInfoModel` class, as so:
```python
from omni.ui import scene as sc
import omni.usd

class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
```

Inside of this class we need an init method to initialize the object and events. We will set this function and set the variable for the current selected primitive, as so:

```python
from omni.ui import scene as sc
import omni.usd

class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None

        self.position = [0, 0, 0]
```

Finally, we save the USD Context variable ([see here for more information on USD in Omniverse](https://docs.omniverse.nvidia.com/plat_omniverse/plat_omniverse/usd.html)), track when selection changes, and create a stage event to be used later on:

```python
from omni.ui import scene as sc
import omni.usd

class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None

        self.position = [0, 0, 0]

        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        print("A stage event has occurred")
        
    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()
```
>📝**Note:** It is important to include the `destroy` method in the model script. This will free the memory as well as clear the screen to prevent any accumlation of events. 

<br><br>

## Step 2.4: Import to extension.py
> 📝**Note:** We are working in `extension.py` for this section. 

<br>

### Theory
Now that we have created `objectInfoModel.py`, we need to do a few things in `extension.py` to reflect the object model, such as import from the model class, create a reference and the object, then destroy the model when the extension is shutdown. 

To begin, we will import into `extension.py` from `objectInfoModel.py` as so:
```python
import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

# NEW: import model class
from .objectInfoModel import ObjInfoModel
# END NEW

...
```

Now we will reference the object model in the init method:
```python
class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    # NEW: Reference to the objModel when created so we can destroy it later
    def __init__(self) -> None:
        super().__init__()
        self.obj_model = None
    # END NEW

    ...
```

This allows us to create the object in `on_startup` and destroy it later on in `on_shutdown`:
```python
 def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        print("[omni.objInfo.tutorial] MyExtension startup")

        # Get the active Viewport (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()
        
        # NEW: create the object
        self.obj_model = ObjInfoModel()
        # END NEW
        
        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Some Label")

                def on_click():
                    # Print to see that we did grab the active viewport
                    print(viewport_window)

                ui.Button("Click Me", clicked_fn=lambda: on_click())

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        print("[omni.objInfo.tutorial] MyExtension shutdown")
        # NEW: Destroy the model when created
        self.obj_model.destroy()
        # END NEW
```
<details>
<summary>Click here for the updated <b>extension.py</b> script  </summary>

```python
import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

# NEW: import model class
from .objectInfoModel import ObjInfoModel
# END NEW

class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    # NEW: Reference to the objModel when created so we can destroy it later
    def __init__(self) -> None:
        super().__init__()
        self.obj_model = None
    # END NEW

     def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        print("[omni.objInfo.tutorial] MyExtension startup")

        # Get the active Viewport (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()
        
        # NEW: create the object
        self.obj_model = ObjInfoModel()
        # END NEW
        
        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Some Label")

                def on_click():
                    # Print to see that we did grab the active viewport
                    print(viewport_window)

                ui.Button("Click Me", clicked_fn=lambda: on_click())

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        print("[omni.objInfo.tutorial] MyExtension shutdown")
        # NEW: Destroy the model when created
        self.obj_model.destroy()
        # END NEW
```

</details>


<br>

# Step 3: Set the Stage
### Theory
At this point, there is nothing viewable in `Omniverse Code` as we have not created a stage for the viewport to reference an event happening. In this section we will be setting that stage by getting a reference to the selected object's information. By the end of step 3 you should be able to view the object info in the viewport.

## Step 3.1: Create a Stage Event
> 📝**Note:** We are working in `objectInfoModel.py` for this section.

At this point, we have have created the start of the Stage Event in `objectInfoModel.py` but there is nothing happening in the event. Let's replace what's in `on_stage_event` with the variable for the primitive path and where that path information is located:

```python
  def on_stage_event(self, event):
        """Called by stage_event_stream."""
        # NEW
        prim_path = self.usd_context.get_selection().get_selected_prim_paths()
        if not prim_path:
            return
        stage = self.usd_context.get_stage()
        prim = stage.GetPrimAtPath(prim_path[0])
        self.prim = prim
        self.current_path = prim_path[0]
        print("Primitive: " + str(prim))

        # END NEW

        ...
```

We can check that this is working by navigating back to `Omniverse Code` and create a primitive in the viewport. When the primitive is created, it's path should display at the bottom. 

![](./Images/path%20displayed.PNG "Object Path displayed when Object Selected")

## Step 3.2: Object Path Name in Scene
### Theory 
In this step we are inistilling another init method in a new class to represent the position. This position will be taken directly from USD when requested. We will be nesting the new `PositionItem` class inside of the `ObjInfoModel` class as so:
```python
class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    
    # NEW: needed for when we call item changed
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """
        def __init__(self) -> None:
            super().__init__()
            self.value = [0, 0, 0]
    # END NEW

    ...
```
We will also have to update the position from [0,0,0] to it's current path and hold position of the object created:

```python
    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None

        #NEW: Remove position and set to current path. 
        self.current_path = ""
        # END NEW

        # NEW: update to hold position obj created
        self.position = ObjInfoModel.PositionItem()
        # END NEW

        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )
        ...
```

After updating the position, we need to check the stage when the selection of an object is changed. We will do this with an "if" statement in `on_stage_event`, like so:

```python
    def on_stage_event(self, event):
        # NEW: if statement to only check when selection changed
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
        # END NEW
        
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()
            if not prim_path:
                return
            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])
            self.prim = prim
            self.current_path = prim_path[0]

            # NEW: Update on item change
            # Position is changed because new selected object has a different position
            self._item_changed(self.position)
            # END NEW

            ...
```

Finally, we will create a new function underneath `on_stage_event` to get identifiers from the model:

```python
    # NEW: function to get identifiers from the model
    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
    # END NEW

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()
```

<details>
<summary>Click here for the updated <b>objectInfoModel.py</b> script  </summary>

```python
from omni.ui import scene as sc
import omni.usd

class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    
    # NEW: needed for when we call item changed
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """
        def __init__(self) -> None:
            super().__init__()
            self.value = [0, 0, 0]
    # END NEW


    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None
        #NEW: Remove position and set to current path. 
        self.current_path = ""
        # END NEW

        # NEW: update to hold position obj created
        self.position = ObjInfoModel.PositionItem()
        # END NEW


        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        # NEW: if statement to only check when selection changed
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
        # END NEW
        
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()
            if not prim_path:
                return
            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])
            self.prim = prim
            self.current_path = prim_path[0]

            # NEW: Update on item change
            # Position is changed because new selected object has a different position
            self._item_changed(self.position)
            # END NEW

    # NEW: function to get identifiers from the model
    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
    # END NEW

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()
```

</details>

<br>

## Step 3.3: The Manipulator Class
### Theory
In this step we will be creating a new script that will reference the manipulator class for the object info that will be displayed in the viewport in another step ([see here for more information on the Manipulator Class in Omniverse](https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.ui.scene/docs/Manipulator.html)).<br>
Similar to when `objectInfoModel.py` was created, we will be creating a new script in the same folder. We will name this file `objectInfoManipulator.py`.

![](./Images/objectinfomanipulator_created.gif)

<br>

The objective of this script will be to grab the reference of the object model's details such as name and path to be displayed in the viewport though the `on_build` function. This is important as it connects the nested data in `objectInfoModel.py`. Let's begin by importing from omniverse:

```python
from omni.ui import scene as sc
import omni.ui as ui
```
From here we will create a the `ObjInfoManipulator` class as so:

```python
...

class ObjInfoManipulator(sc.Manipulator):
    """Manipulator that displays the object path and material assignment
    with a leader line to the top of the object's bounding box.
    """
```

This class will hold the `on_build` function where we will check if there is a selection and create a label for the path:

```python
...

    def on_build(self):
        """Called when the model is changed and rebuilds the whole manipulator"""
        
        if not self.model:
            return
        
        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        position = [0, 0, 0]
        
        sc.Label(f"Path: {self.model.get_item('name')}")
```

Before we move on from `objectInfoManipulator.py` we must call the invalidate method to purge old memory when the model is updated. We will call this at the end of the script:

```python
...

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

<details>
<summary>Click here for the full <b>objectInfoManipulator.py</b> script  </summary>

```python
from omni.ui import scene as sc
import omni.ui as ui


class ObjInfoManipulator(sc.Manipulator):
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

        position = [0, 0, 0]
        
        sc.Label(f"Path: {self.model.get_item('name')}")


    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()
```

</details>

<br>

## Step 3.4: Displaying in the viewport
> 📝**Note:** We are working in `viewportScene.py` for this section.

### Theory
 In this step, we will create a new script that will reference the gathered information from our other scripts and call them to display in the active viewport. 

We will add this script to the same folder and name it `viewportScene.py`.

![](./Images/viewportScene%20created.gif)

This script will import not only from Omniverse but also from our Model and Manipulator, so we will begin there:

```python
from omni.ui import scene as sc
import omni.ui as ui

from .objectInfoManipulator import ObjInfoManipulator
from .objectInfoModel import ObjInfoModel
```

Now that we have imported from our other files, we can create our `ViewportSceneInfo` class:

```python
class ViewportSceneInfo():
```
This is where we will include our init method so that we can place the Object Info Manipulator into the viewport.

```python
...
class ViewportSceneInfo():
    """The Object Info Manipulator, placed into a Viewport"""
    def __init__(self, viewport_window, ext_id) -> None:
        self.scene_view = None
        self.viewport_window = viewport_window
```

To display the information we will create a unique frame for our SceneView and set the default SceneView.

```python
...
        # Create a unique frame for our SceneView
        with self.viewport_window.get_frame(ext_id):
            # Create a default SceneView (it has a default camera-model)
            self.scene_view = sc.SceneView()
```
Now we can add the manipulator into the SceneView's scene and register our SceneView with the Viewport.

```python
...
            # Add the manipulator into the SceneView's scene
            with self.scene_view.scene:
                ObjInfoManipulator(model=ObjInfoModel())
            # Register the SceneView with the Viewport to get projection and view updates
            self.viewport_window.viewport_api.add_scene_view(self.scene_view)
```

Before closing out on `viewportScene.py` we must not forget our `destroy()` function to clear the scene and un-register our unique SceneView from the Viewport. 

```python
...
    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.scene_view:
            # Empty the SceneView of any elements it may have
            self.scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self.viewport_window:
                self.viewport_window.viewport_api.remove_scene_view(self.scene_view)
        # Remove our references to these objects
        self.viewport_window = None
        self.scene_view = None
```

<details>
<summary>Click here for the full <b>viewportScene.py</b> script  </summary>

```python
from omni.ui import scene as sc
import omni.ui as ui

from .objectInfoManipulator import ObjInfoManipulator
from .objectInfoModel import ObjInfoModel

class ViewportSceneInfo():
    """The Object Info Manipulator, placed into a Viewport"""
    def __init__(self, viewport_window, ext_id) -> None:
        self.scene_view = None
        self.viewport_window = viewport_window

        # Create a unique frame for our SceneView
        with self.viewport_window.get_frame(ext_id):
            # Create a default SceneView (it has a default camera-model)
            self.scene_view = sc.SceneView()

            # Add the manipulator into the SceneView's scene
            with self.scene_view.scene:
                ObjInfoManipulator(model=ObjInfoModel())
            # Register the SceneView with the Viewport to get projection and view updates
            self.viewport_window.viewport_api.add_scene_view(self.scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.scene_view:
            # Empty the SceneView of any elements it may have
            self.scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self.viewport_window:
                self.viewport_window.viewport_api.remove_scene_view(self.scene_view)
        # Remove our references to these objects
        self.viewport_window = None
        self.scene_view = None
```

</details>

<br>


## Step 3.5: Cleaning up extension.py
> 📝**Note:** We are working in `extension.py` for this section.

### Theory
Now that we have established out Viewport, we need to clean up `extension.py` to reflect these changes. We will be removing some of the references we made previously and ensuring that the viewport is flushed out on shutdown.

Let's begin by importing `viewportScene.py` and its' class:
```python
import omni.ext
from omni.kit.viewport.utility import get_active_viewport_window
# NEW:
from .viewportScene import ViewportSceneInfo
# END NEW
```
> 📝**Note:** We removed the import from objectInfoModel as it no longer will be used.
```python
# REMOVE
from .objectInfoModel import ObjInfoModel
```

As we removed the import from `objectInfoModel.py` we will also remove its' reference in the init method and replace it with the viewportScene:

```python
# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self) -> None:
        super().__init__()
        # NEW: removed reference to objmodelinfo and replaced with viewportscene
        self.viewport_scene = None
        # END NEW
```
Next, we will remove the start up code where we reference to create the object and the code following it that creates the extension window and "Cick Me" button

```python
...
    def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
       # # # !REMOVE! # # #
        print("[omni.objInfo.tutorial] MyExtension startup")

        viewport_window = get_active_viewport_window()
        
        self.obj_model = ObjInfoModel()
       
        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Some Label")

                def on_click():
                    print(viewport_window)

                ui.Button("Click Me", clicked_fn=lambda: on_click())
         # # # END # # #
...


        # # # !REPLACE WITH! # # #
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id)
        # # # END # # #

```

<details>
<summary>Click to view final <b>on_startup</b> code</summary>

```python
    def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id)
```
</details>

<br>


Finally, we will update the `on_shutdown` function to clean up the viewport:

```python
...
    def on_shutdown(self):
        """Called when the extension is shutting down."""
        # NEW: updated to destroy viewportscene
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None
        # END NEW
```


<details>
<summary>Click to view the updated <b>extension.py</b> </summary>

```python
import omni.ext
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

from .viewportScene import ViewportSceneInfo

class MyExtension(omni.ext.IExt):
    """Creates an extension which will display object info in 3D
    over any object in a UI Scene.
    """
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self) -> None:
        super().__init__()
        # NEW: removed reference to objmodelinfo and replaced with viewportscene
        self.viewport_scene = None
        # END NEW

     def on_startup(self, ext_id):
        """Called when the extension is starting up.

        Args:
            ext_id: Extension ID provided by Kit.
        """
        # # # !REPLACE WITH! # # #
        viewport_window = get_active_viewport_window()

        self.viewport_scene = ViewportSceneInfo(viewport_window, ext_id)
        # # # END # # #


    def on_shutdown(self):
        """Called when the extension is shutting down."""
        # NEW: updated to destroy viewportscene
        if self.viewport_scene:
            self.viewport_scene.destroy()
            self.viewport_scene = None
        # END NEW

```
</details>

<br>


## Congratulations! 
You should be able to create a primitive in the viewport and view the Object Info at the world position [0,0,0].

![](./Images/step3_end_viewport.PNG)

>💡 Tip: If you are logging any errors in the Console in `Omniverse Code` after updating `extention.py` try refreshing the application.

<br>

# Step 4: Displaying Object Info in Local Space
### Theory
  At this stage, the Object Info is displaying in the viewport but it is displayed in World Space. This means that regardless of where your object is located in the World, the info will always be displayed at [0,0,0]. In the next few steps we will convert this into Local Space. By the end of step 4 the Object Info should follow the object. 

  ## Step 4.1: Updating Object Info Model
  > 📝**Note:** We are working in `objectInfoModel.py` for this section.

  In this step and the following steps, we will be doing a little bit of math. Before we jump into that though, let's import what we need to make this work into `objectInfoModel.py`. We will be importing primarily what we need from USD and we will place these imports at the top of the file, as so:

  ```python
# NEW IMPORTS
from pxr import Usd
from pxr import UsdGeom
# END NEW

from omni.ui import scene as sc
import omni.usd
  ```
Next, we need to add a new identifier for the position in the `get_item` function:

```python
...
    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
        # NEW: new identifier
        elif identifier == "position":
            return self.position
        # END NEW
```

After adding to the `get_item` function, we will create a new function to get the position of the primitive. We will call this function `get_as_floats` and inside of this function we will request the position and get the value from the item:

```python
...
    # NEW: new function to get position of prim
    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value

        return []
    # END NEW
```

Although we have created this new function to get the position, we have yet to define the position. The position will be defined in a new function based on the bounding box we will create for the primitive. This new function will be named `get_position` and in this function we will begin by getting the stage:

```python
...
    # NEW: new function that defines the position based on the bounding box of the primitive
    def get_position(self):
        stage = self.usd_context.get_stage()
        if not stage or self.current_path == "":
            return [0, 0, 0]
```

Now, we will get the position directly from USD using the bounding box. This will be placed inside of the `get_position` function:

```python
...
        # Get position directly from USD
        prim = stage.GetPrimAtPath(self.current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin() #bbox stands for bounding box
        bboxMax = range.GetMax()
```

Finally, we need to find the top center of the bounding box. We will also add a small offset upward so that the information is not overlapping our primitive. This will also be added to the `get_position` function:

```python
...
        # Find the top center of the bounding box and add a small offset upward.
        x_Pos = (bboxMin[0] + bboxMax[0]) * 0.5
        y_Pos = bboxMax[1] + 5 
        z_Pos = (bboxMin[2] + bboxMax[2]) * 0.5
        position = [x_Pos, y_Pos, z_Pos]
        return position
    # END NEW 
```

<details>
<summary>Click here for the final <b>objectInfoModel.py</b> code for this step.</summary>

```python
# NEW Imports
from pxr import Usd
from pxr import UsdGeom
# END NEW

from omni.ui import scene as sc
import omni.usd


class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """
        def __init__(self) -> None:
            super().__init__()
            self.value = [0, 0, 0]


    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None
        self.current_path = ""

      
        self.position = ObjInfoModel.PositionItem()

        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()
            if not prim_path:
                return
            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])
            self.prim = prim
            self.current_path = prim_path[0]

            # Position is changed because new selected object has a different position
            self._item_changed(self.position)

    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
        # NEW: new identifier
        elif identifier == "position":
            return self.position
        # END NEW

    # NEW: new function to get position of prim
    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self.get_position()
        if item:
            # Get the value directly from the item
            return item.value

        return []
    # END NEW

    # NEW: new function that defines the position based on the bounding box of the primitive
    def get_position(self):
        stage = self.usd_context.get_stage()
        if not stage or self.current_path == "":
            return [0, 0, 0]
        
        # Get position directly from USD
        prim = stage.GetPrimAtPath(self.current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin() #bbox stands for bounding box
        bboxMax = range.GetMax()

        # Find the top center of the bounding box and add a small offset upward.
        x_Pos = (bboxMin[0] + bboxMax[0]) * 0.5
        y_Pos = bboxMax[1] + 5 
        z_Pos = (bboxMin[2] + bboxMax[2]) * 0.5
        position = [x_Pos, y_Pos, z_Pos]
        return position
    # END NEW 

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()
```

</details>

<br>

## Step 4.2: Updating Object Info Manipulator
> 📝**Note:** We are working in `objectInfoManipulator.py` for this section.
### Theory
  In this step, we need to update the position value and the added transform functions to position the label, or Object Info, at the object's origin and then offset it in the up-direction. We will also want to make sure that it is scaled properly in the viewport. <br><br>
  Fortunately, this does not require a big alteration to our existing code. We merely need to add onto the `on_build` function in the `objectInfoManipulator.py` script:

  ```python
  ...
    def on_build(self):
        """Called when the model is changed and rebuilds the whole manipulator"""
        
        if not self.model:
            return
        
        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        # NEW: update to position value and added transform functions to position the Label at the object's origin and +5 in the up direction
        # we also want to make sure it is scaled properly
        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            with sc.Transform(scale_to=sc.Space.SCREEN):
        # END NEW
                sc.Label(f"Path: {self.model.get_item('name')}")
        sc.Label(f"Path: {self.model.get_item('name')}")

  ...
  ```
## Step 4.3: Moving the Text with the Primitive
### Theory
In the viewport of `Omniverse Code`, our text does not follow our object despite positioning the label at the top center of the bounding box of our object. The text also remains in the viewport even when the object is no longer selected. In this final step we will be guiding you to cleaning up these issues. 
> 📝**Note:** We are back in `objectInfoModel.py` for this section

We have one more import to place into `objectInfoModel.py` at the top of the file, as so:

```python
# NEW 
from pxr import Tf
# END NEW 
from pxr import Usd
from pxr import UsdGeom

from omni.ui import scene as sc
import omni.usd
```
As well as adding a new variable to grab the stage listener under the second init method:

```python
...
    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None
        self.current_path = ""

        # NEW: new variable
        self.stage_listener = None
        # END NEW
        self.position = ObjInfoModel.PositionItem()
...
```
Now, we will be adding to the `on_stage_event` where we will be checking if the primitive path exists and turn off the manipulator if it does not:

```python
...
    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()

            # NEW: if prim path doesn't exist we want to make sure nothing shows up because that means we do not have a prim selected
            if not prim_path:
                # This turns off the manipulator when everything is deselected
                self.current_path = ""
                self._item_changed(self.position)
                return
            # END NEW
...
```

We also need to check if the selected item is a primitive. If it isn't then we will remove the stage listener:

```python
...
            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])

            # NEW: if the selected item is not a prim we need to revoke the stagelistener since we don't need to update anything
            if not prim.IsA(UsdGeom.Imageable):
                self.prim = None
                # Revoke the Tf.Notice listener, we don't need to update anything
                if self.stage_listener:
                    self.stage_listener.Revoke()
                    self.stage_listener = None
                return  
            # END NEW
...
```
Next, we will register a notice with the stage listener when objects in the scene have changed:

```python
...
            # NEW: Register a notice when objects in the scene have changed
            if not self.stage_listener:
                self.stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.notice_changed, stage)
            # END NEW
...
```

The final step in this will be to create a new function that will be called when those objects in the scene have changed and if there are multiple objects in the scene then it will loop through all objects until we find the one that is selected. We will place this new function after `get_position` and name it `notice_changed`. After this, the path should follow the selected object as well as not stay in the viewport when object is deselected:

```python
...
    # NEW: function that will get called when objects change in the scene. We only care about our selected object so we loop through all notices that get passed along until we find ours
    def notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        """Called by Tf.Notice.  Used when the current selected object changes in some way."""
        for p in notice.GetChangedInfoOnlyPaths():
            if self.current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)
    # END NEW
...
```
<details>
<summary>Click here for the final <b>objectInfoModel.py</b> code </summary>

```python
# NEW 
from pxr import Tf
# END NEW 
from pxr import Usd
from pxr import UsdGeom

from omni.ui import scene as sc
import omni.usd


class ObjInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """
    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because we take the position directly from USD when requesting.
        """
        def __init__(self) -> None:
            super().__init__()
            self.value = [0, 0, 0]


    def __init__(self) -> None:
        super().__init__()

        # Current selected prim
        self.prim = None
        self.current_path = ""

        # NEW: new variable
        self.stage_listener = None
        # END NEW
        self.position = ObjInfoModel.PositionItem()

        # Save the UsdContext name (we currently only work with a single Context)
        self.usd_context = omni.usd.get_context()

        # Track selection changes
        self.events = self.usd_context.get_stage_event_stream()
        self.stage_event_delegate = self.events.create_subscription_to_pop(
            self.on_stage_event, name="Object Info Selection Update"
        )

    def on_stage_event(self, event):
        """Called by stage_event_stream.  We only care about selection changes."""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            prim_path = self.usd_context.get_selection().get_selected_prim_paths()

            # NEW: if prim path doesn't exist we want to make sure nothing shows up because that means we do not have a prim selected
            if not prim_path:
                # This turns off the manipulator when everything is deselected
                self.current_path = ""
                self._item_changed(self.position)
                return
            # END NEW

            stage = self.usd_context.get_stage()
            prim = stage.GetPrimAtPath(prim_path[0])

            # NEW: if the selected item is not a prim we need to revoke the stagelistener since we don't need to update anything
            if not prim.IsA(UsdGeom.Imageable):
                self.prim = None
                # Revoke the Tf.Notice listener, we don't need to update anything
                if self.stage_listener:
                    self.stage_listener.Revoke()
                    self.stage_listener = None
                return 
            # END NEW

            # NEW: Register a notice when objects in the scene have changed
            if not self.stage_listener:
                self.stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.notice_changed, stage)
            # END NEW

            self.prim = prim
            self.current_path = prim_path[0]

            # Position is changed because new selected object has a different position
            self._item_changed(self.position)

    def get_item(self, identifier):
        if identifier == "name":
            return self.current_path
        elif identifier == "position":
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
        stage = self.usd_context.get_stage()
        if not stage or self.current_path == "":
            return [0, 0, 0]

        # Get position directly from USD
        prim = stage.GetPrimAtPath(self.current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        # Find the top center of the bounding box and add a small offset upward.
        x_Pos = (bboxMin[0] + bboxMax[0]) * 0.5
        y_Pos = bboxMax[1] + 5 
        z_Pos = (bboxMin[2] + bboxMax[2]) * 0.5
        position = [x_Pos, y_Pos, z_Pos]
        return position

    # NEW: function that will get called when objects change in the scene. We only care about our selected object so we loop through all notices that get passed along until we find ours
    def notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        """Called by Tf.Notice.  Used when the current selected object changes in some way."""
        for p in notice.GetChangedInfoOnlyPaths():
            if self.current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)
    # END NEW

    def destroy(self):
        self.events = None
        self.stage_event_delegate.unsubscribe()
```
</details>

<br>

## Congratulations! 
Your viewport should now display the object info above the selected object and move with the primitive in the scene. You have successfully created the Object Info Extension!

![](./Images/objectinfo_finished.gif "Object Info Moving with Object in Viewport")