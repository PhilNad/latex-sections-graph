# LaTeX Sections Graph
Reads a LaTeX file (.tex), parse it using [LatexWalker](https://pylatexenc.readthedocs.io/en/latest/latexwalker/), and create a graph of elements using [NetworkX](https://networkx.org/documentation/stable/index.html) in which each node represents a LaTeX section and each edge represents a LaTeX reference that links two sections.

The graph is a directed graph, and the edges are directed from the section that contains the reference to the section that
is being referenced.

The typical use of this script is to map the main concepts introduced in a LaTeX document such that it is easier to understand inter-dependencies between concepts.

# Dependencies
- Python 3.x
- LatexWalker
- NetworkX
- Matplotlib

# Usage
```python
from latexSectionsGraph import *
parser = LatexSectionsGraph('example.tex', use_subsubsection=True, use_subsection=True, node_threshold=1)
parser.visualize_graph()
```