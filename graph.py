import networkx as nx
import matplotlib.pyplot as plt




class Graph:
    def __init__(self, vertices=None, edges=None, labels=None):
        self.nx_graph = nx.DiGraph()
        self.labels = {}

        if vertices is not None:
            for v in vertices:
                self.nx_graph.add_node(v)

        if edges is not None:
            for u, v in edges:
                self.nx_graph.add_edge(u, v)

        if labels is not None:
            self.labels.update(labels)
        if self.labels:
            nx.set_node_attributes(self.nx_graph, self.labels, name="label")

    @classmethod
    def from_csv(cls, filepath: str):
        vertices = []
        edges = []
        labels = {}
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return cls()

        # ilość wierzchołków
        first_line = lines[0].split(',')
        try:
            count = int(first_line[0].strip())
        except ValueError:
            count = None

        if count is not None:
            vertices = list(range(1, count+1))

            # na razie etykiety w pierwszej linii 3, yellow, orange, blue
            # TODO: trzebaby to lepiej zrobić
            if len(first_line) > 1:
                labels_list = [x.strip() for x in first_line[1:]]
                if len(labels_list) == count:
                    for i, lab in enumerate(labels_list, start=1):
                        labels[i] = lab

        # w reszcie linii krawędzie
        for line in (lines[1:] if count is not None else lines):
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    u = int(parts[0].strip())
                    v = int(parts[1].strip())
                except ValueError:
                    continue  # jest jakiś syf zamiast dwóch liczb
                edges.append((u, v))
                # TODO: trzebaby dodać że następne częsci linii to etykiety, np 3, 1, red (3->1 etykieta= red)
        return cls(vertices=vertices, edges=edges, labels=(labels if labels else None))

    def nodes(self):
        return list(self.nx_graph.nodes())

    def edges(self):
        return list(self.nx_graph.edges())

    def has_edge(self, u, v) -> bool:
        return self.nx_graph.has_edge(u, v)

    def add_node(self, node, label=None):
        self.nx_graph.add_node(node)
        if label:
            self.labels[node] = label
            nx.set_node_attributes(self.nx_graph, {node: label}, name="label")

    def add_edge(self, u, v):
        self.nx_graph.add_edge(u, v)

    def remove_node(self, node):
        self.nx_graph.remove_node(node)
        if node in self.labels:
            del self.labels[node]

    def remove_edge(self, u, v):
        self.nx_graph.remove_edge(u, v)

    def get_labels(self, node):
        return self.labels.get(node)

    def set_label(self, node, label: str):
        self.labels[node] = label
        nx.set_node_attributes(self.nx_graph, {node: label}, name="label")

    def draw(self, title: str = None):
        pos = nx.spring_layout(self.nx_graph, seed=42)
        labels_to_draw = {}
        if self.labels:
            for node in self.nx_graph.nodes():
                if node in self.labels:
                    labels_to_draw[node] = f"{node}:{self.labels[node]}"
                else:
                    labels_to_draw[node] = str(node)
        else:
            labels_to_draw = {node: str(node) for node in self.nx_graph.nodes()}
        nx.draw(self.nx_graph, pos, with_labels=True, labels=labels_to_draw, arrows=True,
                node_color='#99ccff', node_size=500, font_size=8)
        if title:
            plt.title(title)
        plt.axis('off')
