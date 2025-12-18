import sys
import matplotlib.pyplot as plt
from src.graph import Graph
from src.production import Production

"""
PRZYKŁADOWE UŻYCIE: 

     python main.py graphs/initial_graph.csv graphs/production_left.csv graphs/production_right.csv graphs/mapping.csv
     
"""
# Wczytanie plików z argumentów wywołania lub default
if len(sys.argv) < 5:
    input_graph_file = "graphs/graphs_obj/initial_graph.obj"
    left_graph_file = "graphs/graphs_obj/production_left.obj"
    right_graph_file = "graphs/graphs_obj/production_right.obj"
    mapping_file = "graphs/mapping.csv"

    # input_graph_file = "graphs/graphs_obj/initial2_graph.obj"
    # left_graph_file = "graphs/graphs_obj/production_left2.obj"
    # right_graph_file = "graphs/graphs_obj/production_right2.obj"
    # mapping_file = "graphs/mapping.csv"

    # nie ma krawędzi
    # input_graph_file = "graphs/graphs_obj/initial3_graph.obj"
    # left_graph_file = "graphs/graphs_obj/production_left2.obj"
    # right_graph_file = "graphs/graphs_obj/production_right2.obj"
    # mapping_file = "graphs/mapping.csv"

    # edge w drugą stronę
    # input_graph_file = "graphs/graphs_obj/initial4_graph.obj"
    # left_graph_file = "graphs/graphs_obj/production_left2.obj"
    # right_graph_file = "graphs/graphs_obj/production_right2.obj"
    # mapping_file = "graphs/mapping.csv"
else:
    input_graph_file = sys.argv[1]
    left_graph_file = sys.argv[2]
    right_graph_file = sys.argv[3]
    mapping_file = sys.argv[4]


try:
    G = Graph.from_csv(input_graph_file)
    L = Graph.from_csv(left_graph_file)
    R = Graph.from_csv(right_graph_file, pos_like=L.pos)
    with open(mapping_file, 'r') as f:
        mapping_line = f.readline().strip()
    mapping_list = [int(x.strip())
                    for x in mapping_line.split(',') if x.strip()]
except Exception as e:
    try:
        G = Graph.from_obj(input_graph_file)
        L = Graph.from_obj(left_graph_file)
        R = Graph.from_obj(right_graph_file, pos_like=L.pos)
        with open(mapping_file, 'r') as f:
            mapping_line = f.readline().strip()
        mapping_list = [int(x.strip())
                        for x in mapping_line.split(',') if x.strip()]
    except Exception as e:
        print(f"Błąd wczytywania plików: {e}")
        sys.exit(1)

# wyrzucanie indeksów edgy (na razie)
G.edge_idx = {}
L.edge_idx = {}
R.edge_idx = {}

production = Production(L, R)
production.draw()

plt.figure(figsize=(5, 4))
plt.title("Graf wejściowy (G)")
G.draw()
plt.show()

try:
    result_graph = production.apply(G, mapping_list, transform_positions=True)
    print("Produkcja została zastosowana poprawnie.")

    if result_graph:
        plt.figure(figsize=(5, 4))
        plt.title("Graf wynikowy (G')")
        result_graph.draw()
        plt.show()

except Exception as e:
    print(f"Produkcja nie może być zastosowana, error: {e}")
    sys.exit(1)



