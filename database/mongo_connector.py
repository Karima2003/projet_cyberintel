from pymongo import MongoClient
from config import MONGO_URI
import datetime

client = MongoClient(MONGO_URI)
db = client["cyberintel"]

# ==============================
# 📄 Pages (RAW DATA)
# ==============================

def save_page(data: dict):
    """Sauvegarde une page scrapee dans MongoDB"""
    data["saved_at"] = datetime.datetime.now()

    db.raw_pages.update_one(
        {"url": data["url"]},   # 👈 page = URL
        {"$set": data},
        upsert=True
    )

    print(f"[MONGO] Sauvegarde : {data['url']}")


def get_all_pages():
    """Recupere toutes les pages stockees"""
    return list(db.raw_pages.find({}, {"_id": 0}))


# ==============================
# 🤖 Bots
# ==============================

def save_bot_score(data: dict):
    """Sauvegarde les scores de detection de bots"""
    db.bot_scores.update_one(
        {"ip": data["ip"]},
        {"$set": data},
        upsert=True
    )


# ==============================
# 📊 Graph Metrics (DOMAIN LEVEL)
# ==============================

def save_graph_metrics(data: dict):
    """Sauvegarde PageRank et HITS (par domaine)"""

    if "domain" not in data:
        raise ValueError("Missing 'domain' field in graph metrics")

    db.graph_metrics.update_one(
        {"domain": data["domain"]},   # 👈 مهم: DOMAIN مشي URL
        {"$set": data},
        upsert=True
    )