import sys
import matplotlib.pyplot as plt
from graph import Graph
from production import Production

# Sprawdzenie argumentów wiersza poleceń (zakładamy 4 argumenty: pliki CSV)
if len(sys.argv) < 5:
    print("Użycie: python main.py <plik_graf_wejściowy> <plik_L> <plik_R> <plik_odwzorowania>")
    sys.exit(1)

input_graph_file = sys.argv[1]
left_graph_file = sys.argv[2]
right_graph_file = sys.argv[3]
mapping_file = sys.argv[4]

# Wczytaj graf początkowy oraz produkcję (L i R)
try:
    G = Graph.from_csv(input_graph_file)
    L = Graph.from_csv(left_graph_file)
    R = Graph.from_csv(right_graph_file)
except Exception as e:
    print(f"Błąd wczytywania plików: {e}")
    sys.exit(1)

# Utwórz obiekt produkcji
production = Production(L, R)

# Wczytaj odwzorowanie wierzchołków (jako listę) z pliku
try:
    with open(mapping_file, 'r') as f:
        mapping_line = f.readline().strip()
    mapping_list = [int(x.strip()) for x in mapping_line.split(',') if x.strip()]
except Exception as e:
    print(f"Błąd wczytywania pliku odwzorowania: {e}")
    sys.exit(1)

# Próbuj zastosować produkcję do grafu wejściowego
result_graph = None
try:
    result_graph = production.apply(G, mapping_list)
    print("Produkcja została zastosowana poprawnie.")
except Exception as e:
    print(f"Produkcja nie może być zastosowana: {e}")
    sys.exit(1)

# Oblicz graf sklejający K (część wspólna L i R) do celów wizualizacji
K = production.compute_interface()

# Wizualizacja grafów: graf początkowy, produkcja (L i R), graf sklejający, graf wynikowy
plt.figure(figsize=(5,4))
plt.title("Graf wejściowy (G)")
G.draw(title="Graf wejściowy (G)")

plt.figure(figsize=(5,4))
plt.title("Graf lewy produkcji (L)")
L.draw(title="Graf lewy produkcji (L)")

plt.figure(figsize=(5,4))
plt.title("Graf prawy produkcji (R)")
R.draw(title="Graf prawy produkcji (R)")

plt.figure(figsize=(5,4))
plt.title("Graf sklejający (K)")
K.draw(title="Graf sklejający (K)")

plt.figure(figsize=(5,4))
plt.title("Graf wynikowy (G')")
if result_graph:
    result_graph.draw(title="Graf wynikowy (G')")

plt.show()
