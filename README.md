# indprog
an INteractive Data PROcessing Graph

indproc allows you to process data via a processing graph, where the nodes represent a processing
step and the edges represent the piping to move data from one process to the next.

A graphical interface allows to visually create and maintain a processing scenario, with the option
to execute the processing step either for all nodes or for sections of the graph. Here only nodes
are processed that actually need processing.


**Be aware that this software is still under heavy development! Many planned functions are not yet implemented or
can be subject to major changes.**

# Installation

## Libgtkflow
To run the GUI (and there is no CLI-only version right now), you need
[libgtkflow](https://github.com/grindhold/libgtkflow). Follow the installation instructions there.

**Note:** If you have trouble building libgtkflow, you might have a Gtk version < 3.20 (e.g. when you are on Ubuntu 16.04). A compatibility branch for GTK-3.18 can be [found here](https://github.com/grindhold/libgtkflow/tree/gtk-3.18-compatible).

## MatLab Bindings
To use MatLab processing nodes, you need the [python bindings for
MatLab](https://de.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).


## indprog

indprog itself does not need any installation, just run it.

For a list of available command line arguments, open the help via
```./indprog.py -h```
