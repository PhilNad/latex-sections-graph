from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt


class LatexSectionsGraph:
    """
    This class defines a parser that reads a LaTeX file (.tex), parse it using LatexWalker, and create a graph of elements
    in which each node represents a LaTeX section and each edge represents a LaTeX reference that links two sections.

    The graph is a directed graph, and the edges are directed from the section that contains the reference to the section that
    is being referenced.

    file_path: The path to the LaTeX file to parse.
    use_subsubsection: If True, then the graph will contain edges between subsubsections. Otherwise,
        when referring to a subsubsection, the edge will point to the subsection it belongs to.
    use_subsection: If True, then the graph will contain edges between subsections. Otherwise,
        when referring to a subsection, the edge will point to the section it belongs to.
    node_threshold: The minimum number of edges a node must have to be kept in the graph. Nodes with less than this number
        of edges will be removed from the graph.
    """

    def __init__(
        self, file_path, use_subsubsection=False, use_subsection=True, node_threshold=2
    ):
        self.verify_tex_path(file_path)
        self.file_path = file_path
        self.parse_tex_file()
        # Instantiate a directed graph.
        self.graph = nx.DiGraph()
        # Add nodes and edges to the graph without using subsubsections.
        label_section_map = self.add_nodes(use_subsubsection, use_subsection)
        self.add_edges(label_section_map, use_subsubsection, use_subsection)
        # Remove nodes that have less than 2 edges.
        self.remove_lightly_connected_nodes(node_threshold)

    def verify_tex_path(self, file_path):
        """
        Verify that the file path exists and is a .tex file.
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File {file_path} not found.")
        if not Path(file_path).suffix == ".tex":
            raise ValueError(f"File {file_path} is not a .tex file.")

    def parse_tex_file(self):
        """
        Parse the LaTeX file using LatexWalker.
        """
        self.file_content = self.read_file_content(Path(self.file_path))
        self.soup = LatexWalker(self.file_content)

    def read_file_content(self, file_path: Path):
        """
        If the Path provided resolves to an existing LaTeX file, read its content and return it as a string.
        """
        if file_path.exists():
            with open(file_path.absolute().as_posix()) as f:
                return f.read()

    def visualize_graph(self):
        """
        Visualize the graph in a shell layout using Matplotlib.
        The size of each node is proportional to the number of edges it has, and  the edges are blue while the nodes are red.
        The labels are displayed in white.
        """
        # pos = nx.spring_layout(self.graph, k=10, iterations=1500)
        pos = nx.shell_layout(self.graph)
        # pos = nx.circular_layout(self.graph, scale=10)
        # pos = nx.kamada_kawai_layout(self.graph, scale=3)
        nodesize = [500 * len(self.graph.in_edges(node)) for node in self.graph.nodes()]
        nx.draw_networkx_edges(
            self.graph,
            pos,
            alpha=1,
            width=3,
            edge_color="b",
            arrowsize=20,
            arrowstyle="->",
        )
        nx.draw_networkx_nodes(
            self.graph, pos, node_size=nodesize, node_color="#ff0000", alpha=0.5
        )
        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
        nx.draw_networkx_labels(self.graph, pos, font_size=14, bbox=label_options)
        plt.show()

    def remove_lightly_connected_nodes(self, threshold=1):
        """
        Remove nodes that have less than threshold edges.
        """
        remove = [node for node, degree in self.graph.degree() if degree < threshold]
        self.graph.remove_nodes_from(remove)

    def add_nodes(self, use_subsubsection=False, use_subsection=True):
        """
        Traverse the LatexWalker tree and find all section, subsection, subsubsection, label, and reference elements.
        When a label is found, the preceding section, subsection, or subsubsection is added as a node in the graph.

        If use_subsubsection is True, then the graph will contain edges between subsubsections. Otherwise,
        when referring to a subsubsection, the edge will point to the subsection it belongs to.
        """
        s = self.soup
        (nodelist, pos, len_) = s.get_latex_nodes(pos=0)

        # Keep track of the previous section, subsection, and subsubsection
        # such that the label can refer to the immediately preceding section.
        prev_section = None
        prev_subsection = None
        prev_subsubsection = None

        # Maps label names to the section, subsection, or subsubsection they refer to.
        # That ways, a reference can be resolved to the section, subsection, or subsubsection it refers to.
        label_section_map = {}

        # Traverse the tree in a depth-first manner.
        for node in nodelist:
            if node.isNodeType(LatexEnvironmentNode):
                if node.environmentname == "document":
                    nodelist = node.nodelist
                    for node in nodelist:
                        if node.isNodeType(LatexEnvironmentNode):
                            if (
                                node.environmentname == "equation"
                                or node.environmentname == "align"
                            ):
                                for sub_node in node.nodelist:
                                    if sub_node.isNodeType(LatexMacroNode):
                                        if sub_node.macroname == "label":
                                            label_name = (
                                                sub_node.nodeargs[0].nodelist[0].chars
                                            )
                                            if prev_subsubsection and use_subsubsection:
                                                label_section_map[label_name] = (
                                                    prev_subsubsection
                                                )
                                            elif prev_subsection and use_subsection:
                                                label_section_map[label_name] = (
                                                    prev_subsection
                                                )
                                            elif prev_section:
                                                label_section_map[label_name] = (
                                                    prev_section
                                                )
                        if node.isNodeType(LatexMacroNode):
                            if node.macroname == "section":
                                prev_section = node.nodeargs[0].nodelist[0].chars
                                prev_subsection = None
                                prev_subsubsection = None
                            if node.macroname == "subsection":
                                prev_subsection = node.nodeargs[0].nodelist[0].chars
                                prev_subsubsection = None
                            if node.macroname == "subsubsection":
                                prev_subsubsection = node.nodeargs[0].nodelist[0].chars
                            if node.macroname == "label":
                                label_name = node.nodeargs[0].nodelist[0].chars
                                if prev_subsubsection and use_subsubsection:
                                    label_section_map[label_name] = prev_subsubsection
                                elif prev_subsection and use_subsection:
                                    label_section_map[label_name] = prev_subsection
                                elif prev_section:
                                    label_section_map[label_name] = prev_section
        return label_section_map

    def add_edges(
        self, label_section_map, use_subsubsection=False, use_subsection=True
    ):
        """
        Traverse the LatexWalker tree and find all section, subsection, subsubsection, label, and reference elements.
        When a reference is found, the reference is added as an edge in the graph.

        The label_section_map maps label names to the section, subsection, or subsubsection they refer to.
        That way, a reference can be resolved to the section, subsection, or subsubsection it refers to.

        If use_subsubsection is True, then the graph will contain edges between subsubsections. Otherwise,
        when referring to a subsubsection, the edge will point to the subsection it belongs to.
        """
        s = self.soup
        (nodelist, pos, len_) = s.get_latex_nodes(pos=0)

        # Keep track of the previous section, subsection, and subsubsection
        # such that the label can refer to the immediately preceding section.
        prev_section = None
        prev_subsection = None
        prev_subsubsection = None

        for node in nodelist:
            if node.isNodeType(LatexEnvironmentNode):
                if node.environmentname == "document":
                    nodelist = node.nodelist
                    for node in nodelist:
                        if node.isNodeType(LatexMacroNode):
                            if node.macroname == "section":
                                prev_section = node.nodeargs[0].nodelist[0].chars
                                prev_subsection = None
                                prev_subsubsection = None
                            if node.macroname == "subsection" and use_subsection:
                                prev_subsection = node.nodeargs[0].nodelist[0].chars
                                prev_subsubsection = None
                            if node.macroname == "subsubsection" and use_subsubsection:
                                prev_subsubsection = node.nodeargs[0].nodelist[0].chars
                            if (
                                node.macroname == "Cref"
                                or node.macroname == "cref"
                                or node.macroname == "ref"
                                or node.macroname == "eqref"
                                or node.macroname == "autoref"
                                or node.macroname == "nameref"
                            ):
                                label_name = node.nodeargs[0].nodelist[0].chars
                                if label_name in label_section_map:
                                    if prev_subsubsection:
                                        if (
                                            prev_subsubsection
                                            != label_section_map[label_name]
                                        ):
                                            self.graph.add_edge(
                                                label_section_map[label_name],
                                                prev_subsubsection,
                                            )
                                    elif prev_subsection:
                                        if (
                                            prev_subsection
                                            != label_section_map[label_name]
                                        ):
                                            self.graph.add_edge(
                                                label_section_map[label_name],
                                                prev_subsection,
                                            )
                                    elif prev_section:
                                        if (
                                            prev_section
                                            != label_section_map[label_name]
                                        ):
                                            self.graph.add_edge(
                                                label_section_map[label_name],
                                                prev_section,
                                            )

    def export_tikz(
        self,
        out_path: str = "concept_map.tikz",
        layout: str = "shell",  # "shell", "spring", or "circular"
        scale: float = 10.0,  # global scaling factor for coordinates
        standalone: bool = False,  # wrap in full LaTeX document?
    ) -> str:
        """
        Write a TikZ version of the concept‑map to *out_path* and return the same
        string.  The picture keeps the same relative geometry as the Matplotlib
        preview.

        Parameters
        ----------
        out_path   : Destination file.  If None, nothing is written to disk.
        layout     : 'shell' (default), 'spring', or 'circular'.
        scale      : Multiplier that turns layout‑unit coordinates into cm.
        standalone : If True, wrap the \\tikzpicture in a minimal standalone
                     document so it can be compiled directly with (pdf)latex.
                     If False you can simply \\input{} the file.
        """
        output_path = Path(out_path).resolve().as_posix()

        # 1) Choose a layout identical to the one used in `visualize_graph`
        if layout == "shell":
            pos = nx.shell_layout(self.graph)
        elif layout == "spring":
            pos = nx.spring_layout(self.graph, k=10, iterations=1500)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph, scale=3)
        else:
            raise ValueError(f"Unknown layout '{layout}'")

        # 2) Shift everything into the first quadrant and scale to cm
        xs, ys = zip(*pos.values())
        min_x, min_y = min(xs), min(ys)
        for n, (x, y) in pos.items():
            pos[n] = ((x - min_x) * scale, (y - min_y) * scale)

        # 3) Helper to build valid node names and readable labels
        def _node_key(i: int) -> str:  # internal TikZ name
            return f"n{i}"

        def _escape(s: str) -> str:  # human‑readable label
            return s.replace("_", r"\_").replace("%", r"\%")

        tikz_lines = []
        if standalone:
            tikz_lines += [
                r"\documentclass{standalone}",
                r"\usepackage{tikz}",
                r"\begin{document}",
            ]

        tikz_lines += [r"\begin{tikzpicture}[>=stealth,shorten >=1pt]"]

        # 4) TikZ nodes (size ≈ in‑degree, like in Matplotlib preview)
        node_id = {}
        for i, node in enumerate(self.graph.nodes()):
            node_id[node] = _node_key(i)
            x, y = pos[node]
            deg = max(1, self.graph.in_degree(node))  # avoid zero
            size = 4 + 1.5 * deg  # pt → TikZ 'minimum size'
            tikz_lines.append(
                rf"  \node[circle,draw=red!70,fill=red!30,inner sep=2pt,"
                rf"minimum size={size}pt] ({node_id[node]}) at ({x:.2f}cm,{y:.2f}cm)"
                rf" {{{_escape(node)}}};"
            )

        # 5) Directed edges
        for src, dst in self.graph.edges():
            tikz_lines.append(
                rf"  \draw[->,thick,blue] ({node_id[src]}) -- ({node_id[dst]});"
            )

        tikz_lines += [r"\end{tikzpicture}"]
        if standalone:
            tikz_lines += [r"\end{document}"]

        tikz_code = "\n".join(tikz_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(tikz_code)

        return tikz_code


if __name__ == "__main__":
    parser = LatexSectionsGraph(
        "example.tex",
        use_subsubsection=True,
        use_subsection=True,
        node_threshold=1,
    )
    parser.visualize_graph()
    parser.export_tikz(
        out_path="./concept_map.tikz",  # will be written beside your .tex source
        layout="shell",  # same default as visualize_graph()
        scale=10.0,  # 10 layout‑units → 10 cm
        standalone=False,  # produce only the \tikzpicture block
    )
