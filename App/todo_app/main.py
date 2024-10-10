from functools import partial
from threading import Thread

import os.path

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.loader import Loader, ProxyImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget 
from kivy.uix.image import AsyncImage, Image
from kivy.uix.behaviors import ButtonBehavior

from widgets.multi_exp_widget import MultiExpressionButton, MultiExpressionLabel
from layouts.layouts import (CustomRelativeLayout, CustomBoxLayout, MainButtonsBox, CreateButtonsBox, 
                     EditButtonsBox, CreateIconBox)
from widgets.icons import (CreateIcon, CancelIcon, SelectAllIcon, DeleteIcon, 
                           PinIcon, UnpinIcon, SelectIcon, CompletedIcon, PinnedIcon, BackIcon, SaveIcon)

from kivy.config import Config

# Config.set("graphics", "resizable", "0")
# Config.set("graphics", "width", "400")
# Config.set("graphics", "height", "900")

from kivy.core.window import Window

Window.clearcolor = (0.2, 0.2, 0.2, 0.2)


class CustomButton(MultiExpressionButton):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.text = "Modify"
        self.font_size = (Window.width ** 2 + Window.height ** 2) / 19 ** 4
        self.size_hint = (0.18, 1)

        with self.canvas.after:
            Color(0.35, 0.35, 0.35, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def on_single_press(instance):
        print("single press")
        if screens[0].selected_todo_number == 0:
            screens[0].add_completed_icon(instance)
            screens[0].complete_todo(instance)
    
    def on_double_press(instance):
        print("double press")
    
    def on_long_press(instance):
        print("long press")


class PressableLabel(ButtonBehavior, MultiExpressionLabel):
    pass


class CustomLabel(PressableLabel):
    def __init__(self, **kwargs):
        super(CustomLabel, self).__init__(**kwargs)
        self.text = "Label"
        self.text_content = self.text
        self.font_size = (Window.width ** 2 + Window.height ** 2) / 16 ** 4
        self.strikethrough = False

        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1) 
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

        self.selected = False
        self.completed = False
        self.pinned = False

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def validate_text(self):
        if self.text_content.find("\n") != -1:
            stroke = self.text_content.split("\n")[0]
        else:
            stroke = self.text_content
        if len(stroke) > 20:
            self.text = stroke[:20]
            self.text = self.text.rstrip()
            self.text += "..."
        else:
            self.text = stroke

    def on_size(self, *args):
        self.text_size = self.size

    def on_completed(self, instance, value):
        if value == True:
            self.strikethrough = True

    def on_single_press(instance):
        print("single press")
        if screens[0].selected_todo_number == 0:
            screens[0].go_to_edit_todo(instance.parent.parent)
        else:
            screens[0].start_selecting(instance)
            print(instance.id_number)

    def on_double_press(instance):
        print("double press")
    
    def on_custom_long_press(instance):
        print("custom long press")

        # for preventing false long press
        if sm.current == "main":
            screens[0].start_selecting(instance)
            print(instance.id_number)


class MainWindow(Screen):
    scroll_view = ObjectProperty(None)
    todos_grid_container = ObjectProperty(None)
    buttons_box = ObjectProperty(None)
    create_button_box = ObjectProperty(None)

    todos_initial_number = 8
    todo_height = Window.height / todos_initial_number
    todos_number = NumericProperty(todos_initial_number)
    
    first_loop = True
    selected_todo_number = 0
    all_todos_selected = BooleanProperty(False)
    completed_todos_number = 0
    pinned_todos_number = 0

    todo_added = False
    new_todo = ""

    todo_edited = False
    edited_todo = ObjectProperty(None)

    create_icon = None
    completed_icon = None
    pinned_icon = None
    cancel_icon = None
    select_all_icon = None
    delete_icon = None
    pin_icon = None
    unpin_icon = None
    select_icon = None

    partial_results = ""
    results = ""

    def on_enter(self, *args):
        print("On enter")
        print()
        
        if self.first_loop:

            global db_exists
            if not db_exists:
                # save to database
                thread = Thread(target=self.save_to_database)
                thread.start()
                db_exists = True
            else:
                self.clear_all_todos()
                self.read_from_database()
            
            self.load_images()
            self.first_loop = False

        # check if todo added
        if self.todo_added:   
            self.add_todo()
        
        # check if todo edited
        if self.todo_edited:
            self.edit_todo()

    # async loading
    def load_images(self):
        create_icon_proxyImage = Loader.image("img/add_in_circle.png")
        create_icon_proxyImage.bind(on_load=self._create_icon_loaded)
        self.create_icon = CreateIcon(self)

        completed_icon_proxyImage = Loader.image("img/completed.png")
        completed_icon_proxyImage.bind(on_load=self._completed_icon_loaded)
        self.completed_icon = CompletedIcon()

        pinned_icon_proxyImage = Loader.image("img/pinned.png")
        pinned_icon_proxyImage.bind(on_load=self._pinned_icon_loaded)
        self.pinned_icon = PinnedIcon()

        self.cancel_icon = CancelIcon(self)
        cancel_icon_proxyImage = Loader.image("img/cancel.png")
        cancel_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.cancel_icon))

        self.select_all_icon = SelectAllIcon(self)
        select_all_icon_proxyImage = Loader.image("img/select_all.png")
        select_all_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.select_all_icon))
        
        self.delete_icon = DeleteIcon(self)
        delete_icon_proxyImage = Loader.image("img/delete.png")
        delete_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.delete_icon))
        
        self.pin_icon = PinIcon(self)
        pin_icon_proxyImage = Loader.image("img/pin.png")
        pin_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.pin_icon))
        
        self.unpin_icon = UnpinIcon(self)
        unpin_icon_proxyImage = Loader.image("img/unpin.png")
        unpin_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.unpin_icon))
        
        self.select_icon = SelectIcon()
        select_icon_proxyImage = Loader.image("img/select.png")
        select_icon_proxyImage.bind(on_load=partial(self._icon_loaded, self.select_icon))    

    def _icon_loaded(self, icon, proxyImage):
        if proxyImage.image.texture:
            icon.texture = proxyImage.image.texture

    def _create_icon_loaded(self, proxyImage):
        if proxyImage.image.texture:
            create_button_box = self.create_button_box
            self.create_icon.texture = proxyImage.image.texture
            create_button_box.add_widget(self.create_icon)
    
    def _completed_icon_loaded(self, proxyImage):
        if proxyImage.image.texture:
            todos_grid_container = self.todos_grid_container
            self.completed_icon.texture = proxyImage.image.texture

            for i in range(1, self.todos_number + 1):
                box_layout = todos_grid_container.children[-i]
                relative_layout = box_layout.children[0]
                label = relative_layout.children[-1]

                if label.completed:
                    completed_icon = CompletedIcon()
                    completed_icon.id_number = i
                    completed_icon.pos_hint = {"x": 0.8, "y": 0.5}
                    completed_icon.size_hint = 0.1, 0.5

                    relative_layout.add_widget(completed_icon)

    def _pinned_icon_loaded(self, proxyImage):
        if proxyImage.image.texture:
            todos_grid_container = self.todos_grid_container
            self.pinned_icon.texture = proxyImage.image.texture

            for i in range(1, self.todos_number + 1):
                box_layout = todos_grid_container.children[-i]
                relative_layout = box_layout.children[0]
                label = relative_layout.children[-1]
            
                if label.pinned:
                    pinned_icon = PinnedIcon()
                    pinned_icon.id_number = i
                    pinned_icon.pos_hint = {"x": 0.9, "y": 0.5}
                    pinned_icon.size_hint = 0.1, 0.5

                    relative_layout.add_widget(pinned_icon) 

    def read_from_database(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        self.height = Window.height
        scroll_view.height = self.height - self.buttons_box.height
        todo_grid.height = 1

        # read properties
        todos_number = storage.get("properties")["todos_number"]
        self.todos_number = todos_number

        completed_todos_number = storage.get("properties")["completed_todos_number"]
        self.completed_todos_number = completed_todos_number

        pinned_todos_number = storage.get("properties")["pinned_todos_number"]
        self.pinned_todos_number = pinned_todos_number

        todo_height = storage.get("properties")["todo_height"]
        self.todo_height = todo_height
        
        # read todos
        for i in range(1, todos_number + 1):
            key = str(i)
            text_value = storage.get(key)["text"]
            completed_value = storage.get(key)["completed"]
            pinned_value = storage.get(key)["pinned"]

            todo_id_number = int(i)
            todo_text = str(text_value)

            if completed_value == "True":
                todo_completed = True
                strikethrough = True
            if completed_value == "False":
                todo_completed = False
                strikethrough = False

            if pinned_value == "True":
                todo_pinned = True
            if pinned_value == "False":
                todo_pinned = False

            # adding todo
            box_layout = CustomBoxLayout()
            box_layout.id_number = todo_id_number

            button = CustomButton()
            button.id_number = todo_id_number
            box_layout.add_widget(button)

            relative_layout = CustomRelativeLayout()
            relative_layout.id_number = self.todos_number
            box_layout.add_widget(relative_layout)

            label = CustomLabel()
            label.id_number = todo_id_number
            label.text_content = todo_text
            label.validate_text()
            label.strikethrough = strikethrough
            label.halign =  "left"
            label.valign = "middle"
            label.padding_x = 15
            label.completed = todo_completed
            label.pinned = todo_pinned
            
            relative_layout.add_widget(label)
            todo_grid.add_widget(box_layout)
            todo_grid.height += self.todo_height

    def save_to_database(self):   
        storage.clear()

        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        todo_grid_length = len(todo_grid.children)

        # save todos
        for i in range(todo_grid_length - 1, -1, -1):
            box_layout = todo_grid.children[i]
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]

            todo_id_number = label.id_number
            todo_text = label.text_content
            todo_completed = label.completed
            todo_pinned = label.pinned

            key = str(todo_id_number)
            text_value = str(todo_text)
            completed_value = str(todo_completed)
            pinned_value = str(todo_pinned)

            storage.put(key, text=text_value, completed=completed_value, pinned=pinned_value)
        
        # save properties
        todos_number = self.todos_number
        completed_todos_number = self.completed_todos_number
        pinned_todos_number = self.pinned_todos_number
        todo_height = self.todo_height

        storage.put("properties", todos_number=todos_number,
                                    completed_todos_number=completed_todos_number,
                                    pinned_todos_number=pinned_todos_number,
                                    todo_height=todo_height)

        self.print_db()

    def print_db(self):
        for key in storage.keys():
            value = storage.get(key)
            print(f"{key} - {value}")

    def on_all_todos_selected(self, instance, value):
        if value == True:
            self.hide_select_all_button()
        if value == False:
            self.unhide_select_all_button()

    def is_instance_selected(self, instance):
        return instance.selected

    def start_selecting(self, instance):      
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        box_layout = todo_grid.children[-instance.id_number]
        button = box_layout.children[1]
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]
        
        if not self.is_instance_selected(label):
            select_icon = SelectIcon()
            box_layout.remove_widget(button)
            box_layout.add_widget(select_icon, 1)
            label.selected = True

            self.selected_todo_number += 1

            if self.selected_todo_number == len(todo_grid.children):
                self.all_todos_selected = True

            if self.selected_todo_number == 1:
                self.show_buttons_box()
                self.add_buttons(label.pinned)

            if self.selected_todo_number == 2:
                self.hide_pin_button()

        else:
            custom_button = CustomButton()
            box_layout.remove_widget(button)
            box_layout.add_widget(custom_button, 1)
            label.selected = False

            self.selected_todo_number -= 1

            if self.all_todos_selected:
                self.all_todos_selected = False

            if self.selected_todo_number == 1:
                # check if selected_todo is pinned
                # only when self.selected_todo_number == 1
                selected_pinned_label = self.find_selected_todo()
                self.unhide_pin_button(selected_pinned_label)

            if self.selected_todo_number == 0:
                self.remove_buttons()
                self.hide_buttons_box()

    def find_selected_todo(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        todo_grid_length = len(todo_grid.children)
        
        selected_pinned_label = False
        
        for i in range(todo_grid_length - 1, -1, -1):
            box_layout = todo_grid.children[i]
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]

            if label.selected and label.pinned:
                selected_pinned_label = True         

        return selected_pinned_label

    def select_all_todos(self):
        if self.selected_todo_number == 1:
            self.hide_pin_button()
        
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        
        for box_layout in todo_grid.children:
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]

            if not self.is_instance_selected(label):
                select_icon = SelectIcon()
                box_layout.remove_widget(button)
                box_layout.add_widget(select_icon, 1)
                label.selected = True

                self.selected_todo_number += 1

        self.all_todos_selected = True

        print("all todos selected")

    def unselect_all_todos(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container

        for box_layout in todo_grid.children:
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]

            if self.is_instance_selected(label):
                custom_button = CustomButton()
                box_layout.remove_widget(button)
                box_layout.add_widget(custom_button, 1)
                label.selected = False

        self.selected_todo_number = 0
        self.all_todos_selected = False

    def add_todo(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container

        self.todos_number += 1

        box_layout = CustomBoxLayout()
        box_layout.id_number = self.todos_number

        button = CustomButton()
        button.id_number = self.todos_number
        box_layout.add_widget(button)

        relative_layout = CustomRelativeLayout()
        relative_layout.id_number = self.todos_number
        box_layout.add_widget(relative_layout)

        label = CustomLabel()
        label.id_number = self.todos_number
        label.text_content = self.new_todo
        label.validate_text()
        label.strikethrough = False
        label.halign =  "left"
        label.valign = "middle"
        label.padding_x = 15
        relative_layout.add_widget(label)

        completed_icon = CompletedIcon()
        completed_icon.id_number = self.todos_number
        completed_icon.pos_hint = {"x": 0.8, "y": 0.5}
        completed_icon.size_hint = 0, 0
        relative_layout.add_widget(completed_icon)

        pinned_icon = PinnedIcon()
        pinned_icon.id_number = self.todos_number
        pinned_icon.pos_hint = {"x": 0.9, "y": 0.5}
        pinned_icon.size_hint = 0, 0
        relative_layout.add_widget(pinned_icon)

        widget_index = self.pinned_todos_number
        todo_grid.add_widget(box_layout, widget_index)

        todo_grid.height += self.todo_height

        self.todo_added = False
        self.new_todo = ""

        self.reassign_id_numbers(todo_grid)

        thread = Thread(target=self.save_to_database)
        thread.start()

    def edit_todo(self):
        box_layout = self.edited_todo
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]
        label.validate_text()
        
        edited_todo_id_number = int(self.edited_todo.id_number)
        print("id_number", edited_todo_id_number)

        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container

        i = -1 * edited_todo_id_number
        todo_grid.children[i] = self.edited_todo

        self.todo_edited = False
        self.edited_todo = ""

        thread = Thread(target=self.save_to_database)
        thread.start()

    def complete_todo(self, instance):
        print(instance.text)
        box_layout = instance.parent
        button = box_layout.children[1]
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]

        if not label.completed:
            label.strikethrough = True
            button.text = "Revert"
            label.completed = True
            self.completed_todos_number += 1
        else:
            label.strikethrough = False
            button.text = "Modify"
            label.completed = False
            self.completed_todos_number -= 1
        
        thread = Thread(target=self.save_to_database)
        thread.start()

    # editing buttons
    def show_buttons_box(self):
        buttons_box = self.buttons_box
        root = buttons_box.parent
        buttons_box.size_hint = 1, None
        buttons_box.height = root.height * 0.07
        buttons_box.hidden = False
    
    def hide_buttons_box(self):
        buttons_box = self.buttons_box
        buttons_box.size_hint = 0, None
        buttons_box.height = 0
        buttons_box.hidden = True

    def add_buttons(self, instance_pinned):
        create_button_box = self.create_button_box
        buttons_box = self.buttons_box
        
        create_icon = create_button_box.children[0]
        create_button_box.remove_widget(create_icon)

        buttons_box.add_widget(self.cancel_icon)

        if self.todos_number > 1:
            buttons_box.add_widget(self.select_all_icon)

        buttons_box.add_widget(self.delete_icon)

        if not instance_pinned:
            buttons_box.add_widget(self.pin_icon)
        else:
            buttons_box.add_widget(self.unpin_icon)
    
    def remove_buttons(self):
        create_button_box = self.create_button_box
        buttons_box = self.buttons_box

        buttons_box.clear_widgets()

        create_button_box.add_widget(self.create_icon)
    
    def hide_select_all_button(self):
        if self.todos_number > 1:
            buttons_box = self.buttons_box
            select_all_button = buttons_box.children[-2]
            buttons_box.remove_widget(select_all_button)
            print("remove ", select_all_button)

    def unhide_select_all_button(self):
        buttons_box = self.buttons_box
        buttons_box.add_widget(self.select_all_icon, 1)

    def hide_pin_button(self):
        buttons_box = self.buttons_box
        pin_button = buttons_box.children[0]
        buttons_box.remove_widget(pin_button)
    
    def unhide_pin_button(self, selected_pinned_label):
        buttons_box = self.buttons_box
        
        if not selected_pinned_label:
            buttons_box.add_widget(self.pin_icon)
        else:
            buttons_box.add_widget(self.unpin_icon)

    def add_completed_icon(self, instance):
        box_layout = instance.parent
        button = box_layout.children[1]
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]
        
        if label.pinned:
            widget_index = 1
            pos_hint = {"x": 0.8, "y": 0.5}
        else:
            widget_index = 0
            pos_hint = {"x": 0.9, "y": 0.5}

        if not label.completed:
            completed_icon = CompletedIcon()
            completed_icon.id_number = box_layout.id_number
            completed_icon.pos_hint = pos_hint
            completed_icon.size_hint = 0.1, 0.5
            relative_layout.add_widget(completed_icon, widget_index)
        else:
            completed_icon = relative_layout.children[widget_index]
            relative_layout.remove_widget(completed_icon)

    # for mobile input     
    def start_pinning_todo(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        todo_grid_length = len(todo_grid.children)

        for i in range(todo_grid_length - 1, -1, -1):
            box_layout = todo_grid.children[i]
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]
            id_number = box_layout.id_number

            if label.selected and not label.pinned:
                # pin todo

                custom_button = CustomButton()
                box_layout.remove_widget(button)
                box_layout.add_widget(custom_button, 1)

                label.selected = False
                label.pinned = True

                if label.completed:
                    completed_icon = relative_layout.children[0]
                    completed_icon.pos_hint = {"x": 0.8, "y": 0.5}

                pinned_icon = PinnedIcon()
                pinned_icon.id_number = id_number
                pinned_icon.pos_hint = {"x": 0.9, "y": 0.5}
                pinned_icon.size_hint = 0.1, 0.5
                relative_layout.add_widget(pinned_icon)

                self.pinned_todos_number += 1
                self.selected_todo_number = 0
                
                todo_grid.remove_widget(box_layout)
                widget_index = self.pinned_todos_number - 1
                todo_grid.add_widget(box_layout, widget_index)

                print("pin todo - ", id_number)

                break
                
            if label.selected and label.pinned:
                # unpin todo

                custom_button = CustomButton()
                box_layout.remove_widget(button)
                box_layout.add_widget(custom_button, 1)

                label.selected = False
                label.pinned = False

                if label.completed:
                    completed_icon = relative_layout.children[1]
                    completed_icon.pos_hint = {"x": 0.9, "y": 0.5}

                pinned_icon = relative_layout.children[0]
                relative_layout.remove_widget(pinned_icon)

                self.pinned_todos_number -= 1
                self.selected_todo_number = 0

                todo_grid.remove_widget(box_layout)
                widget_index = self.pinned_todos_number
                todo_grid.add_widget(box_layout, widget_index)

                print("unpin todo - ", id_number)

                break

        self.reassign_id_numbers(todo_grid)

        thread = Thread(target=self.save_to_database)
        thread.start()

    def delete_todos(self):        
        todo_deleted = 0
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        todo_grid_length = len(todo_grid.children)

        for i in range(todo_grid_length - 1, -1, -1):
            box_layout = todo_grid.children[i]
            button = box_layout.children[1]
            relative_layout = box_layout.children[0]
            label = relative_layout.children[-1]

            if label.selected:
                id_number = box_layout.id_number
                todo_grid.remove_widget(box_layout)
                self.todos_number -= 1
                if label.pinned:
                    self.pinned_todos_number -= 1
                if label.completed:
                    self.completed_todos_number -= 1

                todo_deleted += 1
                print("delete todo - ", id_number)

        todo_grid.height -= todo_deleted * self.todo_height

        self.selected_todo_number = 0
        print(f"delete {todo_deleted} todos")
        print("todos number - ", self.todos_number)

        self.hide_buttons_box()
        self.reassign_id_numbers(todo_grid)

        thread = Thread(target=self.save_to_database)
        thread.start()

    def reassign_id_numbers(self, todo_grid):    
        for i in range(len(todo_grid.children)):
            box_layout = todo_grid.children[i]
            box_layout.id_number = self.todos_number - i

            button = box_layout.children[1]
            button.id_number = self.todos_number - i

            relative_layout = box_layout.children[0]
            relative_layout.id_number = self.todos_number - i

            label = relative_layout.children[-1]
            label.id_number = self.todos_number - i

            if label.pinned:
                completed_icon = relative_layout.children[1]
            else:
                completed_icon = relative_layout.children[0]
            completed_icon.id_number = self.todos_number - i

            pinned_icon = relative_layout.children[0]
            pinned_icon.id_number = self.todos_number - i
        
        print("id numbers reassigned")
    
    def clear_all_todos(self):
        scroll_view = self.scroll_view
        todo_grid = self.todos_grid_container
        todo_grid.clear_widgets()
        todo_grid.height = 0

    # going to other screens
    def go_to_create_todo(self):
        self.manager.transition.direction = "left"
        sm.current = "create"

    def go_to_edit_todo(self, instance):
        screens[2].edited_todo = instance
        self.manager.transition.direction = "left"
        sm.current = "edit"


class CreateToDoWindow(Screen):
    buttons_box = ObjectProperty(None)
    todo_input = ObjectProperty(None)
    
    def on_enter(self, *args):
        Window.clearcolor = (1, 1, 1, 1)
        self.todo_input.focus = True
    
    def add_todo(self):     
        if self.todo_input.text != "":
            screens[0].todo_added = True
            screens[0].new_todo = self.todo_input.text
            self.manager.transition.direction = "left"
            self.todo_input.text = ""
            Window.clearcolor = (0.2, 0.2, 0.2, 0.2)
            sm.current = "main"
        else:
            self.cancel()
    
    def cancel(self):
        self.manager.transition.direction = "right"
        self.todo_input.text = ""
        Window.clearcolor = (0.2, 0.2, 0.2, 0.2)
        sm.current = "main"


class EditToDoWindow(Screen):
    buttons_box = ObjectProperty(None)
    todo_input = ObjectProperty(None)
    edited_todo = ObjectProperty(None)

    def on_enter(self, *args):
        Window.clearcolor = (1, 1, 1, 1)
        self.manager.transition.direction = "right"

        box_layout = self.edited_todo
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]
        
        self.todo_input.text = label.text_content
        self.todo_input.strikethrough = label.strikethrough
        self.todo_input.focus = True
    
    def edit_todo(self):
        box_layout = self.edited_todo
        relative_layout = box_layout.children[0]
        label = relative_layout.children[-1]

        label.text_content = self.todo_input.text
        label.strikethrough = self.todo_input.strikethrough
        screens[0].todo_edited = True
        screens[0].edited_todo = self.edited_todo
        self.todo_input.text = ""
        Window.clearcolor = (0.2, 0.2, 0.2, 0.2)
        sm.current = "main"
    
    def cancel(self):
        self.todo_input.text = ""
        Window.clearcolor = (0.2, 0.2, 0.2, 0.2)
        sm.current = "main"


kv = Builder.load_file("main.kv")
storage = JsonStore("strg.json")
db_exists = os.path.exists("strg.json")

Loader.num_workers = 10
Loader.max_upload_per_frame = 10

sm = ScreenManager()
screens = [MainWindow(name="main"), CreateToDoWindow(name="create"), EditToDoWindow(name="edit")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "main"


class MyMainApp(App):
    
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()


# Todos:

# Later:
# add sorting by Created Date
