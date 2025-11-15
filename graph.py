import networkx as nx

class Graph:
    """Reprezentacja grafu skierowanego z opcjonalnymi etykietami wierzchołków."""
    def __init__(self, vertices=None, edges=None, labels=None):
        # Inicjalizacja grafu jako skierowanego
        self.nx_graph = nx.DiGraph()
        self.labels = {}  # słownik etykiet wierzchołków (opcjonalnie)
        # Dodaj wierzchołki
        if vertices is not None:
            for v in vertices:
                self.nx_graph.add_node(v)
        # Dodaj krawędzie
        if edges is not None:
            for u, v in edges:
                self.nx_graph.add_edge(u, v)
        # Dodaj etykiety wierzchołków (jeśli podano)
        if labels is not None:
            self.labels.update(labels)
        if self.labels:
            nx.set_node_attributes(self.nx_graph, self.labels, name="label")

    @classmethod
    def from_csv(cls, filepath: str):
        """Wczytuje graf z pliku CSV.
        Format pliku:
        - Pierwsza linia: liczba wierzchołków (opcjonalnie po przecinku etykiety tych wierzchołków).
        - Kolejne linie: pary "u,v" oznaczające krawędź skierowaną z u do v (opcjonalnie trzecia kolumna jako etykieta krawędzi - ignorowana w tej implementacji)."""
        vertices = []
        edges = []
        labels = {}
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return cls()
        # Pierwsza linia
        first_line = lines[0].split(',')
        try:
            count = int(first_line[0].strip())
        except ValueError:
            count = None
        if count is not None:
            # Jeśli podano liczbę wierzchołków, dodajemy je jako 1..count
            vertices = list(range(1, count+1))
            # Sprawdź, czy po liczbie wierzchołków podano ich etykiety
            if len(first_line) > 1:
                labels_list = [x.strip() for x in first_line[1:]]
                if len(labels_list) == count:
                    # Przypisz etykiety do kolejnych wierzchołków
                    for i, lab in enumerate(labels_list, start=1):
                        labels[i] = lab
        # Przetwarzanie linii z krawędziami
        for line in (lines[1:] if count is not None else lines):
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    u = int(parts[0].strip())
                    v = int(parts[1].strip())
                except ValueError:
                    continue  # pomiń linie, które nie zawierają poprawnych liczb
                edges.append((u, v))
                # (Ignorujemy ewentualną trzecią kolumnę z etykietą krawędzi)
        return cls(vertices=vertices, edges=edges, labels=(labels if labels else None))

    def nodes(self):
        """Zwraca listę wierzchołków grafu."""
        return list(self.nx_graph.nodes())

    def edges(self):
        """Zwraca listę krawędzi grafu jako pary (u, v)."""
        return list(self.nx_graph.edges())

    def has_edge(self, u, v) -> bool:
        """Sprawdza, czy graf zawiera krawędź z u do v."""
        return self.nx_graph.has_edge(u, v)

    def add_node(self, node, label=None):
        """Dodaje wierzchołek do grafu (z opcjonalną etykietą)."""
        self.nx_graph.add_node(node)
        if label:
            self.labels[node] = label
            nx.set_node_attributes(self.nx_graph, {node: label}, name="label")

    def add_edge(self, u, v):
        """Dodaje krawędź skierowaną z u do v."""
        self.nx_graph.add_edge(u, v)

    def remove_node(self, node):
        """Usuwa wierzchołek (oraz wszystkie incydentne krawędzie) z grafu."""
        self.nx_graph.remove_node(node)
        if node in self.labels:
            del self.labels[node]

    def remove_edge(self, u, v):
        """Usuwa krawędź z u do v z grafu."""
        self.nx_graph.remove_edge(u, v)

    def get_label(self, node):
        """Zwraca etykietę wierzchołka (jeśli ustawiona)."""
        return self.labels.get(node)

    def set_label(self, node, label: str):
        """Ustawia etykietę dla danego wierzchołka."""
        self.labels[node] = label
        nx.set_node_attributes(self.nx_graph, {node: label}, name="label")

    def draw(self, title: str = None):
        """Wyświetla graf za pomocą matplotlib (networkx)."""
        import matplotlib.pyplot as plt
        # Użyj layoutu spring dla czytelnego rozmieszczenia wierzchołków
        pos = nx.spring_layout(self.nx_graph, seed=42)
        # Przygotuj etykiety do wyświetlenia: jeżeli są etykiety, pokazujemy "id:etykieta"
        labels_to_draw = {}
        if self.labels:
            for node in self.nx_graph.nodes():
                if node in self.labels:
                    labels_to_draw[node] = f"{node}:{self.labels[node]}"
                else:
                    labels_to_draw[node] = str(node)
        else:
            labels_to_draw = {node: str(node) for node in self.nx_graph.nodes()}
        # Rysuj wierzchołki i krawędzie
        nx.draw(self.nx_graph, pos, with_labels=True, labels=labels_to_draw, arrows=True,
                node_color='#99ccff', node_size=500, font_size=8)
        if title:
            plt.title(title)
        plt.axis('off')
