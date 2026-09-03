import json
from database.mongo_connector import db

# Export raw_pages
raw_pages = list(db.raw_pages.find({}, {"_id": 0}))

with open("raw_pages.json", "w", encoding="utf-8") as f:
    json.dump(raw_pages, f, ensure_ascii=False, indent=2, default=str)

print("[EXPORT] raw_pages.json OK")

#  Export graph_metrics

graph_metrics = list(db.graph_metrics.find({}, {"_id": 0}))

with open("graph_metrics.json", "w", encoding="utf-8") as f:
    json.dump(graph_metrics, f, ensure_ascii=False, indent=2, default=str)

print("[EXPORT] graph_metrics.json OK")


# Export bot_scores
bot_scores = list(db.bot_scores.find({}, {"_id": 0}))

with open("bot_scores.json", "w", encoding="utf-8") as f:
    json.dump(bot_scores, f, ensure_ascii=False, indent=2, default=str)

print("[EXPORT] bot_scores.json OK")