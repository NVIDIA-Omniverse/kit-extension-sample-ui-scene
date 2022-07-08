from omni.ui import scene as sc
import omni.ui as ui


class ObjInfoManipulator(sc.Manipulator):

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

    def on_model_updated(self, item):
        # Regenerate the manipulator
        self.invalidate()