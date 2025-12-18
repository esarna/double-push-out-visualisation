from matplotlib import pyplot as plt
import numpy as np
from .graph import Graph


class Production:
    def __init__(self, left: Graph, right: Graph):
        self.L = left
        self.R = right
        self.K = None
        self.compute_K_graph()

    # Obliczenie grafu sklejającego
    def compute_K_graph(self) -> Graph:
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        K_nodes = L_nodes.intersection(R_nodes)
        L_edges = set(self.L.edges())
        R_edges = set(self.R.edges())

        # Krawędzie wspólne w L i R
        K_edges = [(u, v) for (u, v) in L_edges.intersection(
            R_edges) if u in K_nodes and v in K_nodes]
        K_graph = Graph(vertices=list(K_nodes), edges=K_edges, pos=self.L.pos)

        for node in K_graph.nodes():
            label = self.L.get_labels(node)
            if label is not None:
                K_graph.set_label(node, label)

            self.K = K_graph
        return K_graph

    # zastosowanie produkcji
    def apply(self, input: Graph, mapping: list[int], transform_positions: bool = False) -> Graph:

        # kopia wejścia
        G = input
        output = Graph(vertices=G.nodes(), edges=G.edges(), pos=G.pos.copy())

        for node in G.nodes():
            lbl = G.get_labels(node)
            if lbl is not None:
                output.set_label(node, lbl)

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

        if transform_positions:
            self.update_positions(input, output, mapping)

        return output

    def draw(self, title: str | None = None):

        plt.figure(figsize=(14, 6))

        # kolorki
        color_L = '#D44C33'
        color_K = '#E0BA28'
        color_R = '#6EB52D'

        pos_L = self.L.draw(title="L (Lewy)", color=color_L)
        if pos_L:
            max_x_L = max(p[0] for p in pos_L.values())
            min_x_L = min(p[0] for p in pos_L.values())
            width_L = max_x_L - min_x_L
            offset_K = (max_x_L + 1.5, 0)
        else:
            offset_K = (0, 0)


        pos_K = self.K.draw(title="K (Sklejający)", offset=offset_K, color=color_K)
        if pos_K:
            max_x_K = max(p[0] for p in pos_K.values())
            offset_R = (max_x_K + 1.5, 0)
        else:
            offset_R = (offset_K[0] + 2, 0)


        self.R.draw(title="R (Prawy)", offset=offset_R, color=color_R)

        # tytuł
        if title:
            plt.suptitle(title, fontsize=16)

        plt.tight_layout()
        plt.show()


    def update_positions(self, input_graph: Graph, output_graph: Graph, mapping: list[int]):
        """
        Oblicza pozycje nowych wierzchołków w output_graph stosując transformację afiniczną.
        """

        # 1. Odtworzenie mapowania (L -> G)
        L_nodes_sorted = sorted(self.L.nodes())
        if len(mapping) != len(L_nodes_sorted):
            print("[ERROR] Długość mapowania nie zgadza się z liczbą węzłów w L.")
            return
        mapping_dict = {Lnode: Gnode for Lnode, Gnode in zip(L_nodes_sorted, mapping)}

        # 2. Zbieranie punktów do obliczenia transformacji (Wspólne L i Input)
        src_pts = []
        dst_pts = []

        for l_node in L_nodes_sorted:
            g_node = mapping_dict[l_node]
            # Bierzemy pod uwagę tylko węzły, które mają pozycje w obu grafach
            if l_node in self.L.pos and g_node in input_graph.pos:
                src_pts.append(self.L.pos[l_node])
                dst_pts.append(input_graph.pos[g_node])

        if not src_pts:
            return  # Brak punktów odniesienia

        src_matrix = np.array(src_pts)
        dst_matrix = np.array(dst_pts)

        # 3. Obliczenie macierzy transformacji afinicznej M
        # Równanie: [x_L, y_L, 1] * M = [x_G, y_G]
        ones = np.ones((len(src_matrix), 1))
        A = np.hstack([src_matrix, ones])

        if len(src_pts) >= 3:
            # Metoda najmniejszych kwadratów dla pełnej transformacji (skala, obrót, przesunięcie)
            M, res, rank, s = np.linalg.lstsq(A, dst_matrix, rcond=None)
        else:
            # Fallback dla < 3 punktów: tylko przesunięcie (translacja) na podstawie centroidów
            centroid_src = np.mean(src_matrix, axis=0)
            centroid_dst = np.mean(dst_matrix, axis=0)
            diff = centroid_dst - centroid_src
            M = np.array([
                [1.0, 0.0],
                [0.0, 1.0],
                [diff[0], diff[1]]
            ])

        # 4. Identyfikacja faktycznie nowych wierzchołków w Output

        # a) Ustalmy, co zostało usunięte z Input
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        to_remove_L = L_nodes - R_nodes
        to_remove_G = {mapping_dict[ln] for ln in to_remove_L if ln in mapping_dict}

        # b) Ustalmy, co z Input przetrwało (tło + zachowana część produkcji)
        input_nodes = set(input_graph.nodes())
        preserved_input_nodes = input_nodes - to_remove_G

        # c) Wszystko w Output, co nie jest "przetrwałe", musi być nowe
        output_nodes = set(output_graph.nodes())
        newly_added_ids = output_nodes - preserved_input_nodes

        # Sortujemy po ID, bo apply() przydziela ID rosnąco
        output_new_ids_sorted = sorted(list(newly_added_ids))

        # d) Nowe węzły z definicji produkcji (R - L) - sortujemy, bo apply() dodaje je w tej kolejności
        new_R_nodes_sorted = sorted(list(R_nodes - L_nodes))

        # Weryfikacja
        if len(new_R_nodes_sorted) != len(output_new_ids_sorted):
            print(
                f"[WARN] Liczba nowych wierzchołków w R ({len(new_R_nodes_sorted)}) nie zgadza się z wykrytymi w Output ({len(output_new_ids_sorted)}).")
            return

        # 5. Aplikacja transformacji
        for r_node, out_id in zip(new_R_nodes_sorted, output_new_ids_sorted):
            if r_node in self.R.pos:
                rx, ry = self.R.pos[r_node]

                # Przekształcenie: [rx, ry, 1] * M
                vec = np.array([rx, ry, 1.0])
                new_pos = vec @ M

                # Aktualizacja pozycji w grafie wynikowym
                output_graph.pos[out_id] = tuple(new_pos)

        # output_graph.draw()
        # plt.show()