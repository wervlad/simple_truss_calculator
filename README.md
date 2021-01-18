# Simple Truss Calculator
![app screenshot](/screenshots/calculate.png?raw=true)

![animated demo](/screenshots/animated_demo.gif?raw=true)

## Installation
**Python** and **NumPy** are required to run this app. In Linux Python is most likely already installed. Check the version to ensure you have at least Python 3.6 that supports f-strings. Otherwise use your distro package manager to install it. In Windows download installer from [Python home page](https://www.python.org/downloads/). To install NumPy follow instructions on [NumPy home page](https://numpy.org/install/).

Download project files and start application:

    git clone https://github.com/wervlad/simple_truss_calculator.git
    cd simple_truss_calculator
    python3 run.pyw

## Hotkeys
- Delete - delete selected item
- Escape - cancel creating/editing item and return to normal mode
- Ctrl-N - create new truss (all unsaved changes to current will be lost)
- Ctrl-L - load truss from file (all unsaved changes to current will be lost)
- Ctrl-S - save truss to file
- Ctrl-Z - undo previous change
- Ctrl-Y - redo change
- Ctrl-A - show item labels
- Ctrl-U - redraw truss
- Ctrl-C - calculate
- Ctrl-P - create new pinned support
- Ctrl-R - create new roller support
- Ctrl-J - create new pin joint
- Ctrl-B - create new beam
- Ctrl-F - create new force

## License
Copyright © Vladmir Rusakov. Distributed under the GNU Lesser General Public License v2.1. See the file [LICENSE](/LICENSE).
