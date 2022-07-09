# Slider Manipulator (omni.example.ui_scene.slider_manipulator)
![](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/raw/main/exts/omni.example.ui_scene.slider_manipulator/data/preview.png)

## Overview

We provide the End-to-End example that draws a 3D slider in the viewport overlay
on the top of the bounding box of the selected imageable. The slider controls
the scale of the prim. It has a custom manipulator, model, and gesture. When the
slider's value is changed, the manipulator processes the custom gesture that
changes the data in the model, which changes the data directly in the USD stage.

​The viewport overlay is synchronized with the viewport using `Tf.Notice` that
watches the USD Camera.

### Manipulator

The manipulator is a very basic implementation of the slider in 3D space. The
main feature of the manipulator is that it redraws and recreates all the
children once the model is changed. It makes the code straightforward. It takes
the position and the slider value from the model, and when the user changes the
slider position, it processes a custom gesture. It doesn't write to the model
directly to let the user decide what to do with the new data and how the
manipulator should react to the modification. For example, if the user wants to
implement the snapping to the round value, it would be handy to do it in the
custom gesture.

### Model

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

## [Tutorial](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/tree/main/exts/omni.example.ui_scene.object_info/Tutorial)
This extension sample also includes a step-by-step tutorial to accelerate your growth as you learn to build your own Omniverse Kit extensions. 

In the tutorial you will learn how to create an extension from the Extension Manager in Omniverse Code, set up your files, and use Omniverse's Library. Additionally, the tutorial has a `Final Scripts` folder to use as a reference as you go along. 

​[Get started with the tutorial here.](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/tree/main/exts/omni.example.ui_scene.slider_manipulator/Tutorial)

## Usage

Once the extension is enabled in the `Extension Manager`, go to your `Viewport` and right-click to create a primitive - such as a cube, sphere, cyclinder, etc. Then, left-click/select the primitive to view and manipulate the slider.
​

