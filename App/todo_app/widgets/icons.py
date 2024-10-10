from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior


class CreateIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(CreateIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0, "y": 0}
        self.size_hint = (1, 1)
    
    def on_release(instance):
        instance.root.go_to_create_todo()
    

class CancelIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(CancelIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0, "y": 0}
        self.size_hint = (0.25, 1)
    
    def on_release(instance):
        instance.root.unselect_all_todos()
        instance.root.remove_buttons()
        instance.root.hide_buttons_box()


class SelectAllIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(SelectAllIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0.25, "y": 0}
        self.size_hint = (0.25, 1)
    
    def on_release(instance):
        instance.root.select_all_todos()


class DeleteIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(DeleteIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0.5, "y": 0}
        self.size_hint = (0.25, 1)

    def on_release(instance):
        instance.root.delete_todos()
        instance.root.remove_buttons()


class PinIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(PinIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0.75, "y": 0}
        self.size_hint = (0.25, 1)
    
    def on_release(instance):
        instance.root.start_pinning_todo()
        instance.root.remove_buttons()
        instance.root.hide_buttons_box()


class UnpinIcon(ButtonBehavior, AsyncImage):
    def __init__(self, root, **kwargs):
        super(UnpinIcon, self).__init__(**kwargs)
        self.root = root
        self.pos_hint = {"x": 0.75, "y": 0}
        self.size_hint = (0.25, 1)

    def on_release(instance):
        instance.root.start_pinning_todo()
        instance.root.remove_buttons()
        instance.root.hide_buttons_box()


class SelectIcon(ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super(SelectIcon, self).__init__(**kwargs)
        self.source = "img/select.png"
        self.size_hint = (0.18, 1)

        with self.canvas.before:
            Color(0.35, 0.35, 0.35, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class CompletedIcon(ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super(CompletedIcon, self).__init__(**kwargs)
        self.source = "img/completed.png"


class PinnedIcon(ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super(PinnedIcon, self).__init__(**kwargs)
        self.source = "img/pinned.png"


class BackIcon(ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super(BackIcon, self).__init__(**kwargs)
        self.source = "img/back.png"


class SaveIcon(ButtonBehavior, AsyncImage):
    def __init__(self, **kwargs):
        super(SaveIcon, self).__init__(**kwargs)
        self.source = "img/save.png"
