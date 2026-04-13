import matplotlib.pyplot as plt
import networkx as nx
from z3 import *


def optimize_graph(graph, atoms):
    """
    Optimize the given NetworkX graph using linear programming.

    Parameters:
    - graph: NetworkX graph object
    - atoms: Integer for the number of nodes to select

    Returns:
    - A dictionary with node selection status and the optimization status.
    """
    # Define the problem
    solver = Optimize()
    # Variables
    node_vars = {node: Bool(f"node_{node}") for node in graph.nodes()}

    # Calculate contributions
    contributions = []
    for node in graph.nodes():
        # Use sum of neighbor variables
        f_node = sum(If(node_vars[neigh], 1, 0) for neigh in graph.neighbors(node))
        contributions.append(If(node_vars[node], graph.degree(node) - f_node, 0))

    # Objective function
    objective = sum(contributions)
    solver.minimize(objective)

    # Constraint for the number of selected nodes
    solver.add(sum(If(node_vars[node], 1, 0) for node in graph.nodes()) == atoms)

    print("Solving...")
    if solver.check() == sat:
        model = solver.model()
        print(f"Energy: {model.eval(objective)}")
        results = {node: model[node_vars[node]] for node in graph.nodes()}
        return {
            "status": "SAT",
            "selection": results
        }
    else:
        return {
            "status": "UNSAT",
            "selection": {}
        }


def main():
    atoms = 6  # Adjust as needed
    # Create a sample graph
    G = nx.grid_2d_graph(atoms, atoms - 1, False)

    # Optimize the graph
    result = optimize_graph(G, atoms)

    nodes = []
    print("Optimization Status:", result['status'])
    for node, value in result['selection'].items():
        if value:
            nodes.append(node)
            print(f"{node}: {value}")

    nx.draw(G, pos=ID(), edge_color="white")
    nx.draw(G.subgraph(nodes), pos=ID(), node_color="orange", edge_color="orange")
    plt.show()


class ID:
    def __getitem__(self, x):
        return x


# Example usage
if __name__ == "__main__":
    main()
