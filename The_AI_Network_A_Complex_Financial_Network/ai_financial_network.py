import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def simulate_cascade(graph, initial_failures, threshold=0.35):
    failed = set(initial_failures)
    queue = list(initial_failures)

    while queue:
        current = queue.pop(0)
        for neighbor in graph.successors(current):
            if neighbor in failed:
                continue

            lost_exposure = graph[current][neighbor]["weight"]
            total_incoming = sum(
                graph[u][neighbor]["weight"]
                for u in graph.predecessors(neighbor)
            )

            if total_incoming > 0 and (lost_exposure / total_incoming) > threshold:
                failed.add(neighbor)
                queue.append(neighbor)

    return failed

# -------------------------------
# Financial relationships (USD billions)
# -------------------------------
def initalize_financial_network():
    edges = [
        # -------- Equity investments --------
        ("Microsoft", "OpenAI", 13, "equity"),
        ("SoftBank", "OpenAI", 40, "equity"),
        ("Nvidia", "OpenAI", 10, "equity"),
        ("Amazon", "Anthropic", 8, "equity"),
        ("Google", "Anthropic", 3, "equity"),
        ("Nvidia", "Anthropic", 10, "equity"),
        ("Valor Equity", "xAI", 5, "equity"),
        ("Qatar Investment Authority", "xAI", 2, "equity"),
        ("Thrive Capital", "Databricks", 10, "equity"),
        ("Andreessen Horowitz", "Databricks", 5, "equity"),

        # -------- Debt / project finance --------
        ("Bank Syndicate", "OpenAI", 15, "debt"),
        ("Bank Syndicate", "CoreWeave", 7, "debt"),
        ("Bank Syndicate", "Hyperscaler Data Centers", 20, "debt"),

        # -------- Contractual dependencies --------
        ("OpenAI", "Microsoft", 20, "contract"),
        ("Anthropic", "Amazon", 15, "contract"),
        ("xAI", "Nvidia", 10, "contract"),
        ("Databricks", "Amazon", 5, "contract"),
        ("CoreWeave", "Nvidia", 8, "contract"),
    ]

    g = nx.DiGraph()

    for source, target, value, relation in edges:
        g.add_edge(
            source,
            target,
            weight=value,
            relationship=relation
        )

    # Eigenvector centrality captures systemic importance
    centrality = nx.eigenvector_centrality(g, weight="weight", max_iter=1000)

    # Total financial exposure (incoming + outgoing)
    exposure = {}
    for node in g.nodes():
        incoming = sum(g[u][node]["weight"] for u in g.predecessors(node))
        outgoing = sum(g[node][v]["weight"] for v in g.successors(node))
        exposure[node] = incoming + outgoing

    df_metrics = pd.DataFrame({
        "Eigenvector Centrality": centrality,
        "Total Exposure ($B)": exposure
    }).sort_values("Eigenvector Centrality", ascending=False)

    print(df_metrics)

    plt.figure(figsize=(16, 14))

    # Use spring layout with improved spacing to prevent node overlap
    pos = nx.spring_layout(g, k=2.5, iterations=50, seed=42)

    # Node sizes scale with centrality
    node_sizes = [centrality[n] * 600 for n in g.nodes()]

    # Color edges by relationship type
    edge_colors = []
    for u, v in g.edges():
        rel = g[u][v]["relationship"]
        if rel == "equity":
            edge_colors.append("tab:blue")
        elif rel == "debt":
            edge_colors.append("tab:red")
        else:
            edge_colors.append("tab:green")

    nx.draw(
        g,
        pos,
        with_labels=True,
        node_size=node_sizes,
        edge_color=edge_colors,
        node_color="lightgray",
        font_size=9,
        arrows=True
    )

    edge_labels = {
        (u, v): f'{g[u][v]["weight"]}B'
        for u, v in g.edges()
    }
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=8)

    plt.title(
        "AI Financial Network\nBlue = Equity | Red = Debt | Green = Contracts",
        fontsize=14
    )
    plt.show()
    return g

if __name__ == "__main__":
    
    G = initalize_financial_network()
    #initial_failures = ["OpenAI"]
    #failed_nodes = simulate_cascade(G, initial_failures, threshold=0.35)
    #print("Nodes failed in cascade:", failed_nodes)