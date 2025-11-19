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
    input_graph_file = "graphs/initial_graph.csv"
    left_graph_file = "graphs/production_left.csv"
    right_graph_file = "graphs/production_right.csv"
    mapping_file = "graphs/mapping.csv"
else:
    input_graph_file = sys.argv[1]
    left_graph_file = sys.argv[2]
    right_graph_file = sys.argv[3]
    mapping_file = sys.argv[4]


try:
    G = Graph.from_csv(input_graph_file)
    L = Graph.from_csv(left_graph_file)
    R = Graph.from_csv(right_graph_file)
    with open(mapping_file, 'r') as f:
        mapping_line = f.readline().strip()
    mapping_list = [int(x.strip())
                    for x in mapping_line.split(',') if x.strip()]
except Exception as e:
    print(f"Błąd wczytywania plików: {e}")
    sys.exit(1)


production = Production(L, R)
K = production.compute_interface()
result_graph = None

try:
    result_graph = production.apply(G, mapping_list)
    print("Produkcja została zastosowana poprawnie.")
except Exception as e:
    print(f"Produkcja nie może być zastosowana, error: {e}")
    sys.exit(1)


# Wizualizacja grafów
plt.figure(figsize=(5, 4))
plt.title("Graf wejściowy (G)")
G.draw(title="Graf wejściowy (G)")

plt.figure(figsize=(5, 4))
plt.title("Graf lewy produkcji (L)")
L.draw(title="Graf lewy produkcji (L)")

plt.figure(figsize=(5, 4))
plt.title("Graf prawy produkcji (R)")
R.draw(title="Graf prawy produkcji (R)")

plt.figure(figsize=(5, 4))
plt.title("Graf sklejający (K)")
K.draw(title="Graf sklejający (K)")

plt.figure(figsize=(5, 4))
plt.title("Graf wynikowy (G')")
if result_graph:
    result_graph.draw(title="Graf wynikowy (G')")

plt.show()
