from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from napari_tools_menu.__init__ import register_function, register_action, register_dock_widget

@register_action(menu="Utilities > Action")
def a_function(viewer):
    print("hello")

@register_function(menu="Utilities > Function")
def a_function_with_params(sigma:float=0.5):
    print("sigma", sigma)

@register_dock_widget(menu="Utilities > Widget")
class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

@register_action(menu="Registration > a")
def a_function1(viewer):
    print("hello")
@register_action(menu="Segmentation > Threshold (Otsu et al 1979)")
def a_function2(viewer):
    print("hello")
@register_action(menu="Measurement > Action")
def a_function3(viewer):
    print("hello")
@register_action(menu="Visualization > Action")
def a_function4(viewer):
    print("hello")
@register_action(menu="Segmentation > Threshold (my algorithm)")
def a_function5(viewer):
    print("hello")
@register_action(menu="Segmentation > Cell labeling (CellLab)")
def a_function6(viewer):
    print("hello")
@register_action(menu="Segmentation > Nuclei segmentation (Nuc-Dect)")
def a_function7(viewer):
    print("hello")
@register_action(menu="Utilities > Action")
def a_function8(viewer):
    print("hello")

def test_list(make_napari_viewer):
    viewer = make_napari_viewer()
