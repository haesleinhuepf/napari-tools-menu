# napari-tools-menu

[![License](https://img.shields.io/pypi/l/napari-tools-menu.svg?color=green)](https://github.com/haesleinhuepf/napari-tools-menu/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-tools-menu.svg?color=green)](https://pypi.org/project/napari-tools-menu)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-tools-menu.svg?color=green)](https://python.org)
[![tests](https://github.com/haesleinhuepf/napari-tools-menu/workflows/tests/badge.svg)](https://github.com/haesleinhuepf/napari-tools-menu/actions)
[![codecov](https://codecov.io/gh/haesleinhuepf/napari-tools-menu/branch/master/graph/badge.svg)](https://codecov.io/gh/haesleinhuepf/napari-tools-menu)

Attaches a customizable Tools menu to napari

![img.png](https://github.com/haesleinhuepf/napari-tools-menu/raw/main/images/screenshot.png)
----------------------------------

## Usage

Just add napari-tools-menu to the dependencies of your napari-plugin. Afterwards, you can annotate your functions and dock widgets using the following syntax.
The specified menu path will be used to put your tool in the right place in the tools menu. 
All menus and sub-menus will be listed alphabetically.

```python
from napari_tools_menu import register_function, register_action, register_dock_widget


@register_action(menu="Utilities > Action")
def test_function(viewer):
    print("hello")


@register_function(menu="Utilities > Function")
def test_function_with_params(sigma: float = 0.5):
    print("sigma", sigma)


@register_dock_widget(menu="Utilities > Widget")
class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer):
```

Note: This implementation is based on a [monkey patch](https://en.wikipedia.org/wiki/Monkey_patch) of napari, tested with napari 0.4.11. 
Thus, it might stop working with a future version of napari, e.g. when the [new plugin engine](https://github.com/napari/napari/issues/3115) is finished.
 For now it is a nice workaround to ease the life of end-users.

## Menu name suggestions

To keep the Tools menu clean and organized, some suggestions should be made.
Create category menus that classify your tool in a way such that a broad audience knows what it's doing. Examples:

  * Registration
  * Segmentation
  * Measurement
  * Visualization
  * Utilities  

Put a descriptive function name in the menu name first and the implementation behind. Examples:

  * Segmentation > Threshold (Otsu et al 1979)
  * Segmentation > Threshold (my algorithm)
  * Segmentation > Cell labeling (CellLab)
  * Segmentation > Nuclei segmentation (Nuc-Dect)

Again, there are no constraints. However, please make the life of (y)our users easy by keeping this menu well organized.

## Installation

You can install `napari-tools-menu` via [pip]:

    pip install napari-tools-menu

## Contributing

Contributions are very welcome. Tests can be run with [pytest], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-tools-menu" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/haesleinhuepf/napari-tools-menu/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
