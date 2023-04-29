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
Executing the following code (taken from `test.py`):
```python
from latexSectionsGraph import *
parser = LatexSectionsGraph('example.tex', use_subsubsection=True,\
    use_subsection=True, node_threshold=1)
parser.visualize_graph()
```
which parse `example.tex` with content
```latex
\documentclass[letterpaper]{article}
\usepackage{cleveref}

\begin{document}

\section{First}
\label{sec:first}
\subsection{First sub}
\label{sec:first_sub_first}
\subsection{Second sub}
\label{sec:first_sub_second}
Reference to the first subsection \cref{sec:first_sub_first}.

\section{Second}
\label{sec:second}
Reference to the first section \cref{sec:first}. 
Reference to the first subsection \cref{sec:first_sub_first}. 
Reference to the second subsection \cref{sec:first_sub_second}.

\section{Third}
\label{sec:third}
Reference to the second section \cref{sec:second}.

\end{document}
```
will produce the following output in a window:
![output concept graph](https://github.com/PhilNad/latex-sections-graph/blob/main/test_output.png?raw=true)