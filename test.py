from latexSectionsGraph import *

parser = LatexSectionsGraph('example.tex', use_subsubsection=True, use_subsection=True, node_threshold=1)
parser.visualize_graph()