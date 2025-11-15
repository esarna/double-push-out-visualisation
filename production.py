from graph import Graph  # import klasy Graph z modułu graph.py

class Production:
    """Reprezentuje produkcję grafową (regułę transformacji) z grafem lewym (L) i prawym (R)."""
    def __init__(self, left: Graph, right: Graph):
        self.L = left
        self.R = right

    def compute_interface(self) -> Graph:
        """
        Oblicza graf sklejający K, czyli część wspólną L i R.
        Węzły K to węzły występujące zarówno w L, jak i w R.
        Krawędzie K to krawędzie występujące zarówno w L, jak i w R między węzłami, które są w K.
        """
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        K_nodes = L_nodes.intersection(R_nodes)
        L_edges = set(self.L.edges())
        R_edges = set(self.R.edges())
        # Krawędzie wspólne (zarówno w L, jak i R) ograniczone do węzłów K
        K_edges = [(u, v) for (u, v) in L_edges.intersection(R_edges) if u in K_nodes and v in K_nodes]
        K_graph = Graph(vertices=list(K_nodes), edges=K_edges)
        # Przypisz etykiety z L (zakładamy, że jeśli węzeł jest wspólny, etykiety L i R są zgodne)
        for node in K_graph.nodes():
            label = self.L.get_label(node)
            if label is not None:
                K_graph.set_label(node, label)
        return K_graph

    def apply(self, host: Graph, mapping: list[int]) -> Graph:
        """
        Próbuje zastosować produkcję do grafu hosta (G) według zadanego odwzorowania.
        Parametr 'mapping' to lista wierzchołków grafu hosta, odpowiadająca kolejno wierzchołkom L
        (w porządku rosnącym ich identyfikatorów w grafie L).
        Zwraca nowy graf będący wynikiem transformacji,
        lub rzuca wyjątkiem z opisem błędu jeśli produkcji nie można zastosować.
        """
        G = host
        # Utwórz kopię grafu hosta, aby nie modyfikować oryginału bezpośrednio
        output = Graph(vertices=G.nodes(), edges=G.edges())
        # Skopiuj etykiety wierzchołków
        for node in G.nodes():
            lbl = G.get_label(node)
            if lbl is not None:
                output.set_label(node, lbl)
        # Przygotuj słownik odwzorowania L->G
        L_nodes_sorted = sorted(self.L.nodes())
        if len(mapping) != len(L_nodes_sorted):
            raise Exception("Niepoprawna liczba wierzchołków w odwzorowaniu dla grafu L.")
        mapping_dict = {Lnode: Gnode for Lnode, Gnode in zip(L_nodes_sorted, mapping)}
        # Sprawdzenie warunku identyfikacji (odwzorowanie musi być injektywne)
        if len(set(mapping_dict.values())) != len(mapping_dict):
            raise Exception("Odwzorowanie nie jest injektywne – różne węzły L odwzorowano na ten sam węzeł grafu G.")
        # Sprawdzenie istnienia wszystkich krawędzi L w grafie hosta (dopasowanie L -> G)
        for (u, v) in self.L.edges():
            uG = mapping_dict[u]
            vG = mapping_dict[v]
            if not output.has_edge(uG, vG):
                raise Exception(f"Brak wymaganej krawędzi ({u}->{v}) z L w grafie początkowym (oczekiwano {uG}->{vG}).")
        # Określ zbiory wierzchołków usuwanych i zachowywanych
        L_nodes = set(self.L.nodes())
        R_nodes = set(self.R.nodes())
        to_remove_L = L_nodes - R_nodes     # węzły, które są w L, ale nie w R (zostaną usunięte)
        to_remove_G = {mapping_dict[Ln] for Ln in to_remove_L}  # odpowiadające im węzły w G
        # **Sprawdzenie warunku wiszących krawędzi** – żadna krawędź spoza dopasowania L nie może łączyć usuwanego węzła z pozostającym węzłem
        for gnode in to_remove_G:
            # Dla każdej krawędzi wychodzącej z gnode
            for succ in list(G.nx_graph.successors(gnode)):
                if succ not in to_remove_G:
                    # succ to węzeł, który pozostaje (nie jest usuwany)
                    # Jeśli succ nie jest obrazem żadnego węzła z L (czyli jest spoza dopasowania), to wykryliśmy krawędź wiszącą
                    inv_map = {Gv: Lv for Lv, Gv in mapping_dict.items()}
                    if succ not in inv_map:
                        raise Exception(f"Naruszenie warunku wiszącej krawędzi: wierzchołek {gnode} (do usunięcia) ma krawędź do {succ}, który nie jest objęty dopasowaniem.")
                    else:
                        # succ jest obrazem jakiegoś węzła z L (czyli succ odpowiada węzłowi zachowanemu z L)
                        Lnode_removed = inv_map[gnode]   # węzeł L, który usuwamy
                        Lnode_other = inv_map[succ]      # węzeł L odpowiadający succ
                        # Sprawdź, czy L zawierał taką krawędź (usuwany->zachowany). Jeśli nie, to mamy krawędź wiszącą.
                        if not self.L.has_edge(Lnode_removed, Lnode_other):
                            raise Exception(f"Naruszenie warunku wiszącej krawędzi: krawędź {Lnode_removed}->{Lnode_other} łączy usuwany i zachowany węzeł w G, ale nie istnieje w L.")
            # Dla każdej krawędzi wchodzącej do gnode
            for pred in list(G.nx_graph.predecessors(gnode)):
                if pred not in to_remove_G:
                    inv_map = {Gv: Lv for Lv, Gv in mapping_dict.items()}
                    if pred not in inv_map:
                        raise Exception(f"Naruszenie warunku wiszącej krawędzi: wierzchołek {gnode} (do usunięcia) ma krawędź od {pred}, który nie jest objęty dopasowaniem.")
                    else:
                        Lnode_removed = inv_map[gnode]
                        Lnode_other = inv_map[pred]
                        if not self.L.has_edge(Lnode_other, Lnode_removed):
                            raise Exception(f"Naruszenie warunku wiszącej krawędzi: krawędź {Lnode_other}->{Lnode_removed} łączy zachowany i usuwany węzeł w G, ale nie istnieje w L.")
        # Jeśli warunki są spełnione – wykonaj transformację
        # 1. Usuń z grafu wynikowego węzły (i ich krawędzie) przeznaczone do usunięcia
        for node in to_remove_G:
            output.remove_node(node)
        # 2. Usuń krawędzie, które istniały między zachowanymi węzłami w L, ale nie ma ich w R (czyli mają być usunięte)
        L_edges = set(self.L.edges())
        R_edges = set(self.R.edges())
        preserved_L = L_nodes.intersection(R_nodes)  # węzły zachowane
        for (u, v) in L_edges:
            if u in preserved_L and v in preserved_L and (u, v) not in R_edges:
                # jeśli krawędź łączy dwa zachowane węzły, a nie jest obecna w R, usuń ją
                uG, vG = mapping_dict[u], mapping_dict[v]
                if output.has_edge(uG, vG):
                    output.remove_edge(uG, vG)
        # 3. Dodaj nowe węzły z R (takie, których nie było w L)
        new_R_nodes = R_nodes - L_nodes
        new_node_map = {}  # mapowanie: węzeł R (nowy) -> nowy węzeł w output
        # Wyznacz początkowy nowy identyfikator (aby nie kolidował z istniejącymi w output)
        next_id = max(output.nodes())+1 if output.nodes() else 1
        for Rnode in sorted(new_R_nodes):
            new_id = next_id
            next_id += 1
            output.add_node(new_id)
            new_node_map[Rnode] = new_id
            # Skopiuj etykietę nowego węzła (jeśli zdefiniowana w R)
            lbl = self.R.get_label(Rnode)
            if lbl is not None:
                output.set_label(new_id, lbl)
        # 4. Dodaj nowe krawędzie z R (pomiędzy odpowiednimi węzłami w output)
        for (u, v) in self.R.edges():
            # Ustal odpowiedniki węzłów u, v w grafie output:
            u_out = mapping_dict.get(u) if u in L_nodes else new_node_map.get(u)
            v_out = mapping_dict.get(v) if v in L_nodes else new_node_map.get(v)
            if u_out is None or v_out is None:
                continue  # pomiń, jeśli coś nie zostało zmapowane (nie powinno się zdarzyć)
            if output.has_edge(u_out, v_out):
                continue  # jeśli krawędź już istnieje (np. zachowana), nie dodawaj ponownie
            output.add_edge(u_out, v_out)
        # Zwróć przetransformowany graf
        return output
