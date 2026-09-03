from elasticsearch import Elasticsearch
from config import ELASTIC_HOST

es = Elasticsearch(ELASTIC_HOST)

def index_page(page: dict):
    """Indexe une page pour la recherche full-text"""
    es.index(
        index="cyberintel_pages",
        id=page["url"],
        document={
            "url":   page["url"],
            "title": page.get("title", ""),
            "text":  page.get("text",  "")[:5000],  # max 5000 chars
        }
    )
    print(f"[ELASTIC] Indexe : {page['url']}")

def search_keyword(keyword: str):
    """Recherche un mot-cle dans toutes les pages"""
    result = es.search(
        index="cyberintel_pages",
        query={"match": {"text": keyword}}
    )
    return [h["_source"] for h in result["hits"]["hits"]]