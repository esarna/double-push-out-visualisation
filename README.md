# Double Push Out (DPO) Graph Transformation Visualization

This project implements and visualizes Double Push Out (DPO) graph transformations using Python, `networkx`, and `matplotlib`. It allows you to define graph productions and apply them to input graphs, visualizing the results.

## Features

- **Graph Representation**: Load and manipulate directed graphs with labeled vertices and edges.
- **DPO Transformation**: Apply graph productions defined by a Left-Hand Side (LHS) and Right-Hand Side (RHS) graph.
- **Visualization**: Visual representation of input graphs, productions, and the resulting graph after transformation.
- **CSV Support**: Load graph structures and mappings from CSV files.

## Prerequisites

- Python 3
- `networkx`
- `matplotlib`
- `jupyter` (optional, for notebooks)

## Installation & Setup

Install the required packages manually:

```bash
pip install networkx matplotlib
```

## Usage

### Command Line Interface

You can run the main script with paths to your graph files:

```bash
python main.py <input_graph> <left_production> <right_production> <mapping>
```

Example:

```bash
python main.py graphs/graphs_csv/initial_graph.csv graphs/graphs_csv/production_left.csv graphs/graphs_csv/production_right.csv graphs/mapping.csv
```

If no arguments are provided, the script uses default paths defined in `main.py`.

### Programmatic Usage

See `test.py` for an example of how to use the library in your own scripts:

```python
import matplotlib.pyplot as plt
import src as dp

# Load graphs
G = dp.Graph.from_csv("graphs/graphs_csv/initial2_graph.csv")
L = dp.Graph.from_csv("graphs/graphs_csv/production_left.csv")
R = dp.Graph.from_csv("graphs/graphs_csv/production_right.csv", pos_like=L.pos)

# Load mapping
mapping = [1, 2, 3] # Example mapping

# Apply production
production = dp.Production(L, R)
result_graph = production.apply(G, mapping, transform_positions=True)

# Visualize
production.draw()
plt.show()

result_graph.draw()
plt.show()
```

## Project Structure

- `src/`: Contains the core logic (`graph.py`, `production.py`).
- `graphs/`: Contains example graph data in CSV format.
- `main.py`: Main entry point for the CLI.
- `test.py`: Example usage script.
- `shell.nix`: Nix shell configuration.
