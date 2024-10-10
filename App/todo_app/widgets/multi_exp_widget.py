import time

from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label


DOUBLE_TAP_TIME = 0.1   # Change time in seconds
LONG_PRESSED_TIME = 0.8  # Change time in seconds


class MultiExpressionButton(Button):
    def __init__(self, **kwargs):
        super(MultiExpressionButton, self).__init__(**kwargs)
        self.start = 0
        self.single_hit = 0
        self.press_state = False
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        self.register_event_type('on_long_press')

    def on_touch_down(self, touch):
        if not touch.is_mouse_scrolling:
            if self.collide_point(touch.x, touch.y):
                self.start = time.time()
                if touch.is_double_tap:
                    self.press_state = True
                    self.dispatch('on_double_press')
            else:
                return super(MultiExpressionButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if not touch.is_mouse_scrolling and self.press_state is False:
            if self.collide_point(touch.x, touch.y):
                stop = time.time()
                awaited = stop - self.start

                def not_double(time):
                    nonlocal awaited
                    if awaited > LONG_PRESSED_TIME:
                        self.dispatch('on_long_press')
                    else:
                        if not touch.is_double_tap:
                            self.dispatch('on_single_press')

                self.single_hit = Clock.schedule_once(not_double, DOUBLE_TAP_TIME)
            else:
                return super(MultiExpressionButton, self).on_touch_down(touch)
        else:
            self.press_state = False

    def on_single_press(instance):
        pass
    
    def on_double_press(instance):
        pass

    def on_long_press(instance):
        pass


class MultiExpressionLabel(Label):
    def __init__(self, **kwargs):
        super(MultiExpressionLabel, self).__init__(**kwargs)
        self.start = 0
        self.current = 0
        self.single_hit = 0
        self.press_state = False
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        self.register_event_type('on_custom_long_press')

    def check_time(self, dt):
        self.current = time.time()
        awaited = self.current - self.start

        if awaited > LONG_PRESSED_TIME:
            self.press_state = True
            self.dispatch('on_custom_long_press')
            return False

    def on_touch_down(self, touch):
        if not touch.is_mouse_scrolling:
            if self.collide_point(touch.x, touch.y):
                
                self.start = time.time()

                if not touch.is_double_tap:
                    self.event = Clock.schedule_interval(self.check_time, 1 / 30.)
                
                if touch.is_double_tap:
                    self.press_state = True
                    self.dispatch('on_double_press')
                    Clock.unschedule(self.event)
            else:
                return super(MultiExpressionLabel, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.press_state is False and not touch.is_mouse_scrolling and not touch.is_double_tap:
            if self.collide_point(touch.x, touch.y):
                
                if bool(self.start):
                    Clock.unschedule(self.event)
                    
                    self.current = time.time()
                    awaited = self.current - self.start

                    def not_double(time):
                        nonlocal awaited
                        if awaited <= LONG_PRESSED_TIME:
                            self.dispatch('on_single_press')
                        
                    self.single_hit = Clock.schedule_once(not_double, DOUBLE_TAP_TIME)

            else:
                return super(MultiExpressionLabel, self).on_touch_up(touch)
        else:
            self.press_state = False

    def on_single_press(instance):
        pass

    def on_double_press(instance):
        pass

    def on_custom_long_press(instance):
        pass
