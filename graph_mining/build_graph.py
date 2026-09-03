import networkx as nx
from urllib.parse import urlparse
from database.mongo_connector import get_all_pages
from database.neo4j_connector import create_site_link

#  Helper


def get_domain(url):
    domain = urlparse(url).netloc.lower()

   
    if domain.startswith("www."):
        domain = domain.replace("www.", "")

    return domain

#  Build Graph


def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    pages = get_all_pages()

    print(f"[GRAPH] Construction du graphe avec {len(pages)} pages...")

    for page in pages:
        src_domain = get_domain(page["url"])

        for link in page.get("links", []):
            if not link.startswith("http"):
                continue

            tgt_domain = get_domain(link)

            
            if src_domain == tgt_domain:
                continue

            #  Weighted edges
            if G.has_edge(src_domain, tgt_domain):
                G[src_domain][tgt_domain]["weight"] += 1
            else:
                G.add_edge(src_domain, tgt_domain, weight=1)

   
    #  Neo4j 
   

    print("[NEO4J] Export des liens...")

    for src, tgt, data in G.edges(data=True):
        weight = data.get("weight", 1)
        create_site_link(src, tgt, weight)

    print(f"[GRAPH] {G.number_of_nodes()} noeuds, {G.number_of_edges()} liens")

    return G