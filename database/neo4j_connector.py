from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASS)
)

# ==============================
# 🔗 Create Link (WITH WEIGHT)
# ==============================

def create_site_link(source_url: str, target_url: str, weight: int = 1):
    """Cree les noeuds sites et la relation avec poids"""
    with driver.session() as session:
        session.run("""
            MERGE (s:Site {url: $src})
            MERGE (t:Site {url: $tgt})
            MERGE (s)-[r:LIENS_VERS]->(t)
            SET r.weight = coalesce(r.weight, 0) + $weight
        """, src=source_url, tgt=target_url, weight=weight)

# ==============================
# 📊 Get Sites
# ==============================

def get_all_sites():
    """Recupere tous les sites du graphe"""
    with driver.session() as session:
        result = session.run("MATCH (s:Site) RETURN s.url AS url")
        return [r["url"] for r in result]

# ==============================
# 🧹 Optional: Clear Graph
# ==============================

def clear_graph():
    """Supprime tout le graphe (debug)"""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

# ==============================
# 🔌 Close
# ==============================

def close():
    driver.close()