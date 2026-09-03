import networkx as nx
import community as community_louvain
from collections import Counter
from graph_mining.build_graph import build_graph

#  Detection

def detect_link_farms():
    G = build_graph()
    G_undirected = G.to_undirected()

    print("[COMMUNITY] Detection des communautes...")
    partition = community_louvain.best_partition(G_undirected)

    sizes = Counter(partition.values())
    print(f"\n[COMMUNITY] {len(sizes)} communautes detectees")

    link_farms = {}

    #  Analyse chaque communauté
  

    for comm_id, size in sizes.items():

        # ignore petites communautés
        if size < 5:
            continue

        nodes = [u for u, c in partition.items() if c == comm_id]
        subgraph = G.subgraph(nodes)

        #  Density
        density = nx.density(subgraph)

        # Internal vs External links
        internal_links = subgraph.number_of_edges()

        external_links = 0
        for node in nodes:
            for neighbor in G.successors(node):
                if neighbor not in nodes:
                    external_links += 1

        # Ratio
        ratio = internal_links / (external_links + 1)

        #  Decision
     

        if density > 0.3 and ratio > 2:
            link_farms[comm_id] = {
                "size": size,
                "density": round(density, 3),
                "ratio": round(ratio, 2),
                "nodes": nodes
            }

   
    #  Results
   

    print(f"\n[LINK FARMS] {len(link_farms)} suspectes :")

    for comm_id, data in sorted(link_farms.items(),
                               key=lambda x: x[1]["size"],
                               reverse=True):

        print(f"\n  Communaute {comm_id}")
        print(f"    - Taille   : {data['size']}")
        print(f"    - Density  : {data['density']}")
        print(f"    - Ratio    : {data['ratio']}")

        for m in data["nodes"][:5]:
            print(f"    - {m}")

    return partition, link_farms