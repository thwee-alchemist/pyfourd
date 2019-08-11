# PyFourD
## A Small Dynamic Force Directed Graph Visualization

This won't support many nodes yet, but it displays simple shapes. 

### Prerequisites

* Install JupyterLab: https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html
* Enable jupyter-threejs: https://github.com/jupyter-widgets/pythreejs

### Installation

* git clone https://code.joshuamoore.dev/me/pyfourd.git
* Open Unititled.ipynb

### Usage


```py
from pyfourd import FourD

fourd = FourD()
fourd.start()

# creation
v0 = fourd.graph.add_vertex(0)
v1 = fourd.graph.add_vertex(1)

e = fourd.graph.add_edge(0, v0, v1)


# cleanup
fourd.graph.remove_edge(e)

fourd.graph.remove_vertex(v0)
fourd.graph.remove_vertex(v1)
```

The add_vertex function accepts the following keyword arguments:

* color = an HTML Color, eg. green, black, blue
* size = a value greater than 1.0. I use 0.5

The add_edge function accepts the following keyword arguments:

* strength = a value around 1.0
* color = an HTML color
