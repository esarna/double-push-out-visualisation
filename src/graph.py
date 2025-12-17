import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    def __init__(self, vertices=None, edges=None, vertex_labels=None, edge_labels=None, vertex_idx=None, edge_idx=None, pos=None):
        self.nx_graph = nx.DiGraph()
        self.vertex_labels = {}
        self.vertex_idx = {}
        self.edge_labels = {}
        self.edge_idx = {}
        self.pos = {}

        if vertices is not None:
            for v in vertices:
                self.nx_graph.add_node(v)

        if edges is not None:
            for u, v in edges:
                self.nx_graph.add_edge(u, v)

        if vertex_labels is not None:
            self.vertex_labels.update(vertex_labels)
        if self.vertex_labels:
            nx.set_node_attributes(
                self.nx_graph, self.vertex_labels, name="label")

        if edge_labels is not None:
            self.edge_labels.update(edge_labels)
        if self.edge_labels:
            nx.set_edge_attributes(
                self.nx_graph, self.edge_labels, name="label")

        if vertex_idx is not None:
            self.vertex_idx.update(vertex_idx)
        if self.vertex_idx:
            nx.set_node_attributes(
                self.nx_graph, self.vertex_idx, name="index")

        if edge_idx is not None:
            self.edge_idx.update(edge_idx)
        if self.edge_idx:
            nx.set_edge_attributes(
                self.nx_graph, self.edge_idx, name="index")

        if pos is not None:
            self.pos = pos
        else:
            self.pos = nx.spring_layout(self.nx_graph)

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
        return cls(vertices=vertices, edges=edges, vertex_labels=(labels if labels else None))

    @classmethod
    def from_obj(cls, filepath: str):
        vertices = []
        edges = []
        v_labels = {}
        e_labels = {}
        e_idx = {}
        v_idx = {}
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return cls()
        for line in lines:
            line = line.strip()
            first_char = line[0]
            if first_char == 'v':
                labels = line[1:].strip().split()
                idx = labels[0]
                labels = labels[1:]
                if idx or idx.strip() == "":
                    idx = f'{len(vertices) + 1}'
                try:
                    idx = int(idx.strip())
                except ValueError:
                    print(f'[WARN] Expected number in line:\n\t{line}')
                    continue
                v_idx[idx] = idx

                node_id = len(vertices) + 1
                vertices.append(node_id)
                if labels:
                    v_labels[node_id] = labels
                else:
                    v_labels[node_id] = []
            elif first_char == 'e':
                parts = line[1:].strip().split()
                if len(parts) >= 2:
                    try:
                        u = int(parts[0].strip())
                        v = int(parts[1].strip())
                        i = int(parts[2].strip()) if len(parts) >= 3 else None
                    except ValueError:
                        print(f'[WARN] Expected numbers in line:\n\t{line}')
                        continue
                    if i is None:
                        i = len(edges) + 1
                    e_idx[(u, v)] = i
                    label = None
                    if len(parts) >= 4:
                        e_labels[(u, v)] = parts[3:]
                    edges.append((u, v))
        return cls(
            vertices=vertices,
            edges=edges,
            vertex_labels=(v_labels if v_labels else None),
            edge_labels=(e_labels if e_labels else None),
            vertex_idx=(v_idx if v_idx else None),
            edge_idx=(e_idx if e_idx else None)
        )

    def nodes(self):
        return list(self.nx_graph.nodes())

    def edges(self):
        return list(self.nx_graph.edges())

    def has_edge(self, u, v) -> bool:
        return self.nx_graph.has_edge(u, v)

    def add_node(self, node, index=None, label=None):
        # wygląda że działa
        oldVertexes = list(self.nx_graph.nodes())
        self.nx_graph.add_node(node)
        if label:
            self.vertex_labels[node] = label
            nx.set_node_attributes(self.nx_graph, {node: label}, name="label")
        if index:
            self.vertex_idx[node] = index
            nx.set_node_attributes(
                self.nx_graph, {node: index}, name="index")

        self.pos[node] = (0, 0)
        self.pos = nx.spring_layout(
            self.nx_graph, pos=self.pos, fixed=oldVertexes)
        # spring layout oblicza pozycje wieszchołków ale mozna mu powiedzeć których ma nie ruszać wiec w ten sposób licze pozycje nowego

    def add_edge(self, u, v, index=None, label=None):
        self.nx_graph.add_edge(u, v)
        if label:
            self.edge_labels[u][v] = label
            nx.set_node_attributes(
                self.nx_graph, {(u, v): label}, name="label")
        if index:
            self.edge_idx[(u, v)] = index
            nx.set_edge_attributes(
                self.nx_graph, {(u, v): index}, name="index")

    def remove_node(self, node):
        self.nx_graph.remove_node(node)
        if node in self.vertex_labels:
            del self.vertex_labels[node]
            del self.vertex_idx[node]
        self.pos.pop(node)

    def remove_edge(self, u, v):
        self.nx_graph.remove_edge(u, v)
        if (u, v) in self.edge_labels:
            del self.edge_labels[(u, v)]
            del self.edge_idx[(u, v)]

    def get_labels(self, node):
        return self.vertex_labels.get(node)

    def set_label(self, node, label: str):
        self.vertex_labels[node] = label
        nx.set_node_attributes(self.nx_graph, {node: label}, name="label")

    def get_idx(self, node):
        return self.vertex_idx.get(node)

    def set_idx(self, node, index):
        self.vertex_idx[node] = index
        nx.set_node_attributes(self.nx_graph, {node: index}, name="index")

    def draw(self, title: str | None = None, offset=(0, 0), color='#99ccff', ax=None):
        pos = {k: [self.pos[k][0] + offset[0], self.pos[k][1] + offset[1]]
               for k in self.pos.keys()}

        # indeksy
        node_indices = {}
        for node in self.nx_graph.nodes():
            idx = self.vertex_idx.get(node)
            node_indices[node] = str(idx) if idx is not None else str(node)

        nx.draw_networkx_nodes(self.nx_graph, pos, node_color=color, node_size=300, ax=ax)
        nx.draw_networkx_labels(self.nx_graph, pos, labels=node_indices, font_size=9, ax=ax)

        # krawędzie
        nx.draw_networkx_edges(self.nx_graph, pos, arrows=True, ax=ax)

        # wierzchołki - etykiety w ramkach
        if self.vertex_labels:
            for node, (x, y) in pos.items():
                lbl = self.vertex_labels.get(node)
                if lbl:
                    # Rysowanie tekstu z ramką (bbox)
                    plt.text(x, y + 0.12, s=str(lbl),
                             bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.2', alpha=0.8),
                             horizontalalignment='center', fontsize=8, color='black', zorder=10)

        # krawędzie - indeksy i etykiety w ramkach
        edge_indices_to_draw = {}
        for u, v in self.nx_graph.edges():

            e_idx = self.edge_idx.get((u, v))
            if e_idx is not None:
                edge_indices_to_draw[(u, v)] = f"[{e_idx}]"

            e_lbl = self.edge_labels.get((u, v))
            if e_lbl:
                (x0, y0) = pos[u]
                (x1, y1) = pos[v]

                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2

                plt.text(mid_x, mid_y + 0.08, s=str(e_lbl),
                         bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.2', alpha=0.8),
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=7, color='black', zorder=15)


        if edge_indices_to_draw:
            nx.draw_networkx_edge_labels(
                self.nx_graph, pos,
                edge_labels=edge_indices_to_draw,
                font_size=8,
                # Tło dla indeksu: przezroczyste lub lekko białe, bez ramki
                bbox=dict(facecolor='white', edgecolor='none', alpha=1.0),
                ax=ax
            )

        # ewentualny tytuł
        if title:
            xs = [p[0] for p in pos.values()]
            if xs:
                center_x = sum(xs) / len(xs)
                max_y = max([p[1] for p in pos.values()])
                plt.text(center_x, max_y + 0.4, title, fontsize=12, fontweight='bold', ha='center')

        plt.axis('off')
        return pos
