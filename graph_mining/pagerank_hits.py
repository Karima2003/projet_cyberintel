import networkx as nx
from graph_mining.build_graph import build_graph
from database.mongo_connector import save_graph_metrics


def compute_metrics(G=None):
    """Calcule PageRank et HITS  ET SAUVGARDER LES RESULTATS  """

    # Build graph 
   
    if G is None:
        G = build_graph()

    print("[METRICS] Calcul PageRank (weighted)...")

    try:
        pr = nx.pagerank(G, alpha=0.85, weight="weight")
    except Exception as e:
        print(f"[ERROR] PageRank failed: {e}")
        pr = {}

    print("[METRICS] Calcul HITS...")

    try:
        hubs, authorities = nx.hits(G, max_iter=100, normalized=True)
    except Exception as e:
        print(f"[WARNING] HITS failed: {e}")
        hubs, authorities = {}, {}

 
    # Save to MongoDB
   
    print("[MONGO] Sauvegarde des métriques...")

    for node in G.nodes():
        data = {
            "domain": node,
            "pagerank": round(pr.get(node, 0), 6),
            "hub": round(hubs.get(node, 0), 6),
            "authority": round(authorities.get(node, 0), 6),
        }

        try:
            save_graph_metrics(data)
        except Exception as e:
            print(f"[ERROR] Mongo save failed for {node}: {e}")

 
    #  Top 10 PageRank


    top10 = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]

    print("\n[TOP 10 PageRank]")
    for domain, score in top10:
        print(f"  {score:.4f} — {domain}")

    return pr, hubs, authorities