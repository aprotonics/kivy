from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout


class CustomRelativeLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super(CustomRelativeLayout, self).__init__(**kwargs)


class CustomBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CustomBoxLayout, self).__init__(**kwargs)
        self.padding = 10

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class ButtonsBox(RelativeLayout):
    def __init__(self, **kwargs):
        super(ButtonsBox, self).__init__(**kwargs)
        self.hidden = False
        
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class MainButtonsBox(GridLayout):
    def __init__(self, **kwargs):
        super(MainButtonsBox, self).__init__(**kwargs)
        self.hidden = True

        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class CreateButtonsBox(ButtonsBox):
    def __init__(self, **kwargs):
        super(CreateButtonsBox, self).__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class EditButtonsBox(ButtonsBox):
    def __init__(self, **kwargs):
        super(EditButtonsBox, self).__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class CreateIconBox(GridLayout):
    def __init__(self, **kwargs):
        super(CreateIconBox, self).__init__(**kwargs)
