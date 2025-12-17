from .graph import Graph
import networkx as nx


class Production:
    def __init__(self, left: Graph, right: Graph):
        self.L = left
        self.R = right

    # Obliczenie grafu sklejającego
    def compute_interface(self) -> Graph:
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        K_nodes = L_nodes.intersection(R_nodes)
        L_edges = set(self.L.edges())
        R_edges = set(self.R.edges())

        # Krawędzie wspólne w L i R
        K_edges = [(u, v) for (u, v) in L_edges.intersection(
            R_edges) if u in K_nodes and v in K_nodes]
        K_graph = Graph(vertices=list(K_nodes), edges=K_edges)

        for node in K_graph.nodes():
            label = self.L.get_labels(node)
            if label is not None:
                K_graph.set_label(node, label)
        return K_graph

    # zastosowanie produkcji
    def apply(self, input: Graph, mapping: list[int]) -> Graph:

        # kopia wejścia
        G = input
        output = Graph(vertices=G.nodes(), edges=G.edges())

        for node in G.nodes():
            lbl = G.get_labels(node)
            if lbl is not None:
                output.set_label(node, lbl)

        # TODO: nie wiem czy mapowianie się dobrze wczytuje i stosuje
        # Mapowanie wierzchołków L->G
        L_nodes_sorted = sorted(self.L.nodes())

        # Sprawdzanie produkcji
        if len(mapping) != len(L_nodes_sorted):
            raise Exception(
                "Niepoprawna liczba wierzchołków w odwzorowaniu dla grafu L.")

        mapping_dict = {Lnode: Gnode for Lnode,
                        Gnode in zip(L_nodes_sorted, mapping)}

        if len(set(mapping_dict.values())) != len(mapping_dict):
            raise Exception(
                "Odwzorowanie nie jest injektywne – różne węzły L odwzorowano na ten sam węzeł grafu G.")

        for (u, v) in self.L.edges():
            uG = mapping_dict[u]
            vG = mapping_dict[v]
            if not output.has_edge(uG, vG):
                raise Exception(
                    f"Brak wymaganej krawędzi ({u}->{v}) z L w grafie początkowym (oczekiwano {uG}->{vG}).")

        # Węzły
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        to_remove_L = L_nodes - R_nodes     # węzły które zostaną usunięte
        # odpowiadające im węzły w G
        to_remove_G = {mapping_dict[Ln] for Ln in to_remove_L}

        #  mapping w drugą stronę
        inv_map = {Gv: Lv for Lv, Gv in mapping_dict.items()}

        # sprawdzenie warunku wiszących krawędzi
        for gnode in to_remove_G:

            # krawędzie wychodzące z gnode
            for succ in list(G.nx_graph.successors(gnode)):

                # jeśli succ pozostaje w wyniku
                if succ not in to_remove_G:
                    if succ not in inv_map:
                        raise Exception(
                            f"Naruszenie warunku wiszącej krawędzi: wierzchołek {gnode} (do usunięcia) ma krawędź do {succ}, który nie jest objęty dopasowaniem.")
                    else:
                        # succ jest w G, jest obrazem jakiegoś węzła z L
                        Lnode_removed = inv_map[gnode]
                        Lnode_other = inv_map[succ]

                        if not self.L.has_edge(Lnode_removed, Lnode_other):
                            raise Exception(
                                f"Naruszenie warunku wiszącej krawędzi: krawędź {Lnode_removed}->{Lnode_other} łączy usuwany i zachowany węzeł w G, ale nie istnieje w L.")

            # krawędzie wchodzące do gnode
            for pred in list(G.nx_graph.predecessors(gnode)):
                if pred not in to_remove_G:
                    inv_map = {Gv: Lv for Lv, Gv in mapping_dict.items()}
                    if pred not in inv_map:
                        raise Exception(
                            f"Naruszenie warunku wiszącej krawędzi: wierzchołek {gnode} (do usunięcia) ma krawędź od {pred}, który nie jest objęty dopasowaniem.")
                    else:
                        Lnode_removed = inv_map[gnode]
                        Lnode_other = inv_map[pred]
                        if not self.L.has_edge(Lnode_other, Lnode_removed):
                            raise Exception(
                                f"Naruszenie warunku wiszącej krawędzi: krawędź {Lnode_other}->{Lnode_removed} łączy zachowany i usuwany węzeł w G, ale nie istnieje w L.")

        # Usunięcie węzłów i krawędzi do usunięcia
        for node in to_remove_G:
            output.remove_node(node)

        L_edges = set(self.L.edges())
        R_edges = set(self.R.edges())

        preserved_L = L_nodes.intersection(R_nodes)  # węzły zachowane
        for (u, v) in L_edges:
            if u in preserved_L and v in preserved_L and (u, v) not in R_edges:
                uG, vG = mapping_dict[u], mapping_dict[v]
                if output.has_edge(uG, vG):
                    output.remove_edge(uG, vG)

        # dodanie nowych węzłów
        new_R_nodes = R_nodes - L_nodes
        new_node_map = {}  # mapowanie: R -> output

        next_id = max(output.nodes())+1 if output.nodes() else 1
        for Rnode in sorted(new_R_nodes):
            new_id = next_id
            next_id += 1
            output.add_node(new_id)
            new_node_map[Rnode] = new_id
            lbl = self.R.get_labels(Rnode)
            if lbl is not None:
                output.set_label(new_id, lbl)

        # dodanie nowych krawędzi
        for (u, v) in self.R.edges():
            u_out = mapping_dict.get(
                u) if u in L_nodes else new_node_map.get(u)
            v_out = mapping_dict.get(
                v) if v in L_nodes else new_node_map.get(v)
            if u_out is None or v_out is None:
                continue
            if output.has_edge(u_out, v_out):
                continue  # jeśli krawędź już istnieje
            output.add_edge(u_out, v_out)

        return output

    def draw(self, title: str | None = None):
        pos = self.L.draw(title=title)
        max_x = 0
        for key in pos:
            if pos[key][0] > max_x:
                max_x = pos[key][0]
        offset = (max_x * 2, 0)
        self.R.draw(title=title, offset=offset)
