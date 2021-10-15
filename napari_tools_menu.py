
"""
This module is an example of a barebones function plugin for napari

Replace code below according to your needs.
"""
import warnings
#from napari_plugin_engine import napari_hook_implementation
import napari
from qtpy.QtWidgets import QMenu
from napari.utils.translations import trans
from toolz import curry
from typing import Callable
from magicgui import magicgui
import inspect

__version__ = "0.1.0"

class ToolsMenu(QMenu):

    def __init__(self, window: 'Window'):
        super().__init__(trans._('&Tools'), window._qt_window)

        entries = sorted(list(ToolsMenu.menus.keys()))

        all_sub_menus = {}

        for k in entries:
            sub_menus = k.split(">")
            if len(sub_menus) != 2:
                warnings.warn("Menu " + k + " is ignored because it has the wrong number of levels.\nUse 'Main menu>Sub menu'.")
                continue
            if sub_menus[0] not in all_sub_menus.keys():
                new_menu = QMenu(sub_menus[0], window._qt_window)
                all_sub_menus[sub_menus[0]] = new_menu
                self.addMenu(new_menu)

            menu = all_sub_menus[sub_menus[0]]
            self.make_sub_sub_menu(menu, sub_menus[1], window, ToolsMenu.menus[k])

    def make_sub_sub_menu(self, menu, title, window, action_type_tuple):
        sub_sub_menu = menu.addAction(title)

        def func(whatever=None):
            # ugh
            napari_viewer = window._qt_window.qt_viewer.viewer
            action, type_ = action_type_tuple
            if type_ == "action":
                action(napari_viewer)
            elif type_ == "function":
                napari_viewer.window.add_dock_widget(magicgui(action), area='right', name=title)
            elif type_ == "dock_widget":
                # Source: https://github.com/napari/napari/blob/1287e618469e765a6db0e80d11e736b738e62823/napari/_qt/qt_main_window.py#L669
                # if the signature is looking a for a napari viewer, pass it.
                kwargs = {}
                for param in inspect.signature(action.__init__).parameters.values():
                    if param.name == 'napari_viewer':
                        kwargs['napari_viewer'] = napari_viewer
                        break
                    if param.annotation in ('napari.viewer.Viewer', napari.Viewer):
                        kwargs[param.name] = self.qt_viewer.viewer
                        break
                    # cannot look for param.kind == param.VAR_KEYWORD because
                    # QWidget allows **kwargs but errs on unknown keyword arguments

                # instantiate the widget
                wdg = action(**kwargs)
                napari_viewer.window.add_dock_widget(wdg, name=title)


        sub_sub_menu.triggered.connect(func)
        return sub_sub_menu

ToolsMenu.menus = {}

@curry
def register_action(func: Callable, menu:str) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [func, "action"]
    return func

@curry
def register_function(func: Callable, menu:str) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [func, "function"]
    return func

@curry
def register_dock_widget(widget, menu:str) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [widget, "dock_widget"]
    return widget


# monkey patch the napari menu
# Why?
#   https://github.com/chanzuckerberg/napari-hub/issues/237
#   https://github.com/napari/napari/issues/3015
if not hasattr(napari._qt.qt_main_window._QtMainWindow.__class__, "_add_menus_bkp"):
    napari._qt.qt_main_window.Window._add_menus_bkp = napari._qt.qt_main_window.Window._add_menus

    def _add_menus(self):
        print("Hi")
        self._add_menus_bkp()
        self.tools_menu = ToolsMenu(self)
        self.main_menu.addMenu(self.tools_menu)
        print("Jack")

    napari._qt.qt_main_window.Window._add_menus = _add_menus

# not sure if this is necessary; maybe only in case of plugin call order issues
#@napari_hook_implementation
#def napari_experimental_provide_function():
#    return []


