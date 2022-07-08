from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SliderManipulator(sc.Manipulator):

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = 100
        self.thickness = 5
        self._radius = 5
        self._radius_hovered = 7

        def set_radius(circle, radius):
            circle.radius = radius

        # We don't recreate the gesture to make sure it's active when the
        # underlying object is recreated
        self._arc_gesture = self._ArcGesture(self)

        if hasattr(sc, "HoverGesture"):
            self._hover_gesture = sc.HoverGesture(
                on_began_fn=lambda sender: set_radius(sender, self._radius_hovered),
                on_ended_fn=lambda sender: set_radius(sender, self._radius),
            )
        else:
            self._hover_gesture = None

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

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        # If we don't have a selection then just return
        if self.model.get_item("name") == "":
            return

        _min = self.model.get_as_floats(self.model.get_item("min"))[0]
        _max = self.model.get_as_floats(self.model.get_item("max"))[0]
        value = float(self.model.get_as_floats(self.model.get_item("value"))[0])
        value_normalized = (value - _min) / (_max - _min)
        value_normalized = max(min(value_normalized, 1.0), 0.0)
        position = self.model.get_as_floats(self.model.get_item("position"))

        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):

            # Left line
            line_from = -self.width * 0.5
            line_to = -self.width * 0.5 + self.width * value_normalized - self._radius
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

            # NEW: same as left line but flipped
            # Right line
            line_from = -self.width * 0.5 + self.width * value_normalized + self._radius
            line_to = self.width * 0.5
            if line_to > line_from:
                sc.Line([line_from, 0, 0], [line_to, 0, 0], color=cl.darkgray, thickness=self.thickness)

    
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
               
                sc.Arc(radius, axis=2, color=cl.gray, gestures=gestures)
                 # END NEW

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