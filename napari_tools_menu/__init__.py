import warnings

from toolz import curry
from typing import Callable

try:
    import napari._qt
    from qtpy.QtWidgets import QMenu
except Exception as e:
    warnings.warn("Importing QT failed; now introducing dummy definitions of QMenu class and register_function decorator.")

    # Define dummy class QMenu, to be used in ToolsMenu below
    class QMenu:
        pass

    # Define dummy register_action decorator, so that it can be imported and
    # used in packages that do not depend on QT
    @curry
    def register_action(func: Callable, menu:str, *args, **kwargs) -> Callable:
        return func


import numpy as np

import inspect
from functools import wraps

__version__ = "0.1.19"

class ToolsMenu(QMenu):

    def __init__(self, window: 'Window', viewer):
        from napari.utils.translations import trans
        import napari

        super().__init__(trans._('&Tools'), window._qt_window)
        self.viewer = viewer

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
            napari_viewer = self.viewer
            action, type_, args, kwargs = action_type_tuple
            dw = None
            if type_ == "action":
                action(napari_viewer)
            elif type_ == "function":
                dw = napari_viewer.window.add_dock_widget(make_gui(action, napari_viewer, *args, **kwargs), area='right', name=title)
            elif type_ == "dock_widget":
                # Source: https://github.com/napari/napari/blob/1287e618469e765a6db0e80d11e736b738e62823/napari/_qt/qt_main_window.py#L669
                # if the signature is looking a for a napari viewer, pass it.
                kwargs = {}
                for param in inspect.signature(action.__init__).parameters.values():
                    if param.name == 'napari_viewer':
                        kwargs['napari_viewer'] = napari_viewer
                        break
                    if param.annotation in ('napari.viewer.Viewer', napari.Viewer):
                        kwargs[param.name] = napari_viewer
                        break
                    # cannot look for param.kind == param.VAR_KEYWORD because
                    # QWidget allows **kwargs but errs on unknown keyword arguments

                # instantiate the widget
                wdg = action(**kwargs)
                dw = napari_viewer.window.add_dock_widget(wdg, name=title)
            if dw is not None:
                # workaround for https://github.com/napari/napari/issues/4348
                dw._close_btn = False

        sub_sub_menu.triggered.connect(func)
        return sub_sub_menu

def make_gui(func, viewer, *args, **kwargs):
    gui = None

    from napari.types import ImageData, LabelsData, PointsData, SurfaceData
    from magicgui import magicgui
    import inspect

    sig = inspect.signature(func)

    @wraps(func)
    def worker_func(*iargs, **ikwargs):
        data = func(*iargs, **ikwargs)
        if data is None:
            return None

        # determine scale of passed data
        scale = None
        from napari_workflows._workflow import _get_layer_from_data
        for passed_data in iargs:
            layer = _get_layer_from_data(viewer, passed_data)
            if layer is not None and isinstance(layer, napari.layers.Image):
                scale = layer.scale

        target_layer = None

        if sig.return_annotation in [ImageData, "napari.types.ImageData", LabelsData, "napari.types.LabelsData",
                                     PointsData, "napari.types.PointsData", SurfaceData, "napari.types.SurfaceData"]:
            op_name = func.__name__
            new_name = f"Result of {op_name}"

            # we now search for a layer that has -this- magicgui attached to it
            try:
                # look for an existing layer
                target_layer = next(x for x in viewer.layers if x.source.widget is gui)
                target_layer.data = data
                target_layer.name = new_name
                # layer.translate = translate
                if sig.return_annotation in [PointsData, "napari.types.PointsData"]:
                    target_layer.size = np.asarray(viewer.dims.range).max() * 0.01

            except StopIteration:
                # otherwise create a new one
                from napari.layers._source import layer_source
                with layer_source(widget=gui):
                    if sig.return_annotation in [ImageData, "napari.types.ImageData"]:
                        target_layer = viewer.add_image(data, name=new_name)
                    elif sig.return_annotation in [LabelsData, "napari.types.LabelsData"]:
                        target_layer = viewer.add_labels(data, name=new_name)
                    elif sig.return_annotation in [PointsData, "napari.types.PointsData"]:
                        target_layer = viewer.add_points(data, name=new_name)
                        target_layer.size = np.asarray(viewer.dims.range).max() * 0.01
                    elif sig.return_annotation in [SurfaceData, "napari.types.SurfaceData"]:
                        target_layer = viewer.add_surface(data, name=new_name)

                # apply scale to data if successfully determined above
                if scale is not None and target_layer is not None:
                    if len(target_layer.data.shape) == len(scale):
                        target_layer.scale = scale
                    if len(target_layer.data.shape) < len(scale):
                        target_layer.scale = scale[-len(target_layer.data.shape):]

        if target_layer is not None:
            # update the workflow manager in case it's installed
            try:
                from napari_workflows import WorkflowManager
                workflow_manager = WorkflowManager.install(viewer)
                workflow_manager.update(target_layer, func, *iargs, **ikwargs)
            except ImportError:
                pass

            return None
        else:
            return data

    gui = magicgui(worker_func, *args, **kwargs)
    return gui

ToolsMenu.menus = {}

def list_registered():
    entries = sorted(list(ToolsMenu.menus.keys()))
    for k in entries:
        thing = ToolsMenu.menus[k][0]
        print(k)
        print("  ", inspect.getmodule(thing).__name__)
        print("  ", thing)

@curry
def register_action(func: Callable, menu:str, *args, **kwargs) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [func, "action", args, kwargs]
    return func

@curry
def register_function(func: Callable, menu:str, *args, **kwargs) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [func, "function", args, kwargs]
    return func

@curry
def register_dock_widget(widget, menu:str, *args, **kwargs) -> Callable:
    ToolsMenu.menus[menu.replace(" > ", ">")] = [widget, "dock_widget", args, kwargs]
    return widget

ever_warned = False

# monkey patch the napari menu
# Why?
#   https://github.com/chanzuckerberg/napari-hub/issues/237
#   https://github.com/napari/napari/issues/3015
try:
    if not hasattr(napari._qt.qt_main_window._QtMainWindow.__class__, "_add_menus_bkp"):
        napari._qt.qt_main_window.Window._add_menus_bkp = napari._qt.qt_main_window.Window._add_menus

        def _add_menus(self):
            self._add_menus_bkp()
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=FutureWarning)
                self.tools_menu = ToolsMenu(self, self.qt_viewer.viewer)
            self.main_menu.insertMenu(self.help_menu.menuAction(), self.tools_menu)

            self.tools_menu.addSeparator()
            act = self.tools_menu.addAction("Tools Info")
            def func(whatever=None):
                list_registered()
            act.triggered.connect(func)

        napari._qt.qt_main_window.Window._add_menus = _add_menus
except:
    if not ever_warned:
        #warnings.warn("Error in monkey patching napari. Please let @haesleinleinhuepf know at\nhttps://github.com/haesleinhuepf/napari-tools-menu/issues")
        ever_warned = True

